# Admin Production Handoff (Railway + Cloudflare)

This runbook deploys the admin/API server to Railway and maps it to `admin.5cypress.com` while keeping the marketing site on Cloudflare Pages.

## 1) Deploy Node API to Railway

1. Push current branch to GitHub.
2. In Railway: New Project → Deploy from GitHub Repo.
3. Select this repository and deploy.
4. Confirm Railway detects [railway.json](railway.json) and starts `node server.js`.
5. Verify health endpoint from Railway domain:
   - `https://<railway-app-domain>/health`

Expected: JSON with `status: ok`.

## 2) Configure Railway Environment Variables

Set these in Railway Project Variables:

- `NODE_ENV=production`
- `PORT=3000`
- `ADMIN_USER=<strong-username>`
- `ADMIN_PASS=<strong-password>`
- `GOOGLE_PAGESPEED_API_KEY=<your-pagespeed-key>`
- `MARKETING_TEAM_PATH=/app/marketing-team` (recommended for container default consistency)

Optional (only if Stripe flow is needed on this host):

- `STRIPE_SECRET_KEY=...`
- `STRIPE_WEBHOOK_SECRET=...`
- `STRIPE_SUCCESS_URL=https://www.5cypress.com/seo-report.html?paid=true`
- `STRIPE_CANCEL_URL=https://www.5cypress.com/seo-dashboard.html`

## 3) Add Custom Domain in Railway

1. Railway service → Settings → Networking → Custom Domains.
2. Add: `admin.5cypress.com`.
3. Copy the target hostname Railway provides (usually a `*.up.railway.app` target).

## 4) Create DNS Record in Cloudflare

In Cloudflare DNS for `5cypress.com`:

- Type: `CNAME`
- Name: `admin`
- Target: `<railway-custom-domain-target>`
- Proxy status: **DNS only** (gray cloud) for first validation pass
- TTL: Auto

After TLS/traffic is stable, you can switch to proxied if desired.

## 5) Validate Auth + Endpoints

Use the verification script in [scripts/verify_admin_deploy.ps1](scripts/verify_admin_deploy.ps1):

- `pwsh -File .\scripts\verify_admin_deploy.ps1 -BaseUrl "https://admin.5cypress.com" -AdminUser "<user>" -AdminPass "<pass>"`

It validates:

- `/health`
- `/admin/`
- `/admin/clients`
- `/admin/seo`
- `/api/admin/clients`
- `/api/admin/seo-audit` (when `-TestSeoAudit` is provided)

## 6) Post-Go-Live Checks

- Open `https://admin.5cypress.com/admin/` and confirm basic-auth prompt.
- Open client list page and confirm it renders.
- Run one SEO audit from the admin page.
- Confirm no 5xx errors in Railway logs.

## 7) Rollback Plan

If deployment regresses:

1. In Railway, redeploy last healthy deployment.
2. Keep DNS record unchanged.
3. Re-run verification script.

## Notes

- The server now uses cross-platform default pathing for marketing data (`/app/marketing-team` equivalent) if `MARKETING_TEAM_PATH` is not provided.
- Existing Cloudflare Pages public site is unchanged; this setup only adds a dedicated admin/API origin.
