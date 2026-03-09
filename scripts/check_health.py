#!/usr/bin/env python3
"""
check_health.py
System-wide health validator for 5 Cypress Automation.

Checks every sub-system before a deploy or first run on a new machine.
Run this whenever something breaks — it will tell you exactly what's wrong
and which directive / script to look at.

Usage:
    python scripts/check_health.py              # full report, colour
    python scripts/check_health.py --json       # JSON output for CI / server
    python scripts/check_health.py --fail-fast  # exit 1 on first error
    python scripts/check_health.py --fix        # auto-fix safe items (create dirs)

Exit codes:
    0 - all checks pass
    1 - at least one CRITICAL or ERROR
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT     = Path(__file__).resolve().parents[1]
EXECUTION_DIR = REPO_ROOT / "execution"
LOGS_DIR      = REPO_ROOT / "logs"
CLIENTS_DIR   = REPO_ROOT / "clients"
CONFIG_DIR    = REPO_ROOT / "config"
DB_PATH       = REPO_ROOT / "database.db"   # better-sqlite3 Node db

REQUIRED_DIRS  = [LOGS_DIR, EXECUTION_DIR / "shared", REPO_ROOT / "directives"]
ANNEAL_LOG     = LOGS_DIR / "anneal.log"

# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------
OK       = "OK"
WARN     = "WARN"
ERROR    = "ERROR"
CRITICAL = "CRITICAL"

COLOUR = {
    OK:       "\033[92m",  # green
    WARN:     "\033[93m",  # yellow
    ERROR:    "\033[91m",  # red
    CRITICAL: "\033[95m",  # magenta
}
RESET = "\033[0m"
BOLD  = "\033[1m"


class Check:
    def __init__(self, name: str, level: str, message: str, detail: str = ""):
        self.name    = name
        self.level   = level      # OK / WARN / ERROR / CRITICAL
        self.message = message
        self.detail  = detail

    def to_dict(self) -> dict:
        return {"name": self.name, "level": self.level,
                "message": self.message, "detail": self.detail}


# ---------------------------------------------------------------------------
# Individual checks
# ---------------------------------------------------------------------------

def check_required_dirs(auto_fix: bool) -> list[Check]:
    results = []
    for d in REQUIRED_DIRS:
        if d.exists():
            results.append(Check("required_dirs", OK, f"{d.relative_to(REPO_ROOT)} exists"))
        elif auto_fix:
            d.mkdir(parents=True, exist_ok=True)
            results.append(Check("required_dirs", WARN,
                                 f"Created missing dir: {d.relative_to(REPO_ROOT)}"))
        else:
            results.append(Check("required_dirs", ERROR,
                                 f"Missing directory: {d.relative_to(REPO_ROOT)}",
                                 "Run with --fix or create it manually"))
    return results


def check_shared_module() -> list[Check]:
    """Ensure execution/shared/ sub-package is importable."""
    results = []
    expected = [
        "execution/shared/__init__.py",
        "execution/shared/logger.py",
        "execution/shared/errors.py",
        "execution/shared/config.py",
        "execution/shared/retry.py",
        "execution/shared/notify.py",
        "execution/shared/anneal.py",
        "execution/shared/client_schema.py",
    ]
    for rel in expected:
        p = REPO_ROOT / rel
        if p.exists():
            results.append(Check("shared_module", OK, f"{rel} present"))
        else:
            results.append(Check("shared_module", CRITICAL, f"MISSING: {rel}",
                                 "execution/shared/ module is the foundation — recreate it"))
    return results


def check_env_vars() -> list[Check]:
    """Validate critical env vars are set (warns for optional ones)."""
    results = []
    # Load .env if present
    env_file = REPO_ROOT / ".env"
    if env_file.exists():
        try:
            from dotenv import dotenv_values
            env = {**dict(dotenv_values(env_file)), **os.environ}
        except ImportError:
            env = dict(os.environ)
    else:
        env = dict(os.environ)

    critical_vars = {
        "QBO_CLIENT_ID":     "QuickBooks OAuth",
        "QBO_CLIENT_SECRET": "QuickBooks OAuth",
        "STRIPE_SECRET_KEY": "Stripe payment processing",
    }
    warning_vars = {
        "RESEND_API_KEY":        "Email sending",
        "TELEGRAM_BOT_TOKEN":    "Failure alerts",
        "DATAFORSEO_LOGIN":      "SEO audits",
        "ANTHROPIC_API_KEY":     "AI features",
        "ZOHO_REFRESH_TOKEN":    "Calendar sync",
    }

    for var, purpose in critical_vars.items():
        if env.get(var):
            results.append(Check("env_vars", OK, f"{var} is set ({purpose})"))
        else:
            results.append(Check("env_vars", ERROR, f"{var} NOT SET — {purpose} will fail",
                                 f"Add to .env: {var}=<value>"))

    for var, purpose in warning_vars.items():
        if env.get(var):
            results.append(Check("env_vars", OK, f"{var} is set ({purpose})"))
        else:
            results.append(Check("env_vars", WARN, f"{var} missing — {purpose} disabled",
                                 f"Add to .env to enable: {var}=<value>"))
    return results


def check_placeholder_scripts() -> list[Check]:
    """Count PLACEHOLDER / NEEDS_CONFIG / PARTIAL scripts."""
    status_re  = re.compile(r"#\s*SCRIPT_STATUS\s*:\s*(\S+)", re.IGNORECASE)
    blocks_re  = re.compile(r"#\s*BLOCKS\s*:\s*(.+)",         re.IGNORECASE)
    results    = []
    placeholders = []
    needs_cfg    = []
    partials     = []

    for path in sorted(EXECUTION_DIR.glob("*.py")):
        if path.parent != EXECUTION_DIR:
            continue
        header = "".join(path.read_text(encoding="utf-8", errors="replace")
                         .splitlines(keepends=True)[:20])
        m = status_re.search(header)
        if not m:
            continue
        status  = m.group(1).upper()
        blocks  = ""
        bm = blocks_re.search(header)
        if bm:
            blocks = bm.group(1).strip()

        entry = (path.name, blocks)
        if status == "PLACEHOLDER":
            placeholders.append(entry)
        elif status == "NEEDS_CONFIG":
            needs_cfg.append(entry)
        elif status == "PARTIAL":
            partials.append(entry)

    for name, blocks in placeholders:
        results.append(Check("readiness", WARN,
                             f"PLACEHOLDER: {name}",
                             f"Blocks: {blocks}" if blocks else ""))
    for name, blocks in needs_cfg:
        results.append(Check("readiness", WARN,
                             f"NEEDS_CONFIG: {name}",
                             f"Blocks: {blocks}" if blocks else ""))
    for name, blocks in partials:
        results.append(Check("readiness", WARN,
                             f"PARTIAL: {name}",
                             f"Blocks: {blocks}" if blocks else ""))

    if not (placeholders or needs_cfg or partials):
        results.append(Check("readiness", OK, "All tagged scripts are READY"))
    return results


def check_bare_excepts() -> list[Check]:
    """Regression guard — confirm zero bare `except:` remain."""
    bare_re = re.compile(r"^\s+except:\s*$", re.MULTILINE)
    offenders = []
    for path in EXECUTION_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        if bare_re.search(text):
            offenders.append(path.name)

    if offenders:
        return [Check("bare_except", ERROR,
                      f"Bare except: found in {len(offenders)} script(s)",
                      ", ".join(offenders))]
    return [Check("bare_except", OK, "Zero bare except: clauses — regression check passed")]


def check_anneal_log() -> list[Check]:
    """Look for unresolved failures recorded by anneal.py."""
    if not ANNEAL_LOG.exists():
        return [Check("anneal", OK, "anneal.log not yet created (no failures logged)")]

    unresolved = []
    try:
        for line in ANNEAL_LOG.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
                if entry.get("type") == "failure" and not entry.get("resolved"):
                    unresolved.append(entry)
            except (json.JSONDecodeError, ValueError):
                pass
    except Exception as exc:
        return [Check("anneal", WARN, f"Could not read anneal.log: {exc}")]

    if unresolved:
        return [Check("anneal", WARN,
                      f"{len(unresolved)} unresolved failure(s) in anneal.log",
                      "; ".join(u.get("script", "?") for u in unresolved[:5]))]
    return [Check("anneal", OK, "No unresolved failures in anneal.log")]


def check_recent_errors() -> list[Check]:
    """Scan today's log file for ERROR / CRITICAL entries."""
    today       = datetime.now(timezone.utc).date().isoformat()
    log_file    = LOGS_DIR / f"{today}.log"
    if not log_file.exists():
        return [Check("recent_logs", OK, f"No log file for {today} yet")]

    errors = []
    try:
        for line in log_file.read_text(encoding="utf-8").splitlines():
            try:
                entry = json.loads(line)
                if entry.get("level") in ("ERROR", "CRITICAL"):
                    errors.append(entry)
            except (json.JSONDecodeError, ValueError):
                pass
    except Exception as exc:
        return [Check("recent_logs", WARN, f"Could not read log: {exc}")]

    if errors:
        last = errors[-1]
        return [Check("recent_logs", WARN,
                      f"{len(errors)} ERROR/CRITICAL entries today",
                      f"Last: [{last.get('logger','?')}] {last.get('message','')}")]
    return [Check("recent_logs", OK, f"No errors in today's log ({today})")]


