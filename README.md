# 5Cypress Data Analytics

> Management dashboards for owner-led businesses with financial and operational data scattered
> across QuickBooks, CRMs, and spreadsheets. See `CLAUDE.md` for full positioning and strategy —
> that file is canonical; this README and `AGENTS.md` are kept in sync with it.

**Live site:** [https://www.5cypress.com](https://www.5cypress.com)
**Contact:** info@5cypress.com (generic inbound, the only address presented publicly) / jimmy@5cypress.com (founder direct)

---

## Canonical Surfaces

This repo contains **two separate, unrelated systems**. Do not mix them up.

| Surface | What it is | Where it runs |
|---------|-----------|----------------|
| **`web/`** | The canonical marketing site (5cypress.com). Astro project, static build. | Cloudflare Pages, built from `web/dist` |
| **`functions/api/contact.ts`** | The live site's fit-call form handler (Cloudflare Pages Function + Resend). | Deploys alongside `web/dist` |
| `public/` | Legacy pre-Astro static site ("5 Cypress Automation" branding, 10-automation catalog, Free SEO Scan). **Not deployed by the current Cloudflare Pages config. Do not edit for marketing-site work.** | Not deployed |
| `server.js` / `routes/` / `db.js` / `platform.db` | Legacy Express app: admin dashboard, GigClock time-tracking SaaS, SEO-report tool, older lead-capture API. Historically deployed to a DigitalOcean droplet (see Production Infrastructure below) — confirm that box is still live before treating any of this as production. | DigitalOcean (if still active) |

If the task is "change something on 5cypress.com," it's a `web/src/` change. Everything else in
this table is dormant unless a task explicitly names it.

---

## Deploying the marketing site (`web/`)

```bash
# From repo root — builds web/ and deploys web/dist to Cloudflare Pages
npm run deploy

# Or manually:
cd web
npm run build
npx wrangler pages deploy dist
```

Cloudflare Pages config: `wrangler.toml` at repo root (`pages_build_output_dir = "web/dist"`).

---

## Legacy Express App — Production Infrastructure

This section describes the **separate legacy backend** (`server.js`), not the marketing site.

| Component | Details |
|-----------|---------|
| **Host** | DigitalOcean Ubuntu 22.04 LTS |
| **IP** | `134.199.192.11` |
| **Process Manager** | PM2 (`pm2 status`) |
| **Web Server** | Nginx (reverse proxy to port 8000) |
| **SSL** | Let's Encrypt via Certbot (auto-renews) |
| **CDN** | Cloudflare (proxy active) |
| **Database** | SQLite at `/home/jimmy/5cypress/platform.db` |
| **Runtime** | Node.js v20, Python 3.10 (venv) |

### Quick Reference - SSH & Deploy

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

### Admin Dashboard (Basic Auth required)
- `/admin` - Main admin panel
- `/admin/seo.html` - SEO audit management
- `/admin/leads.html` - Lead pipeline

### Key API Endpoints (legacy Express app)
- `POST /api/seo/analyze` - Free SEO scan *(off-ICP, parked — see CLAUDE.md)*
- `POST /api/seo/checkout` - Stripe checkout for premium report
- `POST /api/webhooks/stripe` - Stripe payment webhook
- `POST /api/webhooks/calendly` - Calendly booking webhook

**Before accepting real payments:** Switch Stripe keys from `sk_test_` to `sk_live_` in the Stripe Dashboard, then re-run `execution/register_stripe_webhook.py` to get a new webhook secret, and redeploy `.env`.

### Daily Backup

SQLite database backed up nightly at 2am via cron:

```bash
# View schedule
crontab -l

# Manual backup
cp /home/jimmy/5cypress/platform.db /home/jimmy/backups/platform_$(date +%F).db
```

### Maintenance

```bash
# Nginx
sudo nginx -t && sudo systemctl reload nginx

# SSL renewal (runs automatically, but manual test)
sudo certbot renew --dry-run

# View errors
pm2 logs 5cypress --err --lines 100
```

---

## Project Structure

```
web/                   # CANONICAL live marketing site (Astro → Cloudflare Pages)
functions/api/         # Cloudflare Pages Functions for the live site (contact form, etc.)

server.js              # LEGACY Express app (admin, GigClock, SEO tool) — not the marketing site
db.js                  # SQLite database helpers for the legacy app
public/                # LEGACY static frontend — do not edit for marketing-site work
  admin/               # Admin dashboard pages (Basic Auth protected)
execution/             # Python automation scripts (legacy app + client directives)
directives/            # SOP markdown files - workflow instructions
config/                # pricing.json, clients.json
clients/               # Per-client configs and history
marketing-team/        # AI marketing team deliverables
.claude/               # AI context, skills, commands
```

---

## Integrations

| Service | Status | Purpose |
|---------|--------|---------|
| Resend | Active | Transactional email — marketing site fit-call form (`functions/api/contact.ts`) |
| Cloudflare Turnstile | Active (graceful skip if unset) | Spam protection on the fit-call form |
| Stripe | Active (test mode) | Payment processing — legacy Express app only |
| Calendly | Active | Booking webhooks — legacy Express app |
| OpenAI | Active | SEO report generation — legacy Express app, off-ICP/parked |
| DataForSEO | Active | SEO data — legacy Express app, off-ICP/parked |
| Perplexity | Active | Web research — legacy Express app, off-ICP/parked |
| Telegram | Active | Internal notifications — legacy Express app |

---

## Environment Variables

Copy `.env.example` and fill in your values. Never commit `.env`.

**Marketing site (`web/`, via Cloudflare Pages secrets):**
```
RESEND_API_KEY=re_...
TURNSTILE_SECRET=...        # optional — form works without it, just skips verification
RATE_LIMIT=...              # optional KV namespace binding
```

**Legacy Express app (repo root `.env`):**
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

## Automation Scripts (execution/) — legacy Express app

Activate the Python venv on the server, then run:

```bash
source /home/jimmy/5cypress/venv/bin/activate
python execution/<script>.py
```

| Category | Scripts |
|----------|---------|
| SEO *(off-ICP, parked)* | seo_audit_runner.py, seo_outreach_prepper.py |
| Invoicing | create_qbo_invoice.py, create_invoice.py |
| Shipping | create_shipping_order.py |
| Leads | lead_research_orchestrator.py |
| Proposals | create_proposal.py |
| Reports | generate_monthly_insights.py |
| Onboarding | onboard_client.py |

---

## 3-Layer Architecture

1. **Directives** (`directives/`) - Markdown SOPs that define workflow goals
2. **Orchestration** (AI / Claude) - Intelligent routing and decision-making
3. **Execution** (`execution/`) - Deterministic Python scripts that do the work

See `CLAUDE.md` (canonical) or `AGENTS.md` for full agent instructions.
