---
name: backend-development
description: Expert backend architecture for SMB automation APIs. Use when designing QuickBooks, ShipStation, or payment integrations. Covers REST APIs, webhooks, authentication, and resilience patterns.
---

# Backend Development for SMB Automation

Expert backend architecture specializing in scalable API design for business automation workflows.

## When to Use This Skill

- Designing REST APIs for QuickBooks Online integration
- Building ShipStation order sync endpoints
- Creating webhook handlers for payment notifications
- Implementing OAuth 2.0 flows for third-party services
- Setting up resilient API patterns with retry logic

## Core Patterns for SMB Integrations

### 1. QuickBooks Online API Pattern
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx

class Invoice(BaseModel):
    customer_id: str
    line_items: list
    due_date: str

async def create_qbo_invoice(invoice: Invoice, access_token: str):
    """Create invoice in QuickBooks Online."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{QBO_BASE_URL}/invoice",
            headers={"Authorization": f"Bearer {access_token}"},
            json=invoice.model_dump()
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code)
        return response.json()
```

### 2. Webhook Handler Pattern
```python
@app.post("/webhooks/stripe")
async def handle_stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature")

    # Verify signature
    try:
        event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Idempotent processing
    if await is_event_processed(event["id"]):
        return {"status": "already_processed"}

    # Handle event types
    match event["type"]:
        case "payment_intent.succeeded":
            await handle_payment_success(event["data"]["object"])
        case "invoice.paid":
            await sync_to_quickbooks(event["data"]["object"])

    await mark_event_processed(event["id"])
    return {"status": "processed"}
```

### 3. OAuth 2.0 Token Management
```python
class TokenManager:
    """Manage OAuth tokens with automatic refresh."""

    async def get_valid_token(self, service: str) -> str:
        token = await self.get_stored_token(service)

        if self.is_expired(token):
            token = await self.refresh_token(service, token["refresh_token"])
            await self.store_token(service, token)

        return token["access_token"]

    async def refresh_token(self, service: str, refresh_token: str):
        # Service-specific refresh logic
        ...
```

### 4. Resilient API Client
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def call_external_api(url: str, data: dict):
    """Call external API with automatic retry on failure."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=data)
        response.raise_for_status()
        return response.json()
```

## Architecture Principles

1. **Validate at boundaries** - Use Pydantic for all external input
2. **Idempotent operations** - Use request IDs to prevent duplicates
3. **Async by default** - Use async/await for all I/O operations
4. **Structured logging** - Include correlation IDs in all logs
5. **Fail gracefully** - Return partial success where appropriate

## Integration with 3-Layer Architecture

- **Directives**: Define API requirements in `directives/`
- **Execution**: Implement actual API calls in `execution/`
- **This skill**: Provides patterns for connecting them

## Key API Endpoints for SMB Workflows

| Endpoint | Purpose |
|----------|---------|
| `POST /api/invoices` | Create QBO invoice from form |
| `POST /api/orders` | Create ShipStation order |
| `POST /webhooks/stripe` | Handle payment notifications |
| `GET /api/inventory` | Check stock levels |
| `POST /api/customers` | Sync customer data |

## Security Checklist

- [ ] Validate webhook signatures
- [ ] Use environment variables for secrets
- [ ] Implement rate limiting
- [ ] Log all API calls (not sensitive data)
- [ ] Use HTTPS for all external calls
- [ ] Rotate tokens before expiry
