#!/usr/bin/env python3
"""
generate_skill_registry.py
Scan .claude/skills/, extract metadata, and write _meta/skill-registry.json.

Run whenever skills are added, renamed, or domains change:
    python scripts/generate_skill_registry.py

The registry is read by:
- /health-check — to flag missing or stale skills
- /post-mortem  — to find which skill covers a failed workflow
- AGENTS.md     — generated preamble for AI sessions
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT   = Path(__file__).resolve().parents[1]
SKILLS_DIR  = REPO_ROOT / ".claude" / "skills"
META_DIR    = SKILLS_DIR / "_meta"
REGISTRY    = META_DIR / "skill-registry.json"

# ---------------------------------------------------------------------------
# Domain mapping  (skill_folder_name → domain)
# ---------------------------------------------------------------------------
DOMAIN_MAP: dict[str, str] = {
    # ── Development
    "3d-web-experience":        "development",
    "api-scaffolding":          "development",
    "backend-development":      "development",
    "blockrun":                 "development",
    "code-documentation":       "development",
    "data-validation":          "development",
    "development":              "development",
    "exploratory-data-analysis":"development",
    "frontend-design":          "development",
    "mobile-design":            "development",
    "payment-processing":       "development",
    "python-development":       "development",
    "schema-markup":            "development",
    "senior-backend":           "development",
    "ui-design-system":         "development",
    "website-builder":          "development",

    # ── Marketing
    "ab-test-setup":            "marketing",
    "analytics-tracking":       "marketing",
    "campaign-presenter":       "marketing",
    "competitor-alternatives":  "marketing",
    "content-strategy":         "marketing",
    "copy-editing":             "marketing",
    "copywriting":              "marketing",
    "data-analysis-reporting":  "marketing",
    "email-campaign":           "marketing",
    "email-sequence":           "marketing",
    "executing-marketing-campaigns": "marketing",
    "free-tool-strategy":       "marketing",
    "launch-strategy":          "marketing",
    "marketing-ideas":          "marketing",
    "marketing-psychology":     "marketing",
    "marketing-research-strategy": "marketing",
    "paid-ads":                 "marketing",
    "product-marketing-context":"marketing",
    "referral-program":         "marketing",
    "social-content":           "marketing",
    "social-media-content":     "marketing",

    # ── SEO
    "5-cypress-premium-seo":    "seo",
    "programmatic-seo":         "seo",
    "seo-audit":                "seo",

    # ── Sales
    "customer-sales":           "sales",
    "cto-advisor":              "sales",
    "game-changing-features":   "sales",
    "pricing-strategy":         "sales",

    # ── Conversion (CRO)
    "form-cro":                 "conversion",
    "onboarding-cro":           "conversion",
    "page-cro":                 "conversion",
    "paywall-upgrade-cro":      "conversion",
    "popup-cro":                "conversion",
    "signup-flow-cro":          "conversion",
}

# ---------------------------------------------------------------------------
# Metadata extraction from SKILL.md
# ---------------------------------------------------------------------------
META_BLOCK  = re.compile(r"<!--\s*(.*?)\s*-->", re.DOTALL)
META_FIELDS = {
    "version":   re.compile(r"version\s*:\s*(\S+)"),
    "reviewed":  re.compile(r"reviewed\s*:\s*(\S+)"),
    "status":    re.compile(r"status\s*:\s*(\S+)"),
}
WHEN_PATTERN = re.compile(r"## When to (use|load) this skill\s*\n(.*?)(?=\n##|\Z)", re.DOTALL)
DESC_PATTERN = re.compile(r"^#.*?\n(.*?)(?=\n##|\Z)", re.DOTALL)


def _extract_meta(text: str) -> dict:
    """Pull version / reviewed / status from the HTML comment metadata block."""
    result: dict = {}
    for block in META_BLOCK.finditer(text):
        content = block.group(1)
        for field, pattern in META_FIELDS.items():
            if field not in result:
                m = pattern.search(content)
                if m:
                    result[field] = m.group(1).strip()
    return result


def _extract_description(text: str) -> str:
    """Pull the 'When to use/load this skill' text or first-paragraph description."""
    m = WHEN_PATTERN.search(text)
    if m:
        raw = m.group(2).strip()
        # Collapse to one line
        return " ".join(raw.split())[:200]
    # Fall back to first non-heading paragraph
    m2 = DESC_PATTERN.search(text)
    if m2:
        raw = m2.group(1).strip()
        lines = [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith("#")]
        return " ".join(lines)[:200]
    return ""


def _build_entry(folder: Path) -> dict:
    skill_id = folder.name
    skill_md = folder / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8", errors="replace") if skill_md.exists() else ""

    meta = _extract_meta(text)
    description = _extract_description(text)
    domain = DOMAIN_MAP.get(skill_id, "other")

    return {
        "skill_id":    skill_id,
        "domain":      domain,
        "version":     meta.get("version", "0.0.0"),
        "status":      meta.get("status",  "UNKNOWN"),
        "reviewed":    meta.get("reviewed","NEVER"),
        "has_skill_md": skill_md.exists(),
        "description": description,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    META_DIR.mkdir(parents=True, exist_ok=True)

    entries = []
    skipped = []
    for folder in sorted(SKILLS_DIR.iterdir()):
        if not folder.is_dir():
            continue
        if folder.name.startswith("_"):  # skip _meta/
            continue
        entries.append(_build_entry(folder))

    # Sort: domain → skill_id
    entries.sort(key=lambda e: (e["domain"], e["skill_id"]))

    registry = {
        "generated":       date.today().isoformat(),
        "total_skills":    len(entries),
        "domains":         sorted({e["domain"] for e in entries}),
        "needs_versioning": [e["skill_id"] for e in entries if e["version"] == "0.0.0"],
        "stale_review":    [e["skill_id"] for e in entries if e["reviewed"] == "NEVER"],
        "skills":          entries,
    }

    REGISTRY.write_text(json.dumps(registry, indent=2), encoding="utf-8")

    print(f"✓  Registry written → {REGISTRY.relative_to(REPO_ROOT)}")
    print(f"   {len(entries)} skills across {len(registry['domains'])} domains")
    if registry["needs_versioning"]:
        print(f"   ⚠  {len(registry['needs_versioning'])} skills missing version header")
    else:
        print("   ✓  All skills versioned")


if __name__ == "__main__":
    main()
