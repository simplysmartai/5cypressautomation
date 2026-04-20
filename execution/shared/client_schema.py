"""
Canonical client data schema for 5 Cypress Automation.

Merges all existing client data formats into a single validated model:
  - clients/nexairi/info.json            (info.json format)
  - clients/nexairi-mentis/client.json   (client.json format)
  - marketing-team/context/*.md           (Markdown context files)
  - config/clients.json                   (API tier management)

Every client folder should have exactly ONE client.json that validates against this.

Usage:
    from execution.shared.client_schema import ClientData, load_client, save_client

    client = load_client("nexairi")
    print(client.contact.email)
    save_client(client)
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

_PROJECT_ROOT = Path(__file__).parent.parent.parent
_CLIENTS_DIR = _PROJECT_ROOT / "clients"


# ─── Sub-models ───────────────────────────────────────────────────────────────

class ClientContact(BaseModel):
    name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""


class TrialProgram(BaseModel):
    type: str = ""
    investment: float = 0.0
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: str = "pending"  # pending | active | complete | cancelled


class CurrentSystems(BaseModel):
    form: str = ""
    accounting: str = ""
    shipping: str = ""
    inventory: str = ""
    crm: str = ""


class BusinessInfo(BaseModel):
    industry: str = ""
    monthly_order_volume: Optional[int] = None
    current_systems: CurrentSystems = Field(default_factory=CurrentSystems)
    pain_points: List[str] = Field(default_factory=list)
    what_they_sell: str = ""
    who_they_sell_to: str = ""
    main_goal: str = ""


class ROIEstimate(BaseModel):
    monthly_orders: int = 0
    manual_time_per_order: float = 0.0
    automated_time_per_order: float = 0.0
    hourly_cost: float = 0.0
    monthly_savings: float = 0.0
    annual_savings: float = 0.0


class ClientAPIAccess(BaseModel):
    """API tier management (from config/clients.json)."""
    api_key: str = ""
    tier: str = "starter"  # starter | growth | enterprise
    monthly_runs: int = 50
    current_month_runs: int = 0
    rate_limit_per_hour: int = 20
    allowed_skills: List[str] = Field(default_factory=lambda: ["all"])


# ─── Main schema ─────────────────────────────────────────────────────────────

class ClientData(BaseModel):
    """
    The canonical client record. One client.json per client folder.

    Fields are all Optional to allow partial onboarding — but
    operational scripts check and raise ValidationError for fields
    they need before proceeding.
    """

    # Identity
    slug: str  # e.g. "nexairi", "nexairi-mentis" — matches folder name
    name: str
    website: str = ""
    status: str = "prospect"
    # Status values: prospect | prospecting | trial | onboarding | active | paused | churned

    # Contact
    contact: ClientContact = Field(default_factory=ClientContact)

    # Business
    business: BusinessInfo = Field(default_factory=BusinessInfo)

    # Engagement
    engagement_type: str = ""  # e.g. "trial_program", "monthly_retainer"
    services: List[str] = Field(default_factory=list)
    automations: List[str] = Field(default_factory=list)

    # Trial program (if applicable)
    trial_program: Optional[TrialProgram] = None

    # ROI
    roi_estimate: Optional[ROIEstimate] = None

    # API access
    api_access: Optional[ClientAPIAccess] = None

    # Marketing context
    marketing_bio: str = ""  # free-form notes for marketing team
    strategy_brief_path: str = ""  # relative path to latest strategy brief

    # Dates
    start_date: Optional[str] = None
    contract_start: Optional[str] = None

    # Tags for filtering / reporting
    tags: List[str] = Field(default_factory=list)

    # Notes
    notes: str = ""

    @field_validator("slug")
    @classmethod
    def slug_format(cls, v: str) -> str:
        normalized = v.lower().strip().replace(" ", "-")
        if not normalized.replace("-", "").isalnum():
            raise ValueError(f"Slug '{v}' must contain only letters, numbers, and hyphens")
        return normalized

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        valid = {"prospect", "prospecting", "trial", "onboarding", "active", "paused", "churned"}
        if v not in valid:
            raise ValueError(f"Status '{v}' invalid. Choose from: {', '.join(sorted(valid))}")
        return v

    def require_contact_email(self) -> str:
        """Assert contact email is set — call before sending emails."""
        if not self.contact.email:
            from execution.shared.errors import ValidationError
            raise ValidationError(
                f"Client '{self.slug}' has no contact email set",
                field="contact.email",
            )
        return self.contact.email

    def require_website(self) -> str:
        """Assert website is set — call before SEO or CRO operations."""
        if not self.website:
            from execution.shared.errors import ValidationError
            raise ValidationError(
                f"Client '{self.slug}' has no website set",
                field="website",
            )
        return self.website


# ─── I/O helpers ─────────────────────────────────────────────────────────────

def load_client(slug: str) -> ClientData:
    """
    Load and validate a client from clients/{slug}/client.json.
    Falls back to info.json or client-config.json for legacy clients.
    """
    client_dir = _CLIENTS_DIR / slug

    if not client_dir.exists():
        from execution.shared.errors import ValidationError
        raise ValidationError(f"Client folder not found: clients/{slug}", field="slug", value=slug)

    # Try canonical file first
    canonical = client_dir / "client.json"
    if canonical.exists():
        with open(canonical, encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("slug", slug)
        return ClientData(**data)

    # Fall back to legacy formats — merge what we find
    merged: dict = {"slug": slug, "name": slug.replace("-", " ").title()}

    info_file = client_dir / "info.json"
    if info_file.exists():
        with open(info_file, encoding="utf-8") as f:
            info = json.load(f)
        merged.update({
            "name": info.get("client_name", merged["name"]),
            "website": info.get("website", ""),
            "status": _normalize_status(info.get("status", "prospect")),
            "notes": info.get("notes", ""),
            "tags": info.get("tags", []),
            "start_date": info.get("start_date"),
            "contact": {
                "name": info.get("contact_name", ""),
                "email": info.get("contact_email", ""),
                "phone": info.get("phone", ""),
            },
        })

    config_file = client_dir / "client-config.json"
    if config_file.exists():
        with open(config_file, encoding="utf-8") as f:
            cfg = json.load(f)
        merged.update({
            "name": cfg.get("client_name", merged["name"]),
            "status": _normalize_status(cfg.get("status", merged.get("status", "prospect"))),
            "engagement_type": cfg.get("engagement_type", ""),
            "notes": merged.get("notes", ""),
        })
        if "contact" in cfg:
            merged["contact"] = {
                "name": cfg["contact"].get("primary_contact", ""),
                "title": cfg["contact"].get("title", ""),
                "email": cfg["contact"].get("email", ""),
                "phone": cfg["contact"].get("phone", ""),
            }
        if "business_info" in cfg:
            bi = cfg["business_info"]
            merged["business"] = {
                "industry": bi.get("industry", ""),
                "monthly_order_volume": bi.get("monthly_order_volume"),
                "pain_points": bi.get("pain_points", []),
                "current_systems": bi.get("current_systems", {}),
            }
        if "trial_program" in cfg:
            merged["trial_program"] = cfg["trial_program"]
        if "roi_estimate" in cfg:
            merged["roi_estimate"] = cfg["roi_estimate"]

    return ClientData(**merged)


def save_client(client: ClientData) -> Path:
    """Write client to the canonical clients/{slug}/client.json."""
    client_dir = _CLIENTS_DIR / client.slug
    client_dir.mkdir(parents=True, exist_ok=True)
    out_file = client_dir / "client.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(client.model_dump(), f, indent=2, default=str)
    return out_file


def list_clients() -> list[str]:
    """Return slugs for all client folders."""
    if not _CLIENTS_DIR.exists():
        return []
    return [
        d.name for d in _CLIENTS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]


def _normalize_status(s: str) -> str:
    mapping = {
        "lead": "prospect",
        "active_client": "active",
        "inactive": "paused",
    }
    return mapping.get(s, s) if s else "prospect"
