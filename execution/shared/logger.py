"""
Structured JSON logger for all execution scripts.

Replaces ad-hoc print() and inconsistent logging.basicConfig() calls.
Writes to both stdout (for terminal/operator) and logs/ directory (persistent).

Usage:
    from execution.shared.logger import get_logger
    log = get_logger(__name__)
    log.info("Invoice created", extra={"invoice_id": "INV-001", "client": "nexairi"})
    log.error("QBO auth failed", extra={"error": str(e)})
"""

import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ─── Resolve logs/ directory relative to project root ────────────────────────
_HERE = Path(__file__).parent.parent.parent  # project root
LOGS_DIR = _HERE / "logs"
LOGS_DIR.mkdir(exist_ok=True)


class _JSONFormatter(logging.Formatter):
    """Emit every log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # Include any extra fields set via log.info("msg", extra={...})
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "pathname", "process", "processName", "relativeCreated",
                "stack_info", "thread", "threadName", "exc_info", "exc_text",
                "message", "taskName",
            ):
                payload[key] = value

        # Attach exception info if present
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


class _ConsoleFormatter(logging.Formatter):
    """Human-readable formatter for the terminal."""

    LEVEL_COLORS = {
        "DEBUG":    "\033[37m",   # grey
        "INFO":     "\033[36m",   # cyan
        "WARNING":  "\033[33m",   # yellow
        "ERROR":    "\033[31m",   # red
        "CRITICAL": "\033[41m",   # red bg
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelname, self.RESET)
        ts = datetime.now().strftime("%H:%M:%S")
        prefix = f"{color}[{ts} {record.levelname}]{self.RESET} {record.name}"
        msg = record.getMessage()
        base = f"{prefix}: {msg}"

        # Show extra context keys inline
        skip = {
            "name", "msg", "args", "created", "filename", "funcName",
            "levelname", "levelno", "lineno", "module", "msecs", "message",
            "pathname", "process", "processName", "relativeCreated",
            "stack_info", "thread", "threadName", "exc_info", "exc_text",
            "taskName",
        }
        extras = {k: v for k, v in record.__dict__.items() if k not in skip}
        if extras:
            base += f"  {json.dumps(extras, default=str)}"

        if record.exc_info:
            base += "\n" + self.formatException(record.exc_info)

        return base


def get_logger(name: str, level: str | None = None) -> logging.Logger:
    """
    Return a configured logger that writes JSON to logs/<date>.log
    and pretty output to stderr.

    Args:
        name: Typically __name__ of the calling module.
        level: Override log level (default: LOG_LEVEL env var or INFO).
    """
    log_level_str = level or os.environ.get("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on re-import
    if logger.handlers:
        return logger

    logger.setLevel(log_level)
    logger.propagate = False

    # ── Console handler (stderr so it doesn't pollute JSON stdout) ──────────
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(_ConsoleFormatter())
    logger.addHandler(console_handler)

    # ── File handler — rotating daily ───────────────────────────────────────
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"{today}.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(_JSONFormatter())
    logger.addHandler(file_handler)

    return logger


# ─── Module-level logger for shared/ itself ──────────────────────────────────
_log = get_logger("shared.logger")
_log.debug("Logger initialised", extra={"log_dir": str(LOGS_DIR)})
