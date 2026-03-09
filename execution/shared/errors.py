"""
Custom exceptions and safe execution decorator for 5 Cypress scripts.

Design goals:
  - Every error has a type, message, context, and a recoverable flag
  - Bare except: clauses are eliminated — we always know what we caught
  - The @safe_execute decorator wraps any function with logging + notification
  - Script exit codes are non-zero on failure (so callers / server.js detect it)

Usage:
    from execution.shared.errors import APIError, ValidationError, safe_execute

    @safe_execute(context="create_qbo_invoice", directive="directives/sales-to-qbo.md")
    def main():
        ...

    raise APIError("QBO token expired", provider="quickbooks", recoverable=True)
"""

from __future__ import annotations

import functools
import json
import sys
import traceback
from pathlib import Path
from typing import Any, Callable

from execution.shared.logger import get_logger

_log = get_logger("shared.errors")


# ─── Exception hierarchy ──────────────────────────────────────────────────────

class CypressBaseError(Exception):
    """Base for all 5 Cypress errors. Carries structured context."""

    def __init__(
        self,
        message: str,
        *,
        recoverable: bool = False,
        context: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.recoverable = recoverable
        self.ctx = context or {}

    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "message": str(self),
            "recoverable": self.recoverable,
            "context": self.ctx,
        }


class ConfigError(CypressBaseError):
    """Missing or invalid configuration / environment variable.
    Always fatal — immediately tells the operator what to set.
    """
    def __init__(self, message: str, *, missing_var: str | None = None) -> None:
        super().__init__(message, recoverable=False,
                         context={"missing_var": missing_var})
        self.missing_var = missing_var


class ValidationError(CypressBaseError):
    """Input data failed Pydantic or business-rule validation.
    Recoverable because the caller can fix the input.
    """
    def __init__(self, message: str, *, field: str | None = None,
                 value: Any = None) -> None:
        super().__init__(message, recoverable=True,
                         context={"field": field, "value": str(value)})


class APIError(CypressBaseError):
    """External API call failed (QBO, ShipStation, Stripe, DataForSEO, etc.).
    May be recoverable (rate limit, timeout) or not (auth error).
    """
    def __init__(self, message: str, *, provider: str,
                 status_code: int | None = None,
                 recoverable: bool = False) -> None:
        super().__init__(message, recoverable=recoverable,
                         context={"provider": provider,
                                  "status_code": status_code})
        self.provider = provider
        self.status_code = status_code


class RateLimitError(APIError):
    """API rate limit hit. Always recoverable — just wait and retry."""
    def __init__(self, message: str, *, provider: str,
                 retry_after: int | None = None) -> None:
        super().__init__(message, provider=provider, status_code=429,
                         recoverable=True)
        self.ctx["retry_after"] = retry_after


class AuthExpiredError(APIError):
    """OAuth token / API key expired. Needs refresh, not a bug."""
    def __init__(self, message: str, *, provider: str) -> None:
        super().__init__(message, provider=provider, status_code=401,
                         recoverable=True)


class ScriptError(CypressBaseError):
    """Internal script logic error — a bug or an unhandled edge case."""
    def __init__(self, message: str, *, script: str | None = None) -> None:
        super().__init__(message, recoverable=False,
                         context={"script": script})


class PlaceholderError(CypressBaseError):
    """Raised when a stub / placeholder script is called in production.
    Prevents mock data from silently reaching real systems.
    """
    def __init__(self, script_name: str) -> None:
        super().__init__(
            f"Script '{script_name}' is a PLACEHOLDER and has not been "
            "implemented. Do not call it against production systems.",
            recoverable=False,
            context={"script": script_name},
        )


# ─── Safe execution decorator ─────────────────────────────────────────────────

def safe_execute(
    *,
    context: str = "",
    directive: str = "",
    notify: bool = True,
) -> Callable:
    """
    Decorator that wraps a function with:
      - Structured logging of start / success / failure
      - Consistent JSON error output to stdout
      - Non-zero exit code on failure
      - Optional notification dispatch (Telegram/Slack) on error

    Args:
        context: Human-readable name for log messages (e.g. "create_qbo_invoice").
        directive: Path to the directive this script implements, for error context.
        notify: Whether to dispatch a notification on failure.

    Example:
        @safe_execute(context="create_invoice", directive="directives/send_invoice.md")
        def main() -> int:
            ...
            return 0
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            label = context or fn.__name__
            _log.info(f"START {label}", extra={"directive": directive})

            try:
                result = fn(*args, **kwargs)
                _log.info(f"SUCCESS {label}")
                return result

            except PlaceholderError as exc:
                _log.error(f"PLACEHOLDER_CALLED {label}", extra=exc.to_dict())
                _emit_error(exc)
                sys.exit(2)

            except ConfigError as exc:
                _log.error(f"CONFIG_ERROR {label}", extra=exc.to_dict())
                _emit_error(exc)
                if notify:
                    _try_notify(label, exc, directive)
                sys.exit(3)

            except ValidationError as exc:
                _log.warning(f"VALIDATION_ERROR {label}", extra=exc.to_dict())
                _emit_error(exc)
                sys.exit(4)

            except AuthExpiredError as exc:
                _log.error(f"AUTH_EXPIRED {label}", extra=exc.to_dict())
                _emit_error(exc)
                if notify:
                    _try_notify(label, exc, directive)
                sys.exit(5)

            except APIError as exc:
                _log.error(f"API_ERROR {label}", extra=exc.to_dict())
                _emit_error(exc)
                if notify:
                    _try_notify(label, exc, directive)
                sys.exit(6)

            except CypressBaseError as exc:
                _log.error(f"SCRIPT_ERROR {label}", extra=exc.to_dict())
                _emit_error(exc)
                if notify:
                    _try_notify(label, exc, directive)
                sys.exit(7)

            except Exception as exc:
                # Catch-all — but we LOG it so it is never silent
                error_dict = {
                    "type": type(exc).__name__,
                    "message": str(exc),
                    "traceback": traceback.format_exc(),
                    "recoverable": False,
                    "context": {"directive": directive},
                }
                _log.exception(f"UNEXPECTED_ERROR {label}", extra=error_dict)
                _emit_error_dict(error_dict)
                if notify:
                    _try_notify(label, exc, directive)
                sys.exit(1)

        return wrapper
    return decorator


def _emit_error(exc: CypressBaseError) -> None:
    """Print structured JSON error to stdout (consumed by server.js / callers)."""
    _emit_error_dict(exc.to_dict())


def _emit_error_dict(d: dict) -> None:
    print(json.dumps({"success": False, "error": d}))


def _try_notify(label: str, exc: Exception, directive: str) -> None:
    """Best-effort notification — never let notification failure mask the original error."""
    try:
        from execution.shared.notify import send_failure_alert
        send_failure_alert(script=label, error=str(exc), directive=directive)
    except Exception as notify_exc:
        _log.warning("Notification dispatch failed",
                     extra={"notify_error": str(notify_exc)})
