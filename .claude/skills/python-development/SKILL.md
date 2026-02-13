---
name: python-development
description: Modern Python 3.12+ development with FastAPI, Pydantic, async patterns. Use for building execution scripts, API endpoints, and automation workflows.
---

# Python Development for SMB Automation

Modern Python 3.12+ patterns for building reliable automation scripts and APIs.

## When to Use This Skill

- Building new execution scripts in `execution/`
- Creating FastAPI endpoints for webhooks
- Implementing async API integrations
- Setting up Pydantic validation
- Optimizing existing Python code

## Project Structure

```
execution/
├── __init__.py
├── qbo_client.py          # QuickBooks API client
├── shipstation_client.py  # ShipStation API client
├── stripe_webhook.py      # Payment webhook handler
├── send_email.py          # Email delivery
├── validators.py          # Pydantic models
└── utils/
    ├── retry.py           # Retry logic
    └── logging.py         # Structured logging
```

## Quick Patterns

### 1. Pydantic Validation (Always Use)
```python
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class InvoiceRequest(BaseModel):
    customer_email: EmailStr
    customer_name: str = Field(min_length=1, max_length=100)
    line_items: list[LineItem]
    due_date: datetime

    class Config:
        extra = "forbid"  # Reject unknown fields

class LineItem(BaseModel):
    description: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)

    @property
    def total(self) -> float:
        return self.quantity * self.unit_price
```

### 2. Async HTTP Client
```python
import httpx
from typing import Any

class APIClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}

    async def get(self, endpoint: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def post(self, endpoint: str, data: dict) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/{endpoint}",
                headers=self.headers,
                json=data,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
```

### 3. Retry with Exponential Backoff
```python
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
import httpx

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException))
)
async def resilient_api_call(url: str, data: dict):
    """API call with automatic retry on transient failures."""
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, timeout=30.0)
        response.raise_for_status()
        return response.json()
```

### 4. Structured Logging
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)

    def info(self, message: str, **context):
        self.logger.info(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "level": "INFO",
            "message": message,
            **context
        }))

    def error(self, message: str, error: Exception = None, **context):
        self.logger.error(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "level": "ERROR",
            "message": message,
            "error": str(error) if error else None,
            **context
        }))

# Usage
log = StructuredLogger("execution")
log.info("Invoice created", invoice_id="INV-001", customer="john@example.com")
```

### 5. Environment Variables
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    qbo_client_id: str
    qbo_client_secret: str
    stripe_secret_key: str
    resend_api_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## FastAPI Endpoint Pattern

```python
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel

app = FastAPI()

class CreateInvoiceRequest(BaseModel):
    customer_email: str
    amount: float
    description: str

@app.post("/api/invoices")
async def create_invoice(request: CreateInvoiceRequest):
    try:
        # Validate inventory
        if not await check_inventory(request):
            raise HTTPException(status_code=400, detail="Insufficient inventory")

        # Create in QuickBooks
        invoice = await qbo_create_invoice(request)

        # Log activity
        await log_activity("invoice_created", invoice_id=invoice.id)

        return {"invoice_id": invoice.id, "status": "created"}

    except QBOAuthError:
        raise HTTPException(status_code=401, detail="QuickBooks auth expired")
    except Exception as e:
        log.error("Invoice creation failed", error=e)
        raise HTTPException(status_code=500, detail="Internal error")
```

## Testing Pattern

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def mock_qbo_client():
    with patch("execution.qbo_client.QBOClient") as mock:
        mock.return_value.create_invoice = AsyncMock(
            return_value={"Id": "123", "DocNumber": "INV-001"}
        )
        yield mock

@pytest.mark.asyncio
async def test_create_invoice(mock_qbo_client):
    request = CreateInvoiceRequest(
        customer_email="test@example.com",
        amount=100.00,
        description="Test invoice"
    )

    result = await create_invoice(request)

    assert result["status"] == "created"
    mock_qbo_client.return_value.create_invoice.assert_called_once()
```

## Dependencies (requirements.txt)

```
fastapi>=0.109.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
httpx>=0.26.0
tenacity>=8.2.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-asyncio>=0.23.0
```

## Common Mistakes to Avoid

1. **Sync in async code** - Don't use `requests`, use `httpx`
2. **Missing validation** - Always use Pydantic models
3. **Hardcoded secrets** - Use environment variables
4. **No retry logic** - External APIs fail; handle it
5. **Silent failures** - Log all errors with context
