"""
Self-annealing loop — captures errors and resolutions into directive/skill error logs.

This makes the system smarter over time:
  - When a script fails, the error is recorded with context
  - When the fix is applied, the resolution is appended
  - The next AI session reads these logs to avoid repeating the mistake

This IS the learning layer described in CLAUDE.md's "Self-Annealing Loop."

Usage:
    from execution.shared.anneal import AnnealLogger

    # At end of a script's error handler:
    AnnealLogger.record_failure(
        script="execution/create_qbo_invoice.py",
        directive="directives/sales-to-qbo.md",
        error="Token refresh failed with 401",
        context={"realm_id": realm_id, "sandbox": True},
    )

    # When a fix is confirmed:
    AnnealLogger.record_resolution(
        script="execution/create_qbo_invoice.py",
        resolution="Refresh token expires every 100 days; regenerate via /oauth2/playground",
        learning="Set calendar reminder to refresh QBO token before expiry",
    )
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from execution.shared.logger import get_logger

_log = get_logger("shared.anneal")

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_ANNEAL_LOG = _PROJECT_ROOT / "logs" / "anneal.log"
_ANNEAL_LOG.parent.mkdir(exist_ok=True)


class AnnealLogger:
    """Records failures and resolutions to the persistent anneal log."""

    @staticmethod
    def record_failure(
        *,
        script: str,
        error: str,
        directive: str = "",
        context: dict[str, Any] | None = None,
    ) -> None:
        """
        Append a structured failure record to logs/anneal.log.
        Called automatically by @safe_execute for CypressBaseError subtypes.
        """
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "type": "FAILURE",
            "script": script,
            "directive": directive,
            "error": error,
            "context": context or {},
            "resolved": False,
            "resolution": None,
            "learning": None,
        }
        _append(entry)
        _log.info("Anneal failure recorded", extra={"script": script})

        # Also append to directive's LEARNINGS section if path is given
        if directive:
            _append_to_directive(directive, entry)

    @staticmethod
    def record_resolution(
        *,
        script: str,
        resolution: str,
        learning: str = "",
    ) -> None:
        """
        Mark the most recent unresolved failure for this script as resolved.
        Call this after confirming a fix works.
        """
        # Read existing log, find last unresolved for this script, update it
        lines = _read_lines()
        updated = False
        new_lines = []

        for line in reversed(lines):
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                new_lines.insert(0, line)
                continue

            if (
                not updated
                and entry.get("script") == script
                and entry.get("type") == "FAILURE"
                and not entry.get("resolved")
            ):
                entry["resolved"] = True
                entry["resolution"] = resolution
                entry["learning"] = learning
                entry["resolved_ts"] = datetime.now(timezone.utc).isoformat()
                updated = True

            new_lines.insert(0, json.dumps(entry))

        _write_lines(new_lines)

        if updated:
            _log.info("Anneal resolution recorded", extra={"script": script})
        else:
            _log.warning("No unresolved failure found to mark resolved",
                         extra={"script": script})

    @staticmethod
    def get_known_issues(script: str = "") -> list[dict]:
        """
        Return unresolved failures. Pass script to filter, or omit for all.
        Used by /post-mortem command and /health-check.
        """
        lines = _read_lines()
        issues = []
        for line in lines:
            try:
                entry = json.loads(line)
                if entry.get("type") == "FAILURE" and not entry.get("resolved"):
                    if not script or entry.get("script") == script:
                        issues.append(entry)
            except json.JSONDecodeError:
                continue
        return issues

    @staticmethod
    def get_learnings(limit: int = 20) -> list[dict]:
        """Return the most recent resolved entries as learnings to brief an AI session."""
        lines = _read_lines()
        resolved = [
            json.loads(l) for l in lines
            if _safe_parse(l).get("resolved")
        ]
        return resolved[-limit:]


# ─── File I/O helpers ─────────────────────────────────────────────────────────

def _append(entry: dict) -> None:
    with open(_ANNEAL_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def _read_lines() -> list[str]:
    if not _ANNEAL_LOG.exists():
        return []
    with open(_ANNEAL_LOG, encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip()]


def _write_lines(lines: list[str]) -> None:
    with open(_ANNEAL_LOG, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def _safe_parse(line: str) -> dict:
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return {}


def _append_to_directive(directive_path: str, entry: dict) -> None:
    """
    Append error info to the Error Handling table of a directive file.
    Creates the LEARNINGS section if it doesn't exist.
    """
    full_path = _PROJECT_ROOT / directive_path
    if not full_path.exists():
        return

    ts = entry["ts"][:10]  # date only
    error = entry["error"]
    append_text = (
        f"\n<!-- ANNEAL:{ts} -->\n"
        f"| `{ts}` | {error} | Auto-logged by anneal system | Pending resolution |\n"
    )

    try:
        content = full_path.read_text(encoding="utf-8")
        if "## Known Issues" not in content:
            content += (
                "\n\n## Known Issues\n"
                "| Date | Error | Context | Resolution |\n"
                "|------|-------|---------|------------|\n"
            )
        full_path.write_text(content + append_text, encoding="utf-8")
    except Exception as exc:
        _log.warning("Could not update directive with anneal entry",
                     extra={"directive": directive_path, "error": str(exc)})
