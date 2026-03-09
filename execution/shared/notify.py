"""
Notification dispatcher — routes failure alerts to Telegram or Slack.

This is the early-warning system. Script failures surface here before
you notice them from a client complaint.

Usage:
    from execution.shared.notify import send_failure_alert, send_info

    # In production code, just use @safe_execute — it calls this automatically.
    # Direct use for custom alerts:
    send_info("Invoice batch completed", details={"count": 12, "client": "nexairi"})
    send_failure_alert(script="create_qbo_invoice", error="Auth expired", directive="directives/sales-to-qbo.md")
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from execution.shared.logger import get_logger

_log = get_logger("shared.notify")


def _get_settings():
    """Late import to avoid circular dependency at module load."""
    from execution.shared.config import settings
    return settings


def send_failure_alert(
    *,
    script: str,
    error: str,
    directive: str = "",
    context: dict[str, Any] | None = None,
) -> bool:
    """
    Send a failure notification to all configured channels.

    Returns True if at least one channel succeeded.
    """
    cfg = _get_settings()

    if not cfg.notifications_enabled:
        _log.debug("Notifications disabled — skipping alert", extra={"script": script})
        return False

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ctx_str = json.dumps(context or {}, default=str, indent=2) if context else ""

    message = (
        f"🔴 *5 Cypress — Script Failure*\n"
        f"*Script:* `{script}`\n"
        f"*Error:* {error}\n"
        f"*Time:* {ts}"
    )
    if directive:
        message += f"\n*Directive:* `{directive}`"
    if ctx_str:
        message += f"\n*Context:*\n```\n{ctx_str}\n```"

    sent = False

    # ── Telegram ─────────────────────────────────────────────────────────────
    if cfg.telegram_bot_token and cfg.telegram_chat_id:
        if _send_telegram(cfg.telegram_bot_token, cfg.telegram_chat_id, message):
            sent = True

    # ── Slack ─────────────────────────────────────────────────────────────────
    if cfg.slack_webhook_url:
        if _send_slack(cfg.slack_webhook_url, message):
            sent = True

    if not sent:
        _log.warning(
            "No notification channel available — check TELEGRAM_BOT_TOKEN or SLACK_WEBHOOK_URL",
            extra={"script": script},
        )

    return sent


def send_info(
    message: str,
    *,
    details: dict[str, Any] | None = None,
) -> None:
    """
    Send a non-failure informational alert (e.g. batch completed, invoice sent).
    Only dispatched if NOTIFICATIONS_ENABLED and notifications_enabled.
    """
    cfg = _get_settings()
    if not cfg.notifications_enabled:
        return

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = f"ℹ️ *5 Cypress*: {message} _{ts}_"
    if details:
        text += f"\n```\n{json.dumps(details, default=str, indent=2)}\n```"

    if cfg.telegram_bot_token and cfg.telegram_chat_id:
        _send_telegram(cfg.telegram_bot_token, cfg.telegram_chat_id, text)

    if cfg.slack_webhook_url:
        _send_slack(cfg.slack_webhook_url, text)


# ─── Channel implementations ─────────────────────────────────────────────────

def _send_telegram(token: str, chat_id: str, message: str) -> bool:
    """POST message to Telegram Bot API."""
    try:
        import requests
        resp = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"},
            timeout=10,
        )
        if resp.status_code == 200:
            _log.debug("Telegram notification sent")
            return True
        _log.warning("Telegram send failed",
                     extra={"status": resp.status_code, "body": resp.text[:200]})
        return False
    except Exception as exc:
        _log.warning("Telegram dispatch exception", extra={"error": str(exc)})
        return False


def _send_slack(webhook_url: str, message: str) -> bool:
    """POST message to Slack Incoming Webhook."""
    try:
        import requests
        # Convert Markdown bold to plain for Slack (which uses *text* natively)
        slack_text = message.replace("*", "")
        resp = requests.post(
            webhook_url,
            json={"text": slack_text},
            timeout=10,
        )
        if resp.status_code == 200:
            _log.debug("Slack notification sent")
            return True
        _log.warning("Slack send failed",
                     extra={"status": resp.status_code, "body": resp.text[:200]})
        return False
    except Exception as exc:
        _log.warning("Slack dispatch exception", extra={"error": str(exc)})
        return False
