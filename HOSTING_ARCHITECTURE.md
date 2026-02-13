# Hosting Architecture Guide: 5 Cypress Automation

**Date:** February 5, 2026  
**Decision:** No n8n - Pure Python with Modal/Serverless

---

## The Question

"Do I need a VPS if I'm not using n8n?"

**Short Answer:** No. You already have **Modal** set up, which is better than a VPS for your use case.

---

## Your Current Architecture (3-Layer System)

```
┌─────────────────────────────────────────────────┐
│  Layer 1: DIRECTIVES (Markdown SOPs)           │
│  - directives/*.md files                        │
│  - Version controlled, human-readable           │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Layer 2: ORCHESTRATION (AI Decision-Making)    │
│  - Claude Opus 4.5 (you)                        │
│  - Reads directives, makes decisions            │
│  - Calls execution scripts                      │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Layer 3: EXECUTION (Python Scripts)            │
│  - execution/*.py files                         │
│  - Deterministic API calls                      │
│  - Data processing, integrations                │
└─────────────────────────────────────────────────┘
```

**n8n is NOT needed.** You're writing Python automation scripts directly. n8n would be redundant.

---

## Hosting Options Comparison

| Option | Pros | Cons | Best For |
|--------|------|------|----------|
| **Modal (Current)** | Serverless, scales automatically, webhooks built-in, Python-native | Requires code deployment | Event-driven automations, client webhooks |
| **VPS (DigitalOcean/Linode)** | Full control, always-on | Requires DevOps, manual scaling, $20-100/mo | Long-running processes, custom configs |
| **AWS Lambda** | Pay-per-use, massive scale | Complex setup, cold starts | Occasional automations |
| **Render/Railway** | Easy deploy, Git integration | More expensive than VPS | Simple apps, quick deploys |
| **Local Machine** | Free, full control | Not reliable for clients | Development only |

**Recommendation:** Stick with **Modal** for production client work. Use local machine for development/testing.

---

## Modal Setup (What You Already Have)

You already have Modal configured! Check your `AGENTS.md`:

```markdown
## Cloud Webhooks (Modal)

The system supports event-driven execution via Modal webhooks.

**Endpoints:**
- `https://nick-90891--claude-orchestrator-list-webhooks.modal.run` - List webhooks
- `https://nick-90891--claude-orchestrator-directive.modal.run?slug={slug}` - Execute directive
```

**This is PERFECT for your use case.** Here's why:

### ✅ Advantages for Your Business

1. **No server management** - Modal handles infrastructure
2. **Auto-scaling** - Handles 1 client or 100 clients without changes
3. **Event-driven** - Perfect for form submissions, webhooks, scheduled jobs
4. **Python-native** - Your execution scripts run directly
5. **Cheap** - Only pay when code runs (free tier: 30 hours/month)
6. **Slack integration** - Already streams to Slack in real-time

### How It Works

```python
# Your execution script (e.g., live_demo_automation.py)
# Runs on Modal when triggered by webhook

