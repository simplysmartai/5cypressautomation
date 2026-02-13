---
name: code-documentation
description: Generate professional client-facing documentation for automation deliverables. Use when creating runbooks, deploy guides, or technical manuals for clients.
---

# Code Documentation for Client Deliverables

Every client gets professional documentation with their automation. This skill helps you create it fast.

## When to Use This Skill

- Delivering finished automation to a client
- Creating deploy guides for client infrastructure
- Writing runbooks for operational tasks
- Documenting API endpoints you've built
- Generating README files for client repos

## Client Documentation Package

Every project should include:

```
docs/
├── README.md              # Quick start (client reads first)
├── DEPLOY.md              # Deployment instructions
├── RUNBOOK.md             # Day-to-day operations
├── API.md                 # Endpoint documentation (if applicable)
└── TROUBLESHOOTING.md     # Common issues + fixes
```

## README Template

```markdown
# [Client Name] Automation

> [One-line description of what this automation does]

## What It Does

1. **[Step 1]**: [Brief description]
2. **[Step 2]**: [Brief description]
3. **[Step 3]**: [Brief description]

## Quick Start

### Prerequisites
- [ ] QuickBooks Online account (sandbox for testing)
- [ ] [Other required accounts]
- [ ] Node.js 18+ or Python 3.10+

### Setup (5 minutes)

1. Clone this repo
2. Copy `.env.example` to `.env`
3. Fill in your API credentials (see [DEPLOY.md](./DEPLOY.md))
4. Run: `npm install` or `pip install -r requirements.txt`
5. Start: `npm start` or `python main.py`

## Daily Operations

See [RUNBOOK.md](./RUNBOOK.md) for:
- How to manually trigger workflows
- Checking logs and status
- Handling common issues

## Support

- **Issues**: Open a GitHub issue or email support@yourdomain.com
- **Emergency**: [Your phone number] (business hours)

---
Built by [Your Company] | [Your Website]
```

## Deploy Guide Template

```markdown
# Deployment Guide

## Environment Setup

### 1. Get API Credentials

**QuickBooks Online**
1. Go to developer.intuit.com
2. Create an app (Sandbox first, then Production)
3. Copy Client ID and Client Secret to `.env`

**Stripe** (if applicable)
1. Go to dashboard.stripe.com/apikeys
2. Copy Secret Key to `.env`
3. Set up webhook endpoint: `your-domain.com/webhooks/stripe`

### 2. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Required variables:
| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `QBO_CLIENT_ID` | QuickBooks app ID | developer.intuit.com |
| `QBO_CLIENT_SECRET` | QuickBooks secret | developer.intuit.com |
| `QBO_REDIRECT_URI` | OAuth callback URL | Your domain + /callback |
| `STRIPE_SECRET_KEY` | Stripe API key | dashboard.stripe.com |

### 3. Deploy to [Platform]

**Option A: Heroku**
```bash
heroku create [app-name]
heroku config:set $(cat .env | xargs)
git push heroku main
```

**Option B: Railway**
1. Connect GitHub repo
2. Add environment variables from `.env`
3. Deploy

**Option C: Self-hosted (Docker)**
```bash
docker build -t automation .
docker run -d --env-file .env -p 3000:3000 automation
```

### 4. Verify Deployment

1. Visit `your-domain.com/health` - should return `{"status": "ok"}`
2. Trigger test workflow (see RUNBOOK.md)
3. Check logs for any errors

## Post-Deployment

- [ ] Set up monitoring (optional: UptimeRobot, Pingdom)
- [ ] Configure backup schedule
- [ ] Document any client-specific settings
```

## Runbook Template

```markdown
# Operations Runbook

## Daily Checks (2 minutes)

1. **Check system health**: `GET /health`
2. **Review error logs**: `logs/error.log` (last 24 hours)
3. **Verify webhooks received**: Check webhook logs

## Manual Triggers

### Trigger Invoice Sync
```bash
# CLI
python execution/sync_invoices.py --date today

# API
curl -X POST https://your-domain.com/api/sync/invoices
```

### Trigger Inventory Check
```bash
python execution/check_inventory.py --alert-threshold 10
```

## Common Tasks

### Re-process a Failed Invoice
1. Find the failed invoice in logs
2. Get the order ID
3. Run: `python execution/retry_invoice.py --order-id ORDER123`

### Manually Create QBO Invoice
```bash
python execution/create_invoice.py \
  --customer "Customer Name" \
  --amount 150.00 \
  --description "Service description"
```

### Check QuickBooks Connection
```bash
python execution/qbo_health.py
```
If expired, re-authenticate at `/auth/qbo`

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| "401 Unauthorized" from QBO | Token expired | Re-auth at `/auth/qbo` |
| Webhook not received | Endpoint down or misconfigured | Check logs, verify URL |
| Invoice created twice | Duplicate submission | Check idempotency keys |
| Inventory sync slow | Large catalog | Run during off-hours |

See [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for detailed steps.

## Escalation

If you can't resolve an issue:
1. Collect error logs and screenshots
2. Email support@yourdomain.com with:
   - What you were trying to do
   - What happened instead
   - Relevant logs
3. For urgent issues: [Your phone]
```

## API Documentation Template

```markdown
# API Reference

Base URL: `https://your-domain.com/api/v1`

## Authentication

All requests require Bearer token:
```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Create Invoice
`POST /invoices`

**Request:**
```json
{
  "customer_email": "customer@example.com",
  "line_items": [
    {
      "description": "Service",
      "quantity": 1,
      "unit_price": 150.00
    }
  ],
  "due_date": "2025-02-15"
}
```

**Response:**
```json
{
  "invoice_id": "INV-001",
  "qbo_id": "12345",
  "status": "created",
  "total": 150.00
}
```

**Errors:**
| Code | Meaning |
|------|---------|
| 400 | Invalid request body |
| 401 | Missing or invalid API key |
| 422 | Validation failed (see errors array) |
| 500 | Internal error - contact support |

### Get Invoice
`GET /invoices/{invoice_id}`

### List Invoices
`GET /invoices?status=pending&limit=50`

### Webhook Events
Configure at `/settings/webhooks`

Events:
- `invoice.created` - New invoice created
- `invoice.paid` - Payment received
- `inventory.low` - Stock below threshold
```

## Best Practices

1. **Write for non-technical readers** - Clients aren't developers
2. **Include screenshots** - Visual guides reduce support requests
3. **Test your own docs** - Follow them on a fresh machine
4. **Version your docs** - Match to software releases
5. **Keep it updated** - Outdated docs cause confusion
