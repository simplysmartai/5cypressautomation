"""
Retry logic with exponential backoff for external API calls.

Prevents transient failures (network blips, rate limits, brief downtime)
from becoming permanent failures. Referenced in skill docs but previously
had no implementation.

Usage:
    from execution.shared.retry import with_retry, RetryConfig

    # Simple: retry up to 3 times with default backoff
    result = with_retry(call_qbo_api, args=(data,))

    # Custom: stricter for payment endpoints
    payment_config = RetryConfig(max_attempts=2, base_delay=0.5)
    result = with_retry(charge_card, kwargs={"amount": amount},
                        config=payment_config)

    # Decorator form
    @retryable(max_attempts=4)
    def get_serp_results(keyword: str) -> dict:
        ...
"""

from __future__ import annotations

import functools
import time
from dataclasses import dataclass
from typing import Any, Callable, Sequence, Type

from execution.shared.errors import RateLimitError, APIError
from execution.shared.logger import get_logger

_log = get_logger("shared.retry")


@dataclass
class RetryConfig:
    """Backoff configuration for a retry context."""

    max_attempts: int = 3
    """Total number of attempts (including the first)."""

    base_delay: float = 1.0
    """Seconds to wait before first retry."""

    max_delay: float = 30.0
    """Cap on wait time between retries."""

    exponential_base: float = 2.0
    """Multiply delay by this factor each retry."""

    jitter: bool = True
    """Add random 0-1s jitter to avoid thundering herd."""

    retriable_exceptions: tuple[Type[Exception], ...] = (
        RateLimitError,
        APIError,
        ConnectionError,
        TimeoutError,
    )
    """Which exception types trigger a retry vs immediate failure."""


_DEFAULT = RetryConfig()


def with_retry(
    fn: Callable,
    *,
    args: tuple = (),
    kwargs: dict | None = None,
    config: RetryConfig = _DEFAULT,
    label: str = "",
) -> Any:
    """
    Call fn(*args, **kwargs) with retry logic.

    Args:
        fn: The function to call.
        args: Positional arguments to fn.
        kwargs: Keyword arguments to fn.
        config: RetryConfig controlling backoff behaviour.
        label: Human-readable label for log messages.

    Returns:
        The return value of fn on success.

    Raises:
        The last exception after all retries are exhausted.
    """
    kwargs = kwargs or {}
    label = label or getattr(fn, "__name__", str(fn))
    delay = config.base_delay
    last_exc: Exception | None = None

    for attempt in range(1, config.max_attempts + 1):
        try:
            result = fn(*args, **kwargs)
            if attempt > 1:
                _log.info(f"Succeeded on attempt {attempt}", extra={"fn": label})
            return result

        except config.retriable_exceptions as exc:
            last_exc = exc
            if attempt == config.max_attempts:
                _log.error(
                    f"All {config.max_attempts} attempts failed",
                    extra={"fn": label, "error": str(exc)},
                )
                raise

            # Honour Retry-After if provided by a RateLimitError
            if isinstance(exc, RateLimitError) and exc.ctx.get("retry_after"):
                delay = min(exc.ctx["retry_after"], config.max_delay)
            else:
                delay = min(delay * config.exponential_base, config.max_delay)

            if config.jitter:
                import random
                delay += random.uniform(0, 1)

            _log.warning(
                f"Attempt {attempt}/{config.max_attempts} failed — retrying in {delay:.1f}s",
                extra={"fn": label, "error": str(exc)},
            )
            time.sleep(delay)

        except Exception as exc:
            # Non-retriable — don't retry, don't log a retry message
            _log.error(
                f"Non-retriable error on attempt {attempt}",
                extra={"fn": label, "error": str(exc)},
            )
            raise

    # Should not reach here, but satisfy the type checker
    if last_exc:
        raise last_exc


def retryable(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    retriable_exceptions: Sequence[Type[Exception]] = (APIError, ConnectionError, TimeoutError),
) -> Callable:
    """
    Decorator form of with_retry.

    Usage:
        @retryable(max_attempts=4)
        def fetch_data() -> dict:
            ...
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        retriable_exceptions=tuple(retriable_exceptions),
    )

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            return with_retry(fn, args=args, kwargs=kwargs, config=config,
                              label=fn.__name__)
        return wrapper

    return decorator


# ─── Pre-configured configs for common contexts ───────────────────────────────

# For financial operations: fewer retries, fail fast
FINANCE_RETRY = RetryConfig(max_attempts=2, base_delay=0.5, max_delay=5.0)

# For data fetching: more patient, higher Max
DATA_RETRY = RetryConfig(max_attempts=5, base_delay=2.0, max_delay=60.0)

# For webhooks receiving (inbound): don't retry — just log
WEBHOOK_RETRY = RetryConfig(max_attempts=1)
