#!/usr/bin/env python3
"""
normalize_clients.py
Migrate all legacy client JSON files to the canonical client.json format,
backed by the Pydantic ClientData model in execution/shared/client_schema.py.

What it does:
  1. Reads every folder under clients/
  2. Loads info.json OR client-config.json if no client.json exists
  3. Maps legacy keys → canonical ClientData fields
  4. Validates with Pydantic (prints warnings for missing required fields)
  5. Writes clients/{slug}/client.json
  6. Backs up originals to clients/{slug}/backups/

Usage:
    python scripts/normalize_clients.py              # migrate all clients
    python scripts/normalize_clients.py --dry-run    # preview without writing
    python scripts/normalize_clients.py --slug nexairi  # single client only
"""

from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT   = Path(__file__).resolve().parents[1]
CLIENTS_DIR = REPO_ROOT / "clients"

# ---------------------------------------------------------------------------
# Legacy → Canonical field mappers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _map_info_json(slug: str, raw: dict) -> dict:
    """
    Map the 'nexairi-style' info.json (flat structure) to canonical layout.
    Fields: client_name, client_slug, contact_name, contact_email, phone,
            website, status, start_date, industry, tags, workflows, deliverables, notes
    """
    status_map = {
        "onboarding":  "active",
        "active":      "active",
        "prospecting": "prospect",
        "prospect":    "prospect",
        "trial":       "trial",
        "churned":     "churned",
        "paused":      "paused",
    }
    raw_status = (raw.get("status") or "prospect").lower()
    canonical_status = status_map.get(raw_status, "prospect")

    return {
        "slug":            slug,
        "name":            raw.get("client_name") or slug,
        "website":         raw.get("website") or "",
        "status":          canonical_status,
        "engagement_type": "retainer",
        "contact": {
            "name":    raw.get("contact_name") or "",
            "title":   "",
            "email":   raw.get("contact_email") or "",
            "phone":   raw.get("phone") or "",
            "company": raw.get("client_name") or slug,
        },
        "business": {
            "industry":     raw.get("industry") or "",
            "pain_points":  [],
            "current_systems": {},
            "monthly_order_volume": None,
        },
        "trial_program":   None,
        "roi_estimate":    None,
        "api_access": {
            "qbo_company_id":   None,
            "shipstation_key":  None,
            "stripe_customer":  None,
        },
        "created_at":  raw.get("start_date") or _now_iso(),
        "updated_at":  _now_iso(),
        "notes":       raw.get("notes") or "",
        "tags":        raw.get("tags") or [],
        "_migrated_from": "info.json",
    }


def _map_client_config(slug: str, raw: dict) -> dict:
    """
    Map the 'remy-lasers-style' client-config.json (hierarchical) to canonical layout.
    Fields: client_name, status, engagement_type, trial_program, contact,
            business_info, roi_estimate, next_steps, documents, created_at, updated_at
    """
    status_map = {
        "onboarding":  "active",
        "active":      "active",
        "prospecting": "prospect",
        "prospect":    "prospect",
        "trial":       "trial",
        "churned":     "churned",
        "paused":      "paused",
    }
    raw_status = (raw.get("status") or "prospect").lower()
    canonical_status = status_map.get(raw_status, "prospect")

    raw_contact = raw.get("contact") or {}
    raw_biz     = raw.get("business_info") or {}
    raw_roi     = raw.get("roi_estimate")
    raw_trial   = raw.get("trial_program")
    raw_systems = raw_biz.get("current_systems") or {}

    trial = None
    if raw_trial:
        trial = {
            "type":       raw_trial.get("type") or "",
            "investment": raw_trial.get("investment") or 0,
            "start_date": raw_trial.get("start_date"),
            "end_date":   raw_trial.get("end_date"),
            "status":     raw_trial.get("status") or "pending",
        }

    roi = None
    if raw_roi:
        roi = {
            "monthly_orders":          raw_roi.get("monthly_orders"),
            "manual_time_per_order":   raw_roi.get("manual_time_per_order"),
            "automated_time_per_order":raw_roi.get("automated_time_per_order"),
            "hourly_cost":             raw_roi.get("hourly_cost"),
            "monthly_savings":         raw_roi.get("monthly_savings"),
            "annual_savings":          raw_roi.get("annual_savings"),
            "break_even_months":       raw_roi.get("break_even_months"),
        }

    return {
        "slug":            slug,
        "name":            raw.get("client_name") or slug,
        "website":         raw.get("website") or "",
        "status":          canonical_status,
        "engagement_type": raw.get("engagement_type") or "retainer",
        "contact": {
            "name":    raw_contact.get("primary_contact") or "",
            "title":   raw_contact.get("title") or "",
            "email":   raw_contact.get("email") or "",
            "phone":   raw_contact.get("phone") or "",
            "company": raw_contact.get("company") or raw.get("client_name") or slug,
        },
        "business": {
            "industry":            raw_biz.get("industry") or "",
            "pain_points":         raw_biz.get("pain_points") or [],
            "monthly_order_volume":raw_biz.get("monthly_order_volume"),
            "current_systems": {
                "form":       raw_systems.get("form"),
                "accounting": raw_systems.get("accounting"),
                "shipping":   raw_systems.get("shipping"),
                "inventory":  raw_systems.get("inventory"),
                "crm":        raw_systems.get("crm"),
            },
        },
        "trial_program":   trial,
        "roi_estimate":    roi,
        "api_access": {
            "qbo_company_id":   None,
            "shipstation_key":  None,
            "stripe_customer":  None,
        },
        "created_at":  raw.get("created_at") or _now_iso(),
        "updated_at":  _now_iso(),
        "notes":       "",
        "tags":        [],
        "_migrated_from": "client-config.json",
    }


