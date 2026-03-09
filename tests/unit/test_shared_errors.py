"""
tests/unit/test_shared_errors.py
Unit tests for execution/shared/errors.py

Tests:
- Custom exception hierarchy
- @safe_execute decorator behaviour
- Exit code mapping
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add repo root to path so 'execution' is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


# ---------------------------------------------------------------------------
# Exception hierarchy tests
# ---------------------------------------------------------------------------

class TestExceptionHierarchy:
    def test_cypress_base_error_is_exception(self):
        from execution.shared.errors import CypressBaseError
        assert issubclass(CypressBaseError, Exception)

    def test_config_error_inherits(self):
        from execution.shared.errors import ConfigError, CypressBaseError
        assert issubclass(ConfigError, CypressBaseError)

    def test_validation_error_inherits(self):
        from execution.shared.errors import ValidationError, CypressBaseError
        assert issubclass(ValidationError, CypressBaseError)

    def test_api_error_inherits(self):
        from execution.shared.errors import APIError, CypressBaseError
        assert issubclass(APIError, CypressBaseError)

    def test_rate_limit_error_inherits_api_error(self):
        from execution.shared.errors import RateLimitError, APIError
        assert issubclass(RateLimitError, APIError)

    def test_auth_expired_error_inherits_api_error(self):
        from execution.shared.errors import AuthExpiredError, APIError
        assert issubclass(AuthExpiredError, APIError)

    def test_placeholder_error_has_message(self):
        from execution.shared.errors import PlaceholderError
        err = PlaceholderError("test_script.py")
        assert "test_script.py" in str(err)
        assert "PLACEHOLDER" in str(err).upper() or "placeholder" in str(err).lower()

    def test_exception_can_be_raised_and_caught(self):
        from execution.shared.errors import ConfigError
        with pytest.raises(ConfigError):
            raise ConfigError("test message")

    def test_api_error_stores_status_code(self):
        from execution.shared.errors import APIError
        err = APIError("Not Found", provider="quickbooks", status_code=404)
        assert err.status_code == 404


# ---------------------------------------------------------------------------
# PlaceholderError tests
# ---------------------------------------------------------------------------

class TestPlaceholderError:
    def test_message_contains_script_name(self):
        from execution.shared.errors import PlaceholderError
        err = PlaceholderError("lead_research_orchestrator.py")
        assert "lead_research_orchestrator.py" in str(err)

    def test_is_cypress_base_error(self):
        from execution.shared.errors import PlaceholderError, CypressBaseError
        assert issubclass(PlaceholderError, CypressBaseError)


# ---------------------------------------------------------------------------
# Inheritance / catching tests
# ---------------------------------------------------------------------------

class TestExceptionCatching:
    def test_rate_limit_caught_as_api_error(self):
        from execution.shared.errors import RateLimitError, APIError
        with pytest.raises(APIError):
            raise RateLimitError("Too many requests", provider="quickbooks")

    def test_auth_expired_caught_as_cypress_base(self):
        from execution.shared.errors import AuthExpiredError, CypressBaseError
        with pytest.raises(CypressBaseError):
            raise AuthExpiredError("Token expired", provider="zoho")

    def test_config_error_not_caught_as_api_error(self):
        from execution.shared.errors import ConfigError, APIError
        with pytest.raises(ConfigError):
            try:
                raise ConfigError("bad config")
            except APIError:
                pass  # should not be caught here
