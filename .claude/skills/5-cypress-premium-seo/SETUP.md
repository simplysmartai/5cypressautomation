# Setup Guide — Deploy Premium SEO Skill to Cloudflare Pages

## Prerequisites

- **Cloudflare account** with a Pages project
- **Git repository** with code already committed (this repo)
- **Stripe account** (test mode for development, live for production)
- **OpenAI API key** (GPT-4o-mini access)
- **DataForSEO API key** (SEO audit crawling)
- **Text editor** or VS Code

---

## Step 1: Prepare Your Cloudflare KV Namespace

The skill stores audits + reports in KV. You may have already created this in Phase 7, but verify:

```bash
# List all KV namespaces
npx wrangler kv:namespace list

# If SEO_AUDITS_KV doesn't exist, create it:
npx wrangler kv:namespace create "SEO_AUDITS_KV"
npx wrangler kv:namespace create "SEO_AUDITS_KV" --preview

# Copy the namespace ID (looks like: adb56962135c4b6c8e610202123121ed)
```

Add to `wrangler.toml` (if not already there):

```toml
[[kv_namespaces]]
binding = "SEO_AUDITS_KV"
id = "adb56962135c4b6c8e610202123121ed"
preview_id = "adb56962135c4b6c8e610202123121ed"
```

---

## Step 2: Add Environment Variables to Cloudflare Pages

Go to **Cloudflare Dashboard** → **Pages** → your project → **Settings** → **Environment variables**

Add **both Preview and Production**:

| Name | Value | Notes |
|------|-------|-------|
| `OPENAI_API_KEY` | `sk_...` | From openai.com/api-keys |
| `STRIPE_SECRET_KEY` | `sk_live_...` or `sk_test_...` | From stripe.com/dashboard |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` | From Step 3 (create webhook first) |
| `ADMIN_USER` | `your-username` | For free admin access |
| `ADMIN_PASS` | `strong-password` | For free admin access |

**Note:** Stripe and OpenAI keys are sensitive — use live keys for production, test keys for development. Set different values for Preview vs Production if needed.

---

## Step 3: Create Stripe Webhook (Once Deployed)

After you deploy to Cloudflare (Step 4), register the webhook:

**Stripe Dashboard** → **Developers** → **Webhooks** → **Add endpoint**

- **Endpoint URL:** `https://your-domain.com/api/seo/webhook`
- **Events to send:** Select `checkout.session.completed`
- **Click: Add endpoint**
- **Copy the signing secret** (starts with `whsec_`)

Add to Cloudflare env vars:
```
STRIPE_WEBHOOK_SECRET = whsec_...
```

---

## Step 4: Deploy to Cloudflare Pages

### Option A: Auto-Deploy (Recommended)
Cloudflare auto-deploys when you push to GitHub:

```bash
git add -A
git commit -m "deploy: SEO skill to production"
git push origin main
```

Cloudflare detects the push and builds automatically. Check **Pages** → **Deployments** for status.

### Option B: Manual Deploy
```bash
cd /path/to/project
npx wrangler pages deploy public --branch main
```

---

## Step 5: Redeploy After Adding Env Vars

Cloudflare Pages doesn't apply new env vars without a redeploy. After Step 2:

1. Go to **Pages** → **Deployments**
2. Find the latest deployment
3. Click **Retry deployment**

Or push a dummy commit:
```bash
git commit --allow-empty -m "trigger redeploy with env vars"
git push
```

---

## Step 6: Verify Deployment

### Check 1: Functions deployed
```bash
# Visit your site's functions
curl https://your-domain.com/api/seo/analyze -X POST \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com"}'

# Should return 200 with audit data (or error if DataForSEO key missing)
```

### Check 2: KV is working
```bash
curl https://your-domain.com/api/seo/report?session_id=test&domain=example.com \
  -H "Authorization: Basic $(echo -n 'your-username:strong-password' | base64)"

# Should return admin data (since you can bypass with Basic Auth)
```

### Check 3: Stripe is wired (optional, test mode)
Go to `https://your-domain.com/seo-dashboard`
- Run a free scan
- Click "Get Full Report — $49"
- Should redirect to Stripe Checkout (test mode)

---

## Step 7: Test End-to-End

### Test Flow (Using Admin Bypass)

