---
name: payment-processing
description: Stripe and PayPal integration for SMB invoicing. Use when implementing payment flows, webhooks, subscriptions, or refunds. PCI-compliant patterns for client automation.
---

# Payment Processing for SMB Automation

Master Stripe and PayPal payment integration for robust, PCI-compliant payment flows.

## When to Use This Skill

- Implementing Stripe checkout for client invoices
- Setting up subscription billing
- Handling payment webhooks
- Processing refunds and disputes
- Syncing payments to QuickBooks

## Quick Start: Stripe Checkout

```python
import stripe
from pydantic import BaseModel

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class CheckoutRequest(BaseModel):
    amount_cents: int
    customer_email: str
    invoice_id: str

async def create_checkout_session(request: CheckoutRequest):
    """Create Stripe checkout session for invoice payment."""
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': f'Invoice #{request.invoice_id}'},
                'unit_amount': request.amount_cents,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=f'{BASE_URL}/payment/success?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{BASE_URL}/payment/cancel',
        customer_email=request.customer_email,
        metadata={'invoice_id': request.invoice_id}
    )
    return session.url
```

## Webhook Handling (Critical)

```python
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig = request.headers.get("Stripe-Signature")

    # ALWAYS verify signature
    try:
        event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle events idempotently
    event_id = event["id"]
    if await is_processed(event_id):
        return {"status": "duplicate"}

    match event["type"]:
        case "payment_intent.succeeded":
            await handle_payment_success(event["data"]["object"])
        case "payment_intent.payment_failed":
            await handle_payment_failure(event["data"]["object"])
        case "customer.subscription.deleted":
            await handle_subscription_cancel(event["data"]["object"])

    await mark_processed(event_id)
    return {"status": "ok"}

async def handle_payment_success(payment_intent):
    """Sync successful payment to QuickBooks."""
    invoice_id = payment_intent["metadata"]["invoice_id"]

    # Mark invoice as paid in QBO
    await qbo_mark_invoice_paid(invoice_id, payment_intent["id"])

    # Log activity
    await log_activity("payment_received", {
        "invoice_id": invoice_id,
        "amount": payment_intent["amount"] / 100,
        "stripe_id": payment_intent["id"]
    })

    # Send confirmation email
    await send_payment_confirmation(payment_intent)
```

## QuickBooks Sync Pattern

```python
async def sync_payment_to_qbo(payment_intent):
    """Record Stripe payment in QuickBooks."""
    invoice_id = payment_intent["metadata"]["invoice_id"]

    payment = {
        "TotalAmt": payment_intent["amount"] / 100,
        "CustomerRef": {"value": payment_intent["customer"]},
        "Line": [{
            "Amount": payment_intent["amount"] / 100,
            "LinkedTxn": [{
                "TxnId": invoice_id,
                "TxnType": "Invoice"
            }]
        }],
        "PrivateNote": f"Stripe: {payment_intent['id']}"
    }

    return await qbo_create_payment(payment)
```

## Test Cards

| Card Number | Behavior |
|-------------|----------|
| 4242424242424242 | Success |
| 4000000000000002 | Declined |
| 4000002500003155 | Requires 3D Secure |
| 4000000000009995 | Insufficient funds |

## Safety Checklist

- [ ] Use test mode keys for development
- [ ] Verify webhook signatures ALWAYS
- [ ] Process webhooks idempotently
- [ ] Never log full card numbers
- [ ] Store secrets in .env (gitignored)
- [ ] Use cents for amounts (avoid float errors)

## Environment Variables

```bash
# .env.example
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

## Integration with 3-Layer Architecture

1. **Directive**: `directives/sales-to-qbo.md` defines the workflow
2. **Execution**: Payment scripts in `execution/`
3. **This skill**: Provides the implementation patterns

## Common Workflows

### Invoice Payment Flow
1. Form submitted → Create QBO invoice
2. Send invoice with Stripe checkout link
3. Customer pays via Stripe
4. Webhook received → Mark QBO invoice paid
5. Send confirmation email

### Subscription Billing
1. Customer signs up → Create Stripe customer
2. Attach payment method
3. Create subscription
4. Webhook: `invoice.paid` → Extend access
5. Webhook: `subscription.deleted` → Revoke access