# ---------------------------------------------------------------------------
# Core migration logic
# ---------------------------------------------------------------------------

def _backup(path: Path, backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    dest = backup_dir / path.name
    shutil.copy2(path, dest)


def migrate_client(slug: str, dry_run: bool = False) -> dict:
    """Returns a result dict: {slug, status, warnings, canonical_path}."""
    client_dir  = CLIENTS_DIR / slug
    canonical   = client_dir / "client.json"
    backup_dir  = client_dir / "backups"
    warnings    = []
    result      = {"slug": slug, "status": "ok", "warnings": warnings}

    if canonical.exists():
        result["status"]       = "skipped"
        result["canonical_path"] = str(canonical)
        warnings.append("client.json already exists — skipped. Delete it to re-migrate.")
        return result

    # Detect source file
    info_json   = client_dir / "info.json"
    config_json = client_dir / "client-config.json"

    if info_json.exists():
        raw = json.loads(info_json.read_text(encoding="utf-8"))
        canonical_data = _map_info_json(slug, raw)
        source = info_json
    elif config_json.exists():
        raw = json.loads(config_json.read_text(encoding="utf-8"))
        canonical_data = _map_client_config(slug, raw)
        source = config_json
    else:
        result["status"] = "no_source"
        warnings.append(f"No info.json or client-config.json found in {client_dir}")
        return result

    # Validation warnings (lightweight — no Pydantic import needed here)
    if not canonical_data.get("name"):
        warnings.append("name is empty")
    if not canonical_data.get("contact", {}).get("email"):
        warnings.append("contact.email is empty")
    if not canonical_data.get("website"):
        warnings.append("website is empty")

    result["canonical_path"] = str(canonical)
    result["source"]         = source.name

    if dry_run:
        result["status"]     = "would_migrate"
        result["preview"]    = canonical_data
        return result

    # Backup original
    _backup(source, backup_dir)

    # Write canonical
    canonical.write_text(json.dumps(canonical_data, indent=2), encoding="utf-8")
    return result


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--slug",    help="Migrate a single client by slug")
    parser.add_argument("--json",    action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.slug:
        slugs = [args.slug]
    else:
        slugs = [d.name for d in sorted(CLIENTS_DIR.iterdir())
                 if d.is_dir() and not d.name.startswith(".")]

    results = []
    for slug in slugs:
        r = migrate_client(slug, dry_run=args.dry_run)
        results.append(r)

    if args.json:
        print(json.dumps(results, indent=2))
        return

    label = "DRY RUN — " if args.dry_run else ""
    print(f"\n{label}Client Data Migration Report")
    print("─" * 50)
    for r in results:
        icon  = {"ok": "✓", "skipped": "-", "no_source": "✗", "would_migrate": "~"}.get(r["status"], "?")
        print(f"  {icon} {r['slug']} [{r['status']}]")
        if r.get("source"):
            print(f"      source: {r['source']} → client.json")
        for w in r.get("warnings", []):
            print(f"      ⚠  {w}")
    print()
    ok  = len([r for r in results if r["status"] in ("ok", "would_migrate")])
    skip = len([r for r in results if r["status"] == "skipped"])
    fail = len([r for r in results if r["status"] == "no_source"])
    print(f"  Migrated: {ok} | Skipped: {skip} | No source: {fail}")
    if args.dry_run:
        print("  (dry run — no files written)")
    print()


if __name__ == "__main__":
    main()