1. **Run a free scan:**
```bash
curl https://your-domain.com/api/seo/analyze -X POST \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com","email":"test@example.com"}'

# Copy the audit_id from response
```

2. **Fetch as admin (bypasses payment check):**
```bash
curl https://your-domain.com/api/seo/report?session_id=admin&domain=example.com \
  -H "Authorization: Basic $(echo -n 'your-username:strong-password' | base64)"

# Returns enriched report (or 202 if still processing)
```

3. **Check report in browser:**
Visit `https://your-domain.com/seo-report.html?session_id=admin&domain=example.com`

4. **Test PDF export:**
Press `Ctrl+P` (or `Cmd+P` on Mac) → Print to PDF

### Test Flow (Using Stripe Test Mode)

1. Go to `https://your-domain.com/seo-dashboard`
2. Enter any domain (e.g., `example.com`)
3. Click "Run Free Scan"
4. Copy the `audit_id` from browser console (F12 → Console)
5. Click "Get Full Report — $49"
6. In Stripe checkout, use test card: `4242 4242 4242 4242`, any future date, any CVC
7. Complete checkout
8. Should redirect to `/seo-report.html?session_id=...&domain=...`
9. Check if report loads (might be 202 "processing" while OpenAI enriches)

---

## Step 8: Troubleshooting Deployment

### Issue: Functions not found (404)
- Check `functions/api/seo/` folder exists
- Verify file names match: `analyze.js`, `checkout.js`, `webhook.js`, `report.js`
- Redeploy: `git push` or `wrangler pages deploy`

### Issue: KV namespace not found
- Verify `wrangler.toml` has `[[kv_namespaces]]` block
- Check namespace ID is correct (`npx wrangler kv:namespace list`)
- Redeploy after updating `wrangler.toml`

### Issue: Env vars not working
- Confirm vars are added in **Settings** → **Environment variables** (both Preview + Production)
- Verify **both Preview and Production** have the same vars
- Redeploy: click **Retry deployment** on latest build
- Wait 1-2 min for env vars to be available

### Issue: Stripe webhook not firing
- Check **Stripe Dashboard** → **Developers** → **Webhooks** → select your endpoint
- Look for `checkout.session.completed` events
- If none, manually test: create a checkout session, pay with test card
- If webhook still doesn't fire, check the `stripe-signature` header validation in `webhook.js`

### Issue: OpenAI calls timing out
- Check `OPENAI_API_KEY` is valid (try `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`)
- Check if you've hit API rate limits or quota
- Increase timeout in `webhook.js` from 10s to 20s if needed

---

## Step 9: Production Checklist

Before going public with live Stripe keys:

- [ ] Test full flow end-to-end with Stripe test card
- [ ] Verify KV retention (audit + report storage)
- [ ] Confirm DataForSEO API is stable
- [ ] Test admin bypass works (`Authorization: Basic`)
- [ ] Check error handling (missing env vars, API timeouts)
- [ ] Monitor Cloudflare Analytics + error logs (Pages → Analytics)
- [ ] Switch Stripe to **live keys** (not test)
- [ ] Register live webhook URL in Stripe (different from test)
- [ ] Add `STRIPE_WEBHOOK_SECRET` for live (different from test)
- [ ] Test one paid report end-to-end
- [ ] Monitor Stripe Dashboard for failed payments/webhooks

---

## Step 10: Scaling Considerations

**Cloudflare Pages limits:**
- Free tier: up to 500 requests/day, 100 ms CPU per request
- Pro tier ($20/mo): unlimited requests, 50 ms CPU per request
- Workers paid: $0.50/million requests + $0.50/million KV reads

**For 10,000+ reports/month:** Consider upgrading to **Cloudflare Workers (paid)** for more CPU and KV throughput.

**Cost estimate (10,000 reports/month):**
- Cloudflare: $20-50/mo (if using Workers)
- Stripe: 2.9% × $49 × 10,000 = $14,210 revenue → $412 fee
- OpenAI: $0.008 × 10,000 = $80/mo
- DataForSEO: ~$5,000/mo (10,000 crawls × $0.50)
- **Gross margin:** $490,000 (revenue) - $5,560 (API costs) = 98.9%

---

**All set! You're now running the Premium SEO skill on Cloudflare. See `TESTING.md` for deeper test scenarios.**