def check_client_data() -> list[Check]:
    """Ensure each client folder has at least one data file."""
    results = []
    if not CLIENTS_DIR.exists():
        return [Check("clients", WARN, "clients/ directory not found")]

    for client_dir in sorted(CLIENTS_DIR.iterdir()):
        if not client_dir.is_dir():
            continue
        jsonfiles = list(client_dir.glob("*.json"))
        if not jsonfiles:
            results.append(Check("clients", WARN,
                                 f"{client_dir.name}: no JSON files found",
                                 "Run scripts/normalize_clients.py"))
        else:
            # Check for canonical client.json
            if (client_dir / "client.json").exists():
                results.append(Check("clients", OK,
                                     f"{client_dir.name}: canonical client.json present"))
            else:
                names = [f.name for f in jsonfiles]
                results.append(Check("clients", WARN,
                                     f"{client_dir.name}: legacy format {names}",
                                     "Run scripts/normalize_clients.py to migrate"))
    if not results:
        results.append(Check("clients", WARN, "No client folders found in clients/"))
    return results


def check_server_inmemory() -> list[Check]:
    """Warn if server.js still uses in-memory arrays as data stores."""
    server_js = REPO_ROOT / "server.js"
    if not server_js.exists():
        return [Check("server", WARN, "server.js not found")]

    text = server_js.read_text(encoding="utf-8", errors="replace")
    patterns = [
        (r"let orders\s*=\s*\[",   "orders[]  — orders not persisted to SQLite"),
        (r"let clients\s*=\s*\[",  "clients[] — clients not persisted to SQLite"),
        (r"let workItems\s*=\s*\[","workItems[] — work items not persisted to SQLite"),
    ]
    results = []
    for pattern, label in patterns:
        if re.search(pattern, text):
            results.append(Check("server", WARN,
                                 f"In-memory store found: {label}",
                                 "See TODO 9: split server.js into route modules"))
    if not results:
        results.append(Check("server", OK, "No in-memory array stores detected in server.js"))
    return results


