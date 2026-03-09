"""
Centralised environment & configuration management.

Reads ALL environment variables at import time and validates them.
A missing required variable raises ConfigError immediately — not 30 seconds
into an API call when you can't tell where it broke.

Usage:
    from execution.shared.config import settings

    qbo_client_id = settings.qbo_client_id
    stripe_key = settings.stripe_secret_key
    is_sandbox = settings.qbo_sandbox

Variables are split into groups:
  - REQUIRED: Script exits with ConfigError if missing
  - OPTIONAL_WITH_DEFAULT: Has a safe fallback
  - FEATURE_FLAGS: Enable/disable integrations gracefully

Add new vars here as the platform grows. Never call os.getenv() directly
in execution scripts — always go through settings.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from execution.shared.errors import ConfigError

# Load .env relative to the project root
_PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=False)  # don't override real env vars


def _require(var: str) -> str:
    """Return env var value or raise ConfigError with a clear fix message."""
    val = os.environ.get(var, "").strip()
    if not val:
        raise ConfigError(
            f"Required environment variable '{var}' is not set. "
            f"Add it to your .env file or deployment environment. "
            f"See .env.example for the full list.",
            missing_var=var,
        )
    return val


def _optional(var: str, default: str = "") -> str:
    return os.environ.get(var, default).strip()


def _flag(var: str, default: bool = False) -> bool:
    val = os.environ.get(var, "").strip().lower()
    if not val:
        return default
    return val in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class _Settings:
    """
    Immutable settings object. All values resolved at import time.

    Frozen = you can't accidentally overwrite a setting mid-run.
    """

    # ── Admin ────────────────────────────────────────────────────────────────
    admin_user: str = field(default_factory=lambda: _optional("ADMIN_USER", "admin"))
    admin_pass: str = field(default_factory=lambda: _optional("ADMIN_PASS"))

    # ── QuickBooks Online ─────────────────────────────────────────────────────
    qbo_client_id: str = field(default_factory=lambda: _optional("QUICKBOOKS_CLIENT_ID"))
    qbo_client_secret: str = field(default_factory=lambda: _optional("QUICKBOOKS_CLIENT_SECRET"))
    qbo_realm_id: str = field(default_factory=lambda: _optional("QUICKBOOKS_REALM_ID"))
    qbo_refresh_token: str = field(default_factory=lambda: _optional("QUICKBOOKS_REFRESH_TOKEN"))
    qbo_sandbox: bool = field(default_factory=lambda: _flag("QUICKBOOKS_SANDBOX", True))

    # ── Stripe ────────────────────────────────────────────────────────────────
    stripe_secret_key: str = field(default_factory=lambda: _optional("STRIPE_SECRET_KEY"))
    stripe_webhook_secret: str = field(default_factory=lambda: _optional("STRIPE_WEBHOOK_SECRET"))

    # ── Email ────────────────────────────────────────────────────────────────
    resend_api_key: str = field(default_factory=lambda: _optional("RESEND_API_KEY"))
    from_email: str = field(default_factory=lambda: _optional("FROM_EMAIL", "jimmy@5cypress.com"))

    # ── Anthropic / OpenAI ───────────────────────────────────────────────────
    anthropic_api_key: str = field(default_factory=lambda: _optional("ANTHROPIC_API_KEY"))
    openai_api_key: str = field(default_factory=lambda: _optional("OPENAI_API_KEY"))

    # ── DataForSEO ───────────────────────────────────────────────────────────
    dataforseo_username: str = field(default_factory=lambda: _optional("DATAFORSEO_USERNAME"))
    dataforseo_password: str = field(default_factory=lambda: _optional("DATAFORSEO_PASSWORD"))

    # ── Google APIs ──────────────────────────────────────────────────────────
    google_pagespeed_api_key: str = field(default_factory=lambda: _optional("GOOGLE_PAGESPEED_API_KEY"))

    # ── Zoho Calendar ────────────────────────────────────────────────────────
    zoho_client_id: str = field(default_factory=lambda: _optional("ZOHO_CLIENT_ID"))
    zoho_client_secret: str = field(default_factory=lambda: _optional("ZOHO_CLIENT_SECRET"))
    zoho_refresh_token: str = field(default_factory=lambda: _optional("ZOHO_REFRESH_TOKEN"))

    # ── Notifications ────────────────────────────────────────────────────────
    telegram_bot_token: str = field(default_factory=lambda: _optional("TELEGRAM_BOT_TOKEN"))
    telegram_chat_id: str = field(default_factory=lambda: _optional("TELEGRAM_CHAT_ID"))
    slack_webhook_url: str = field(default_factory=lambda: _optional("SLACK_WEBHOOK_URL"))

    # ── Calendly ────────────────────────────────────────────────────────────
    calendly_webhook_signing_key: str = field(
        default_factory=lambda: _optional("CALENDLY_WEBHOOK_SIGNING_KEY")
    )
    calendly_url: str = field(
        default_factory=lambda: _optional("CALENDLY_URL",
                                          "https://calendly.com/jimmy-5cypress/30min")
    )

    # ── Server ───────────────────────────────────────────────────────────────
    port: int = field(default_factory=lambda: int(_optional("PORT", "3000")))
    node_env: str = field(default_factory=lambda: _optional("NODE_ENV", "development"))

    # ── Paths ────────────────────────────────────────────────────────────────
    project_root: Path = field(default_factory=lambda: _PROJECT_ROOT)
    marketing_team_path: Path = field(
        default_factory=lambda: Path(
            _optional("MARKETING_TEAM_PATH",
                      str(_PROJECT_ROOT / "marketing-team"))
        )
    )

    # ── Feature flags ────────────────────────────────────────────────────────
    dry_run: bool = field(default_factory=lambda: _flag("DRY_RUN", False))
    notifications_enabled: bool = field(
        default_factory=lambda: _flag("NOTIFICATIONS_ENABLED", True)
    )

    def require_qbo(self) -> None:
        """Assert all QuickBooks vars are set. Call before any QBO operation."""
        missing = [
            v for v, a in [
                ("QUICKBOOKS_CLIENT_ID", self.qbo_client_id),
                ("QUICKBOOKS_CLIENT_SECRET", self.qbo_client_secret),
                ("QUICKBOOKS_REALM_ID", self.qbo_realm_id),
                ("QUICKBOOKS_REFRESH_TOKEN", self.qbo_refresh_token),
            ] if not a
        ]
        if missing:
            raise ConfigError(
                f"QuickBooks credentials missing: {', '.join(missing)}",
                missing_var=missing[0],
            )

    def require_stripe(self) -> None:
        """Assert Stripe vars are set. Call before any payment operation."""
        if not self.stripe_secret_key:
            raise ConfigError("Stripe secret key not configured",
                              missing_var="STRIPE_SECRET_KEY")

    def require_email(self) -> None:
        """Assert email sending is configured."""
        if not self.resend_api_key:
            raise ConfigError("RESEND_API_KEY not configured — cannot send email",
                              missing_var="RESEND_API_KEY")

    def require_notifications(self) -> None:
        """Assert at least one notification channel is configured."""
        has_telegram = bool(self.telegram_bot_token and self.telegram_chat_id)
        has_slack = bool(self.slack_webhook_url)
        if not (has_telegram or has_slack):
            raise ConfigError(
                "No notification channel configured. Set TELEGRAM_BOT_TOKEN + "
                "TELEGRAM_CHAT_ID, or SLACK_WEBHOOK_URL."
            )

    def is_production(self) -> bool:
        return self.node_env == "production"


# ─── Singleton ───────────────────────────────────────────────────────────────
settings = _Settings()
