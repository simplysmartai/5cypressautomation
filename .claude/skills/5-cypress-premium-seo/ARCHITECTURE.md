# Architecture — 5 Cypress Premium SEO Skill

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                  PUBLIC FRONT-END                           │
├─────────────────────────────────────────────────────────────┤
│  /seo-dashboard.html    ← Free scan entry point             │
│  /seo-report.html       ← Report viewer (polling, PDF print)│
└─────────────────────────────────────────────────────────────┘
          ↓                          ↓
┌──────────────────────────┐  ┌──────────────────────────┐
│  /api/seo/analyze        │  │  /api/seo/report         │
│  (scan, save audit to KV)│  │  (fetch enriched report) │
└──────────────────────────┘  └──────────────────────────┘
          ↓
┌──────────────────────────┐
│ /api/seo/checkout        │
│ (create Stripe session)  │
└──────────────────────────┘
          ↓
┌──────────────────────────┐
│  Stripe Checkout         │
│  (client pays $49)       │
└──────────────────────────┘
          ↓
┌──────────────────────────────────────────────────┐
│  /api/seo/webhook                                │
│  (Stripe calls on payment success)               │
│  → fetch audit from KV                           │
│  → enrichReport() via seo-enrich.js              │
│  → save enriched report to KV as report:{id}    │
└──────────────────────────────────────────────────┘
          ↓
┌──────────────────────────────────────┐
│  Cloudflare KV Storage               │
│  (2 record types per audit):          │
│  - audit:{id} = raw crawl data        │
│  - report:{id} = enriched report + AI │
│  - session:{id} = payment state       │
└──────────────────────────────────────┘
          ↓
┌──────────────────────────────────────┐
│  /seo-report.html                    │
│  Polls /api/seo/report until ready   │
│  Renders: gauges, grade, findings    │
│  Supports: PDF export via print()    │
└──────────────────────────────────────┘
```

---

## 3-Layer Architecture

### Layer 1: DIRECTIVE
**"What to do"** — Written in Markdown, lives in `/directives/`

Files:
- `premium_seo_report_workflow.md` — End-to-end workflow, inputs, outputs, edge cases

Example:
```markdown
# Premium SEO Report Workflow

## Goal
Convert free scan → $49 payment → enriched report delivery

## Inputs
- domain: string (www.example.com)
- email: string (client@example.com)
- audit_id: string (returned from scan)

## Process
1. Client scans domain via /seo-dashboard → analyze.js returns audit_id
2. Client clicks $49 upsell → checkout.js creates Stripe session
3. Stripe confirmation → webhook.js triggered
4. Webhook enriches audit with OpenAI → saves to KV
5. Client redirected to /seo-report.html
6. Report page polls /api/seo/report until ready
7. Enriched report displays to client

## Outputs
- Payment: Stripe Session (approved/pending/failed)
- Report: JSON with expert_summary, findings[], roadmap, ai_prompts[]
- Storage: KV entries (audit:*, report:*, session:*)

## Edge Cases
- OpenAI timeout: return fallback with manual review message
- DataForSEO offline: return cached scan data
- KV quota exceeded: log error, inform user
```

### Layer 2: SKILL (This Folder)
**"How to build & deploy it"** — Setup guides, reusable patterns, documentation

Files:
- `SKILL.md` — Overview, metrics, revenue model
- `ARCHITECTURE.md` — You are here
- `SETUP.md` — Deploy to Cloudflare step-by-step
- `TESTING.md` — Test checklist + dry-run
- `PRICING_MODELS.md` — Revenue options
- `SUPPORT.md` — FAQ, troubleshooting
- `ENV.example` — Required env vars

### Layer 3: EXECUTION
**"Actually do the work"** — Code in `/functions/` and `/public/`

Files:
```
functions/
├── api/seo/
│   ├── analyze.js        ← DataForSEO crawl, save audit to KV
│   ├── checkout.js       ← Create Stripe Checkout Session
│   ├── report.js         ← Return enriched report (payment-gated)
│   └── webhook.js        ← Stripe confirmation, trigger enrichment
└── lib/
    └── seo-enrich.js     ← OpenAI GPT-4o-mini analysis