# Client fills out form → Webhook fires → Modal runs your script
# Script: Creates invoice → Sends email → Logs to Sheet
```

---

## Architecture for Client Automations

### Pattern 1: Webhook-Triggered (Most Common)
```
Client Form/Event → n8n Webhook (optional) → Modal Function → Your Python Script
```

**Example:** Remy Lasers order form
- Microsoft Form submitted
- Webhook URL triggers Modal
- `execution/live_demo_automation.py` runs
- Creates QB invoice, shipping label, email

**No VPS needed.** Modal handles everything.

### Pattern 2: Scheduled Jobs
```
Modal Cron → Your Python Script → Client Dashboard Updates
```

**Example:** Monthly insights report
- Modal cron runs daily at 6 AM
- `execution/generate_monthly_insights.py` runs
- Generates PDF, sends to client

**No VPS needed.** Modal has built-in cron.

### Pattern 3: API Endpoints
```
Client System → Your API (Modal) → Business Logic → Return Data
```

**Example:** Real-time lead scoring
- Client CRM calls your API
- Modal runs `execution/lead_research_orchestrator.py`
- Returns scored leads as JSON

**No VPS needed.** Modal serves HTTP endpoints.

---

## When You WOULD Need a VPS

You only need a VPS if:

1. **Always-on dashboard** - Public-facing website needs 24/7 uptime
2. **Database server** - Postgres/MySQL that clients query directly
3. **WebSocket server** - Real-time bidirectional communication
4. **Custom protocols** - Non-HTTP services (MQTT, gRPC, etc.)

For YOUR business model (automations for clients), **Modal is superior** because:
- Automations run on-demand (not 24/7)
- Each client's automation is isolated
- You don't pay for idle time
- No security patches/maintenance

---

## Recommended Stack (No VPS)

### For Client Automations
- **Hosting:** Modal (serverless Python)
- **Triggers:** Webhooks, cron jobs, HTTP APIs
- **Storage:** Google Sheets (deliverables), `.tmp/` (intermediates)
- **Monitoring:** Slack notifications (already configured)

### For Your Public Website
- **Hosting:** Vercel/Netlify (free for static sites)
- **Domain:** 5cypressautomation.com
- **Backend:** Modal functions (if needed for forms)

### For Development/Testing
- **Local:** `node server.js` on localhost:3000
- **Testing:** `python execution/live_demo_automation.py`

---

## Migration Plan (If You Outgrow Modal)

If you hit Modal's limits (unlikely for first 50 clients), here's the path:

**Stage 1 (Now - 50 clients):** Modal + Google Sheets
- All automations on Modal
- Deliverables in Google Workspace
- Cost: ~$10-50/month

**Stage 2 (50-200 clients):** Modal + Database
- Move from Google Sheets to Postgres (Supabase)
- Still serverless on Modal
- Cost: ~$100-300/month

**Stage 3 (200+ clients):** Kubernetes + Microservices
- Only if you need custom infrastructure
- Hire DevOps engineer
- Cost: $1,000+/month + engineer salary

You're at **Stage 1**. Stay there until revenue justifies Stage 2.

---

## Action Items

### Immediate (This Week)
1. ✅ Confirm Modal is deployed: `modal token status`
2. ✅ Test existing webhook: Call your list-webhooks endpoint
3. ✅ Deploy `live_demo_automation.py` to Modal
4. ✅ Test end-to-end with sample order

### For Remy Lasers (First Client)
1. Create Modal function for their form webhook
2. Point Microsoft Forms webhook to Modal URL
3. Function calls `live_demo_automation.py`
4. Monitor via Slack notifications

### When You Need More
- **Scheduled jobs:** `@modal.cron("0 6 * * *")` decorator
- **Secrets:** `modal secret create` for API keys
- **Debugging:** `modal logs` shows function output

---

## Code Example: Modal Function

```python
# execution/modal_webhook.py (you already have this!)
import modal

app = modal.App("5-cypress-automation")

@app.function()
def handle_order_webhook(order_data: dict):
    """Process incoming order from Microsoft Forms."""
    from live_demo_automation import LiveDemoAutomation
    
    demo = LiveDemoAutomation()
    results = demo.run_full_demo(order_data)
    
    return {"status": "success", "results": results}

@app.local_entrypoint()
def main():
    # Test locally
    test_order = {
        "customer_name": "Test Customer",
        "customer_email": "test@example.com",
        "product": "Laser XL",
        "quantity": 1,
        "price": 2499.00
    }
    result = handle_order_webhook.remote(test_order)
    print(result)
```

Deploy: `modal deploy execution/modal_webhook.py`

---

## Bottom Line

**You don't need a VPS.** Your architecture is already optimal:

- ✅ Python scripts for logic (deterministic)
- ✅ Modal for hosting (serverless, scalable)
- ✅ Google Workspace for deliverables (client-accessible)
- ✅ Slack for monitoring (real-time alerts)

**Focus on clients, not infrastructure.** Modal handles everything you need until you're at $50K+ MRR.

The only thing you need to add is credentials to `.env`:
```bash
MODAL_TOKEN=your_token
QBO_CLIENT_ID=your_qb_sandbox_key
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your_email
```

Then deploy and ship.