def check_config_files() -> list[Check]:
    """Validate required config JSON files are present and parseable."""
    results = []
    required = ["clients.json", "pricing.json"]
    for fname in required:
        p = CONFIG_DIR / fname
        if not p.exists():
            results.append(Check("config", ERROR, f"Missing: config/{fname}"))
            continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            results.append(Check("config", OK, f"config/{fname} valid JSON ({type(data).__name__})"))
        except json.JSONDecodeError as exc:
            results.append(Check("config", ERROR, f"config/{fname} invalid JSON: {exc}"))
    return results


def check_python_version() -> list[Check]:
    version = sys.version_info
    if version >= (3, 12):
        return [Check("python", OK, f"Python {version.major}.{version.minor}.{version.micro}")]
    elif version >= (3, 9):
        return [Check("python", WARN,
                      f"Python {version.major}.{version.minor} — recommend 3.12+")]
    else:
        return [Check("python", ERROR,
                      f"Python {version.major}.{version.minor} is too old",
                      "Upgrade to 3.12+")]


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

ALL_CHECKS = [
    ("Python version",         check_python_version),
    ("Required directories",   lambda: check_required_dirs(False)),
    ("Shared module files",    check_shared_module),
    ("Environment variables",  check_env_vars),
    ("Placeholder scripts",    check_placeholder_scripts),
    ("Bare except: regression",check_bare_excepts),
    ("Anneal log",             check_anneal_log),
    ("Recent log errors",      check_recent_errors),
    ("Client data files",      check_client_data),
    ("Config JSON files",      check_config_files),
    ("Server in-memory stores",check_server_inmemory),
]


