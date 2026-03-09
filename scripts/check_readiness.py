#!/usr/bin/env python3
"""
check_readiness.py
Scan every execution/ script for SCRIPT_STATUS headers and report which ones
are production-ready versus stubs, partials, or needs-config.

Usage:
    python scripts/check_readiness.py              # full table
    python scripts/check_readiness.py --json       # JSON output for server.js
    python scripts/check_readiness.py --fail-on-placeholder   # non-zero exit if any PLACEHOLDER

Exit codes:
    0 - all scripts READY (or no flag set)
    1 - at least one PLACEHOLDER remains (when --fail-on-placeholder)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
EXECUTION_DIR = REPO_ROOT / "execution"

STATUS_PATTERN = re.compile(r"#\s*SCRIPT_STATUS\s*:\s*(\S+)", re.IGNORECASE)
BLOCKS_PATTERN = re.compile(r"#\s*BLOCKS\s*:\s*(.+)", re.IGNORECASE)
REASON_PATTERN = re.compile(r"#\s*REASON\s*:\s*(.+)", re.IGNORECASE)
OWNER_PATTERN  = re.compile(r"#\s*OWNER\s*:\s*(.+)", re.IGNORECASE)

STATUS_ORDER = {
    "PLACEHOLDER":   0,
    "NEEDS_CONFIG":  1,
    "PARTIAL":       2,
    "READY":         3,
    "UNKNOWN":       4,
}

STATUS_COLOUR = {
    "PLACEHOLDER":  "\033[91m",   # red
    "NEEDS_CONFIG": "\033[93m",   # yellow
    "PARTIAL":      "\033[94m",   # blue
    "READY":        "\033[92m",   # green
    "UNKNOWN":      "\033[90m",   # grey
}
RESET = "\033[0m"
BOLD  = "\033[1m"


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _extract(pattern: re.Pattern, text: str) -> str:
    m = pattern.search(text)
    return m.group(1).strip() if m else ""


def _parse_header(path: Path) -> dict:
    """Read the first 20 lines of a script and extract status metadata."""
    try:
        header = "".join(path.read_text(encoding="utf-8").splitlines(keepends=True)[:25])
    except Exception:
        header = ""

    status = _extract(STATUS_PATTERN, header).upper() or "UNKNOWN"
    blocks  = _extract(BLOCKS_PATTERN, header)
    reason  = _extract(REASON_PATTERN, header)
    owner   = _extract(OWNER_PATTERN,  header)

    return {
        "script":  path.name,
        "status":  status,
        "reason":  reason,
        "blocks":  blocks,
        "owner":   owner,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def collect() -> list[dict]:
    scripts = sorted(EXECUTION_DIR.glob("*.py"))
    # Exclude shared/ sub-package entry points
    scripts = [s for s in scripts if s.parent == EXECUTION_DIR]
    return [_parse_header(s) for s in scripts]


def print_table(results: list[dict], colour: bool = True) -> None:
    by_status: dict[str, list[dict]] = {}
    for r in results:
        by_status.setdefault(r["status"], []).append(r)

    groups = sorted(by_status.keys(), key=lambda s: STATUS_ORDER.get(s, 99))

    col = lambda s, text: (STATUS_COLOUR.get(s, "") + text + RESET) if colour else text

    print(f"\n{BOLD}5 Cypress — Script Readiness Report{RESET}")
    print(f"Scanned {len(results)} scripts in {EXECUTION_DIR.relative_to(REPO_ROOT)}\n")

    totals: dict[str, int] = {}

    for status in groups:
        items = by_status[status]
        totals[status] = len(items)
        header = col(status, f"  {status} ({len(items)})")
        print(header)
        print("  " + "─" * 60)
        for item in items:
            name = item["script"].ljust(45)
            extra = item["blocks"] or item["reason"] or ""
            if extra:
                extra = f"  ← {extra[:55]}"
            print(f"  {col(status, name)}{extra}")
        print()

    # Summary bar
    print("  " + "─" * 60)
    summary_parts = [f"{col(s, s)}: {n}" for s, n in totals.items()]
    print("  " + " │ ".join(summary_parts))
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--fail-on-placeholder", action="store_true",
                        help="Exit 1 if any script is PLACEHOLDER")
    parser.add_argument("--no-colour", action="store_true")
    args = parser.parse_args()

    results = collect()

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_table(results, colour=not args.no_colour)

    if args.fail_on_placeholder:
        blockers = [r for r in results if r["status"] == "PLACEHOLDER"]
        if blockers:
            if not args.json:
                print(f"\n[FAIL] {len(blockers)} placeholder script(s) still present.")
            sys.exit(1)


if __name__ == "__main__":
    main()
