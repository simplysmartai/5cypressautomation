"""
execution/shared — 5 Cypress Automation Core Utilities
=======================================================
Reusable infrastructure imported by every execution script.

Usage:
    from execution.shared.logger import get_logger
    from execution.shared.errors import APIError, safe_execute
    from execution.shared.config import settings
    from execution.shared.retry import with_retry
    from execution.shared.notify import notify_on_failure
    from execution.shared.anneal import self_anneal

These modules eliminate the 3 most common silent failure modes:
  1. Bare except: clauses that swallow errors
  2. print() output that vanishes (no log trail)
  3. Missing env vars discovered mid-execution
"""
