# One-Time SEO Intelligence Report ($49)

**Skill Location:** See `.claude/skills/5-cypress-premium-seo/` for complete technical documentation, setup guides, and revenue models.

## Overview
A low-friction, high-value entry point for SMBs to receive a professional SEO audit. Serves as a "Tripwire" offer to convert prospects into long-term monthly retainers.

This directive documents the **5 Cypress implementation** of the Premium SEO Skill. For white-label or self-serve deployments, refer to the skill's SETUP.md and PRICING_MODELS.md.

**Architecture: Cloudflare Pages Functions only (no Railway/server.js)**

## Product Tiers
- **Free Scan**: Performance score, on-page issues, Core Web Vitals — no email required.
- **Premium Report ($49)**: Expert AI analysis (GPT-4o-mini) of every finding, copy-paste AI fix prompts per issue, keyword intelligence, backlink profile, competitive landscape, and a 90-day priority roadmap. Export as PDF via browser print.

## Key Files

| File | Purpose |
|------|---------|
| `public/seo-dashboard.html` | Free scan wizard + premium upsell |
| `public/seo-report.html` | Premium report display page (fetches from API) |
| `functions/api/seo/analyze.js` | DataForSEO + PageSpeed audit runner; saves to KV; returns audit_id |
| `functions/api/seo/checkout.js` | Creates $49 Stripe Checkout Session; stores pending session in KV |
| `functions/api/seo/webhook.js` | Handles checkout.session.completed; triggers OpenAI enrichment; saves report to KV |
| `functions/api/seo/report.js` | Payment-gated report API; admin bypass available |
| `functions/lib/seo-enrich.js` | OpenAI GPT-4o-mini enrichment utility (not a public endpoint) |

## KV Schema (SEO_AUDITS_KV — binding id: adb56962135c4b6c8e610202123121ed)

| Key | Value | TTL |
|-----|-------|-----|
| `audit:{domain}:{timestamp}` | Full analyze.js response JSON | 30 days |
| `session:{stripe_session_id}` | `{domain, email, audit_id, status: 'pending'\|'paid'}` | 30 days |
| `report:{stripe_session_id}` | Enriched report JSON (enriched + raw_audit) | 30 days |

## Workflow

### 1. Free Scan
- User enters URL on `seo-dashboard.html` (no email required)
- Frontend POSTs to `POST /api/seo/analyze` → runs PageSpeed + DataForSEO on-page
- Response includes `audit_id` (saved to KV) stored in `state.auditId`
- Dashboard displays scores + issues; shows premium upsell panel

### 2. Payment
- User enters email and clicks "Get Full Report — $49"
- Frontend POSTs `{domain, email, audit_id}` to `POST /api/seo/checkout`
- Function creates $49 Stripe Checkout Session and saves `session:{id}` pending to KV
- User redirected to Stripe; on success → `/seo-report.html?session_id={id}&domain={domain}`

### 3. Report Generation (Post-Payment)
- Stripe sends `checkout.session.completed` webhook to `POST /api/seo/webhook`
- Webhook verifies HMAC-SHA256 signature, marks session paid, fetches audit from KV
- Calls `enrichReport()` from `functions/lib/seo-enrich.js` → GPT-4o-mini
- Saves enriched report to `report:{session_id}` in KV

### 4. Report Display
- `seo-report.html` polls `GET /api/seo/report?session_id={id}` every 5 seconds
- Returns 202 while enrichment is running, 200 when ready
- Renders: 4 score gauges, grade badge, AI executive summary, quick wins, findings with expert explanation + AI prompt per issue, vitals, keywords, backlinks, competitors, 90-day roadmap, AI Prompts Hub
- "Export PDF" button → `window.print()` with `@media print` styles

### 5. Admin Bypass
- Admin header: `Authorization: Basic {b64(ADMIN_USER:ADMIN_PASS)}`
- `report.js` skips payment check; runs enrichment inline for any domain
- Use `/seo-report.html?session_id=admin_test&domain=example.com` after running a scan

### 6. Upsell
- Report CTA: "Book a Free Strategy Call" → Calendly link
- Follow up for monthly retainer conversation

## Required Environment Secrets (Cloudflare Pages Dashboard)

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | GPT-4o-mini enrichment (~$0.005-0.01/report) |
| `STRIPE_SECRET_KEY` | Stripe checkout session creation |
| `STRIPE_WEBHOOK_SECRET` | Stripe signature verification |
| `ADMIN_USER` | Admin username for bypass |
| `ADMIN_PASS` | Admin password for bypass |
| `GOOGLE_PAGESPEED_API_KEY` | Google PageSpeed API |
| `DATAFORSEO_USERNAME` | DataForSEO API username/email |
| `DATAFORSEO_PASSWORD` | DataForSEO API password |
| `CALENDLY_URL` | (Optional) Fallback if Stripe not configured |

## Stripe Webhook Registration (after deploy)

```
Stripe Dashboard → Webhooks → Add endpoint
URL: https://www.5cypress.com/api/seo/webhook
Event: checkout.session.completed
```

Copy the webhook signing secret → set as `STRIPE_WEBHOOK_SECRET` in Cloudflare.

## OpenAI Enrichment Output Schema

```json
{
  "executive_summary": "Two-paragraph business-focused analysis...",
  "overall_grade": "A|B|C|D|F",
  "findings": [
    {
      "id": "meta_description",
      "category": "On-Page|Technical|Speed|Keywords|Backlinks",
      "check": "Meta Description",
      "status": "Fail|Warning|Pass",
      "value": "Missing",
      "expert_explanation": "Plain-English explanation of why this matters...",
      "priority": "High|Medium|Low",
      "fix_recommendation": "Specific actionable fix...",
      "ai_prompt": "Copy-paste prompt for ChatGPT/Claude to fix this issue..."
    }
  ],
  "quick_wins": ["Top 3-5 easiest wins..."],
  "roadmap": {
    "phase1": {"label": "Foundation", "focus": "Technical fixes", "tasks": ["..."]},
    "phase2": {"label": "Content & Authority", "focus": "Growth", "tasks": ["..."]},
    "phase3": {"label": "Scale", "focus": "Compound returns", "tasks": ["..."]}
  },
  "keyword_strategy": "Insight paragraph...",
  "backlink_insight": "Insight paragraph..."
}
```

## Pricing History
- Originally: $50 (inconsistent)
- Standardized: **$49** everywhere (Stripe unit_amount: 4900, all UI, schema markup)

## Error Handling
- Stripe not configured → 402 with `fallback: 'calendly'` — frontend flips to Calendly CTA
- OpenAI enrichment fails → stores fallback report with manual-review message, still returns 200
- Webhook unreceived → report.js returns 202 until report appears in KV (max 2 min polling)
- Session not found → 404 with "link expired" message

- Triggers `directives/discovery_call.md`.

## Technical Implementation
- **Tool**: `execution/seo_audit_runner.py`
- **Database**: `platform.db` table `seo_audits`
- **Payment**: Stripe API (Node.js)
- **Email**: Follow-up email via `send_email` tool with PDF attachment if possible.

## Edge Cases
- **Payment Failure**: Return to dashboard with error toast.
- **Duplicate Audit**: Check if same domain was audited in last 24h, offer "View Existing" if paid.
- **Invalid URL**: Frontend validation for TLD and connectivity.
