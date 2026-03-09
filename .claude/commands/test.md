# /test

Run the test suite and report coverage.

## Purpose
Execute all Python tests in `tests/` via pytest, then print a coverage summary.
Run this before every client delivery and every deploy.

## Quick run

```bash
# Run all tests
pytest

# With coverage report
pytest --cov=execution --cov-report=term-missing

# Run only a specific script's tests
pytest tests/unit/test_create_qbo_invoice.py -v

# Run integration tests (requires real API creds)
pytest tests/integration/ -v --timeout=30

# Fail if coverage drops below 80%
pytest --cov=execution --cov-fail-under=80
```

## Test structure

```
tests/
├── conftest.py              # shared fixtures (mock env, mock QBO client, etc.)
├── unit/
│   ├── test_create_qbo_invoice.py
│   ├── test_create_invoice.py
│   ├── test_create_shipping_order.py
│   ├── test_send_email.py
│   ├── test_client_schema.py
│   └── test_shared_errors.py
└── integration/
    ├── test_qbo_sandbox.py   # real QBO sandbox call
    └── test_stripe_test.py   # real Stripe test-mode call
```

## Coverage targets
| Module | Target |
|--------|--------|
| `create_qbo_invoice.py` | ≥ 90% |
| `create_invoice.py` | ≥ 90% |
| `create_shipping_order.py` | ≥ 80% |
| `send_email.py` | ≥ 80% |
| `execution/shared/` | ≥ 85% |
| Overall | ≥ 80% |

## Writing a new test

Every execution script gets a companion test in `tests/unit/test_{script_name}.py`:

```python
# tests/unit/test_create_qbo_invoice.py
import pytest
from unittest.mock import patch, MagicMock

def test_invoice_created_successfully(mock_env, mock_qbo_client):
    """Happy path: valid order produces a QBO invoice."""
    from execution.create_qbo_invoice import create_invoice
    result = create_invoice(order_data={"customer": "Test Corp", "amount": 500})
    assert result["success"] is True
    assert "invoice_id" in result

def test_missing_qbo_creds_raises(monkeypatch):
    """Missing QBO_CLIENT_ID must raise ConfigError, not crash silently."""
    monkeypatch.delenv("QBO_CLIENT_ID", raising=False)
    from execution.shared.errors import ConfigError
    with pytest.raises(ConfigError):
        from execution.shared.config import _Settings
        _Settings().require_qbo()
```

## Fixtures (conftest.py)

```python
@pytest.fixture
def mock_env(monkeypatch):
    """Sets all required env vars to test values."""
    monkeypatch.setenv("QBO_CLIENT_ID", "test_id")
    monkeypatch.setenv("QBO_CLIENT_SECRET", "test_secret")
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_xxx")
    # ... etc
```

## CI integration

Add to `package.json`:
```json
"scripts": {
  "test:python": "pytest --cov=execution --cov-fail-under=80",
  "test:all": "npm run test:python"
}
```

Pre-deploy check:
```bash
npm run test:all && python scripts/check_health.py --fail-fast
```

## Related
- `/health-check` — system-level checks before running tests
- `/deploy-check` — full gate that includes test run
- `tests/` — test directory (TODO 10)
- `pytest.ini` — pytest configuration (TODO 10)