public/
├── seo-dashboard.html    ← Free scan interface
├── seo-report.html       ← Premium report viewer
└── styles-premium.css    ← Report styling
```

---

## Data Schema

### KV Namespace: `SEO_AUDITS_KV`

#### Record Type 1: Audit Data
```
Key: audit:{domain}:{timestamp}
Value:
{
  "data": {
    "title": "Page Title",
    "meta_description": "...",
    "h1": "...",
    "canonical": "...",
    "mobile_friendly": true,
    "robots_txt": "...",
    "sitemap_xml": "...",
    "performance_score": 85,
    "seo_score": 92,
    "accessibility_score": 88,
    "best_practices_score": 90,
    "web_vitals": {
      "lcp": { value: 1200, status: "good" },
      "ttfb": { value: 200, status: "good" },
      "cls": { value: 0.05, status: "good" }
    },
    "images": [ { src, alt, title } ],
    "links_internal": [...],
    "links_external": [...],
    "keywords_found": [ { keyword, frequency, density } ],
    "speed_opportunities": [ ... ]
  },
  "url": "https://example.com",
  "timestamp": 1708881234512
}
TTL: 2592000 (30 days)
```

#### Record Type 2: Enriched Report
```
Key: report:{session_id}
Value:
{
  "executive_summary": "Domain has strong SEO foundation...",
  "overall_grade": "A",
  "grade_letter": "A",
  "quick_wins": [
    "Add missing meta descriptions on 3 pages",
    "Compress images (avg 200KB → 50KB)"
  ],
  "findings": [
    {
      "id": "missing_meta_desc",
      "title": "Missing Meta Description",
      "description": "12 pages lack meta descriptions",
      "severity": "high",
      "expert_explanation": "Meta descriptions are HTML snippets...",
      "fix_recommendation": "Add 150-160 char descriptions mentioning target keyword",
      "priority": "high",
      "ai_prompt": "SEO expert reviewing page metatags:\n[copy-paste this prompt into ChatGPT for fix code]"
    }
  ],
  "core_web_vitals": { LCP, TTFB, CLS, FCP, TBT, SI },
  "keyword_strategy": "Your top opportunities: product pricing, integration guides",
  "backlink_insight": "Competitive analysis: 42 referring domains",
  "roadmap": {
    "phase_1": "Improve meta tags and page structure",
    "phase_2": "Content optimization for keywords",
    "phase_3": "Link building and topical authority"
  },
  "report_id": "report:{session_id}",
  "generated_at": 1708881234512,
  "domain": "example.com"
}
TTL: 2592000 (30 days)
```

#### Record Type 3: Checkout Session
```
Key: session:{stripe_session_id}
Value:
{
  "domain": "example.com",
  "email": "client@example.com",
  "audit_id": "example.com:1708881234512",
  "status": "pending",
  "created_at": 1708881234512,
  "expires_at": 1708967634512
}
TTL: 604800 (7 days — cleanup after payment confirmation)
```

---

## API Reference

### POST /api/seo/analyze
**Free scan endpoint**

Request:
```javascript
{
  "domain": "example.com",
  "email": "user@example.com"
}
```

Response (200):
```javascript
{
  "status": "success",
  "data": { /* DataForSEO audit object */ },
  "audit_id": "example.com:1708881234512"
}
```

### POST /api/seo/checkout
**Create $49 checkout session**

Request:
```javascript
{
  "domain": "example.com",
  "email": "user@example.com",
  "audit_id": "example.com:1708881234512"
}
```

Response (200):
```javascript
{
  "url": "https://checkout.stripe.com/...",
  "session_id": "cs_live_..."
}
```

Response (402, if no Stripe key):
```javascript
{
  "status": "setup_incomplete",
  "fallback": "calendly",
  "url": "https://calendly.com/..."
}
```

### POST /api/seo/webhook
**Stripe webhook (called by Stripe, not client)**

Request headers (from Stripe):
```
stripe-signature: t=1614556732,v1=...
```

Process:
1. Verify HMAC-SHA256 signature
2. On `checkout.session.completed`:
   - Fetch session from KV
   - Fetch audit from KV
   - Call `enrichReport(audit, env)` → OpenAI analysis
   - Save enriched report to KV as `report:{session_id}`
3. Return 200 OK

### GET /api/seo/report?session_id={id}&domain={domain}
**Fetch enriched report (payment-gated)**

Query params:
- `session_id` — Stripe session ID
- `domain` — Site domain (for validation)

Headers (optional, for admin bypass):
```
Authorization: Basic base64(ADMIN_USER:ADMIN_PASS)
```

Response (200 — ready):
```javascript
{
  "status": "ready",
  "report": { /* enriched report object */ }
}
```

Response (202 — processing):
```javascript
{
  "status": "processing",
  "message": "Analyzing with AI..."
}
```

Response (402 — unpaid):
```javascript
{
  "status": "unpaid",
  "message": "Payment not received"
}
```

Response (404 — not found):
```javascript
{
  "status": "not_found",
  "message": "Session not found"
}
```

---

## Error Handling

| Scenario | Code | Response |
|----------|------|----------|
| DataForSEO API offline | 200 | Return cached/fallback data |
| OpenAI timeout | 200 | Return report with "manual review pending" note |
| Stripe signature invalid | 400 | Log + return 400 (Stripe will retry) |
| KV quota exceeded | 507 | Log warning, continue (data lost for this session) |
| Missing API key | 402 | Return graceful fallback (Calendly) |
| Admin bypass incorrect | 401 | Return 401 Unauthorized |

---

## Performance Targets

| Operation | Target | Notes |
|-----------|--------|-------|
| Free scan (/api/seo/analyze) | <5 sec | DataForSEO API latency + browser time |
| Stripe checkout (/api/seo/checkout) | <1 sec | Creating session |
| Webhook (/api/seo/webhook) | <10 sec | Including OpenAI enrichment |
| Report fetch (/api/seo/report) | <500ms | KV lookup only |
| Report render (HTML) | <2 sec | DataViz + polling |

---

## Security

- **Stripe:** HMAC-SHA256 signature verification (Web Crypto API)
- **Admin:** Basic Auth HTTP header, base64 encoded
- **KV:** TTL-based auto-expiration (no manual cleanup needed)
- **Payment:** PCI compliance handled by Stripe (no card data stored)
- **APIs:** AllAPI keys stored in Cloudflare env vars (never committed)

---

**For setup, see `SETUP.md`. For tests, see `TESTING.md`.**