def run_all(auto_fix: bool = False) -> list[Check]:
    checks = ALL_CHECKS[:]
    # Override required_dirs check with auto_fix flag
    checks[1] = ("Required directories", lambda: check_required_dirs(auto_fix))
    results: list[Check] = []
    for _label, fn in checks:
        results.extend(fn())
    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(results: list[Check], colour: bool = True) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def col(level: str, text: str) -> str:
        return (COLOUR.get(level, "") + text + RESET) if colour else text

    print(f"\n{BOLD}5 Cypress — Health Check  {now}{RESET}\n")

    current_group = None
    for r in results:
        if r.name != current_group:
            current_group = r.name
            print(f"  {BOLD}{r.name}{RESET}")
        icon = {"OK": "✓", "WARN": "!", "ERROR": "✗", "CRITICAL": "✗✗"}.get(r.level, "?")
        line = f"    {col(r.level, icon + ' ' + r.message)}"
        if r.detail:
            line += f"\n      {col(r.level, '↳ ' + r.detail)}"
        print(line)
    print()

    totals: dict[str, int] = {}
    for r in results:
        totals[r.level] = totals.get(r.level, 0) + 1

    parts = [f"{col(lvl, lvl)}: {n}" for lvl, n in totals.items()]
    print("  " + " | ".join(parts))

    worst = max(results, key=lambda r: [OK, WARN, ERROR, CRITICAL].index(r.level)
                if r.level in [OK, WARN, ERROR, CRITICAL] else 0)
    if worst.level in (ERROR, CRITICAL):
        print(f"\n  {col(CRITICAL, '✗ System not ready — fix errors above before deploying.')}\n")
    elif worst.level == WARN:
        print(f"\n  {col(WARN, '! Warnings present — review before next client delivery.')}\n")
    else:
        print(f"\n  {col(OK, '✓ All checks passed — system is healthy.')}\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json",       action="store_true")
    parser.add_argument("--fail-fast",  action="store_true")
    parser.add_argument("--fix",        action="store_true",
                        help="Auto-fix safe items (create missing directories)")
    parser.add_argument("--no-colour",  action="store_true")
    args = parser.parse_args()

    results: list[Check] = []

    for _label, fn in ALL_CHECKS:
        # swap in auto-fix version for dir check
        if _label == "Required directories":
            batch = check_required_dirs(args.fix)
        else:
            batch = fn()
        results.extend(batch)

        if args.fail_fast:
            bad = [r for r in batch if r.level in (ERROR, CRITICAL)]
            if bad:
                if args.json:
                    print(json.dumps([r.to_dict() for r in bad], indent=2))
                else:
                    print_report(bad, colour=not args.no_colour)
                sys.exit(1)

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        print_report(results, colour=not args.no_colour)

    worst_levels = {r.level for r in results}
    if CRITICAL in worst_levels or ERROR in worst_levels:
        sys.exit(1)


if __name__ == "__main__":
    main()
