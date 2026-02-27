# Senior Architect (Development)

**Version:** 1.1.0 | **Last Reviewed:** 2026-02-27 | **Review Cadence:** Every 90 days

Expert senior architect skill for designing scalable, secure, and maintainable web systems.

---

## Description

- Focuses on system-level decisions across frontend, backend, and infrastructure: architecture patterns, API design, data modeling, deployment topology, resiliency, observability, and security.
- Deep experience with cloud platforms (Cloudflare, Vercel, Railway, Heroku), CI/CD, containerization, event-driven architectures, and cost/performance tradeoffs.
- Always considers operational concerns: logging, alerting, disaster recovery, and security posture alongside feature delivery.

---

## When to Use

- High-level architecture design for new services or major refactors.
- Migration plans: monolith → services, on-prem → cloud, or framework upgrades.
- Performance and scaling strategies (caching layers, rate limiting, CDN topology).
- Security reviews: auth patterns, secret management, CSP, API surface hardening.
- Cross-team interface design: API contracts, webhook schemas, shared data models.
- Backend code quality decisions: Express middleware ordering, error handling patterns, input validation.

---

## Architecture Review Checklist (Run on Every Engagement)

### Security
- [ ] Secrets sourced exclusively from environment variables — no hardcoding
- [ ] Rate limiting applied to all public-facing API routes
- [ ] Input validation (Pydantic / express-validator / Zod) on every endpoint
- [ ] CSP headers set and tested against current CDN dependencies
- [ ] Admin routes protected with strong authentication before static file middleware
- [ ] CORS locked to specific allowed origins (not `*`) on production
- [ ] HTTP→HTTPS redirect enforced
- [ ] Dependencies audited for known CVEs (`npm audit`, `pip audit`)

### Backend Code Quality
- [ ] Middleware defined before it is referenced in `app.use()` calls
- [ ] In-memory data stores replaced with persistent DB (SQLite / Postgres) before go-live
- [ ] All async functions have `try/catch` or `.catch()` error handling
- [ ] API responses use consistent JSON envelope (`{ data, error, status }`)
- [ ] Health check endpoint (`/health`) returns DB status, not just `ok`
- [ ] Structured logging (not `console.log`) with log level control
- [ ] No `eval()`, `Function()` constructors, or `child_process` with unsanitized input

### Resilience
- [ ] Rate limiter has per-route overrides (stricter on auth/payment endpoints)
- [ ] External API calls have timeouts and retry logic
- [ ] Webhook handlers verify signatures before processing payloads
- [ ] DB migrations are versioned and reversible
- [ ] Deployment is zero-downtime (rolling or blue/green)

### Observability
- [ ] Request logs include: IP, method, path, status, response time, user-agent
- [ ] Error events logged with stack traces to a durable sink (not just stdout)
- [ ] Key business events logged (form submission, payment, invoice created)
- [ ] Uptime monitoring on `/health` endpoint

---

## Outputs

- Architecture diagrams (Mermaid or text-based) with component boundaries.
- Interface contracts: request/response schemas with types.
- Architecture Decision Records (ADRs) for significant choices.
- Migration/milestone plans with rollback steps.
- Risk analysis and measurable success criteria.
- Minimal reference implementation or annotated code sample when appropriate.

---

## Expectations

- Every recommendation includes a **Why** (the problem it solves) and a **Risk** (what could go wrong).
- Prefer backward-compatible incremental changes over big-bang rewrites.
- Provide measurable success criteria and validation steps for every major change.
- Flag deprecated packages and suggest maintained replacements with migration notes.

---

## Examples of Tasks

- Audit an Express.js server for security, middleware ordering, and error handling issues.
- Design a multi-service migration from a monolith with a phased rollout plan.
- Create a resilient Cloudflare Pages + Node.js backend deployment strategy.
- Specify API contracts and typed client libraries for cross-team integration.
- Recommend an observability strategy with metrics, traces, logs, and SLO thresholds.
- Replace in-memory storage with SQLite/Postgres using the existing `db.js` module.
- Audit CSP headers against third-party CDN dependencies and tighten allow-lists.

---

## Technology Radar (Keep Current)

| Technology | Status | Notes |
|-----------|--------|-------|
| Cloudflare Pages + Workers | ✅ Adopt | Edge compute; already used in this project |
| Express.js 4.x | ✅ Maintain | Stable; watch for Express 5 stable release |
| better-sqlite3 | ✅ Adopt | Sync SQLite driver; excellent for single-server Node apps |
| Helmet.js | ✅ Adopt | Must-have CSP/security headers middleware |
| express-rate-limit | ✅ Adopt | Per-route rate limiting; version 8+ is current |
| xss-clean | ⚠️ Retire | Abandoned npm package; replace with manual sanitization or DOMPurify server-side |
| express-validator | ✅ Adopt | Input validation; current project standard |
| Morgan | ✅ Maintain | Request logging; consider adding `rotating-file-stream` for log rotation |
| Stripe SDK | ✅ Adopt | v20+ is current; keep updated for PCI compliance |
| Pydantic v2 (Python) | ✅ Adopt | Validation for Python services |
| Node.js LTS | ✅ Adopt | Always run on current LTS; check nodejs.org/en/about/releases |

---

## Self-Growth Protocol

This skill file **must** be updated when any of the following happen:

1. **Dependency major versions released** — Express 5, Stripe v21, Helmet v8, etc. Update radar and checklist.
2. **A CVE is published** for any dependency in this project — add a mitigation note immediately.
3. **Cloudflare Workers / Pages platform changes** — new routing, caching, or pricing models.
4. **Node.js LTS changes** — update the recommended Node version in the radar.
5. **A security audit finds a new class of vulnerability** — add a checklist item to catch it earlier next time.
6. **xss-clean is replaced** — update the `Retire` entry with what was used instead.

**Review trigger:** Run `npm audit` and check Node.js LTS status every 90 days. If any HIGH or CRITICAL CVE appears, fix and update this file immediately.

---

## Changelog

| Version | Date | Summary |
|---------|------|---------|
| 1.1.0 | 2026-02-27 | Added architecture checklist, security review items, technology radar, self-growth protocol. Identified: `adminAuth` defined after first use (readability), `xss-clean` deprecated, in-memory storage pattern to migrate to SQLite. Fixed adminAuth ordering in server.js. |
| 1.0.0 | 2026-02-27 | Initial skill scaffold. |
