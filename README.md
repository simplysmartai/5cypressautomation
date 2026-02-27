# 5 Cypress Automation

> AI-powered marketing and business automation services for small B2B companies.

**Live site:** [https://www.5cypress.com](https://www.5cypress.com)
**Contact:** nick@5cypress.com

---

## Production Infrastructure

| Component | Details |
|-----------|---------|
| **Host** | DigitalOcean Ubuntu 22.04 LTS |
| **IP** | `134.199.192.11` |
| **Process Manager** | PM2 (`pm2 status`) |
| **Web Server** | Nginx (reverse proxy to port 8000) |
| **SSL** | Let''s Encrypt via Certbot (auto-renews) |
| **CDN** | Cloudflare (proxy active) |
| **Database** | SQLite at `/home/jimmy/5cypress/platform.db` |
| **Runtime** | Node.js v20, Python 3.10 (venv) |

---

## Quick Reference - SSH & Deploy

```bash
# SSH into server
ssh jimmy@134.199.192.11

# Check app status
pm2 status
pm2 logs 5cypress --lines 50

# Deploy new code
git pull && pm2 restart 5cypress --update-env

# Update environment variables only
scp .env jimmy@134.199.192.11:/home/jimmy/5cypress/.env
ssh jimmy@134.199.192.11 "pm2 restart 5cypress --update-env"
```

---

## Project Structure

```
server.js              # Main Express app (all routes, API, webhooks)
db.js                  # SQLite database helpers
public/                # Static frontend (HTML, CSS, JS)
  admin/               # Admin dashboard pages (Basic Auth protected)
execution/             # Python automation scripts
directives/            # SOP markdown files - workflow instructions
config/                # pricing.json, clients.json
clients/               # Per-client configs and history
marketing-team/        # AI marketing team deliverables
.claude/               # AI context, skills, commands
```

---

## Services Live at 5cypress.com

### Customer-Facing Pages
- `/` - Homepage
- `/seo-audit.html` - Free SEO scan + $49 premium report
- `/booking.html` - Calendly booking page
- `/services.html` - Services overview
- `/pricing.html` - Pricing page

### Admin Dashboard (Basic Auth required)
- `/admin` - Main admin panel
- `/admin/seo.html` - SEO audit management
- `/admin/leads.html` - Lead pipeline

### Key API Endpoints
- `POST /api/seo/analyze` - Run free SEO scan
- `POST /api/seo/checkout` - Stripe checkout for premium report
- `POST /api/webhooks/stripe` - Stripe payment webhook
- `POST /api/webhooks/calendly` - Calendly booking webhook

---

## Integrations

| Service | Status | Purpose |
|---------|--------|---------|
| Stripe | Active (test mode) | Payment processing for SEO reports |
| Calendly | Active | Booking webhooks |
| OpenAI | Active | SEO report generation |
| Resend | Active | Transactional email |
| DataForSEO | Active | SEO data and SERP analysis |
| Perplexity | Active | Web research for reports |
| Telegram | Active | Internal notifications |

**Before accepting real payments:** Switch Stripe keys from `sk_test_` to `sk_live_` in the Stripe Dashboard, then re-run `execution/register_stripe_webhook.py` to get a new webhook secret, and redeploy `.env`.

---

## Environment Variables

Copy `.env.example` and fill in your values. Never commit `.env`.

```
PORT=8000
ENVIRONMENT=production
FRONTEND_URL=https://5cypress.com
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHER_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
OPENAI_API_KEY=sk-...
RESEND_API_KEY=re_...
CALENDLY_API_KEY=...
```

---

## Automation Scripts (execution/)

Activate the Python venv on the server, then run:

```bash
source /home/jimmy/5cypress/venv/bin/activate
python execution/<script>.py
```

| Category | Scripts |
|----------|---------|
| SEO | seo_audit_runner.py, seo_outreach_prepper.py |
| Invoicing | create_qbo_invoice.py, create_invoice.py |
| Shipping | create_shipping_order.py |
| Leads | lead_research_orchestrator.py |
| Proposals | create_proposal.py |
| Reports | generate_monthly_insights.py |
| Onboarding | onboard_client.py |

---

## Daily Backup

SQLite database backed up nightly at 2am via cron:

```bash
# View schedule
crontab -l

# Manual backup
cp /home/jimmy/5cypress/platform.db /home/jimmy/backups/platform_$(date +%F).db
```

---

## 3-Layer Architecture

1. **Directives** (`directives/`) - Markdown SOPs that define workflow goals
2. **Orchestration** (AI / Claude) - Intelligent routing and decision-making
3. **Execution** (`execution/`) - Deterministic Python scripts that do the work

See `CLAUDE.md` or `AGENTS.md` for full agent instructions.

---

## Maintenance

```bash
# Nginx
sudo nginx -t && sudo systemctl reload nginx

# SSL renewal (runs automatically, but manual test)
sudo certbot renew --dry-run

# View errors
pm2 logs 5cypress --err --lines 100
```
