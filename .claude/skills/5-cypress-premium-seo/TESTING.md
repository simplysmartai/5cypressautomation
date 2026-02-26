# Testing Guide — Premium SEO Skill

Complete test checklist for the skill before going public.

---

## Pre-Deployment Tests

### 1. Function Syntax Check
```bash
# Check for syntax errors in all functions
npx wrangler pages dev public

# Should start without errors
# If errors appear, fix them in /functions/api/seo/*.js
```

### 2. Environment Variables Loaded
```bash
# Test that env vars are available to functions
curl http://localhost:8787/api/seo/analyze \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com"}'

# Should return 200 or error about missing DataForSEO key (not env var error)
```

### 3. KV Namespace Connection
```bash
# wrangler.toml should have:
# [[kv_namespaces]]
# binding = "SEO_AUDITS_KV"
# id = "..."

# Verify wrangler.toml syntax
cat wrangler.toml | grep -A 3 "kv_namespaces"
```

---

## Post-Deployment Tests

### Test 1: Free Scan Endpoint
**Purpose:** Verify `/api/seo/analyze` works and saves to KV

```bash
curl https://your-domain.com/api/seo/analyze \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"domain":"example.com","email":"test@example.com"}'

# Expected response:
# {
#   "status": "success",
#   "data": { /* audit object */ },
#   "audit_id": "example.com:1708881234512"
# }
```

**Verify:**
- [ ] Returns 200 with `audit_id`
- [ ] `audit_id` format: `{domain}:{timestamp}`
- [ ] Audit saved to KV (`audit:{audit_id}` key)

---

### Test 2: Checkout Endpoint
**Purpose:** Verify `/api/seo/checkout` creates Stripe session

```bash
curl https://your-domain.com/api/seo/checkout \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "domain":"example.com",
    "email":"test@example.com",
    "audit_id":"example.com:1708881234512"
  }'

# Expected response:
# {
#   "url": "https://checkout.stripe.com/...",
#   "session_id": "cs_live_..."
# }
```

**Verify:**
- [ ] Returns 200 with Stripe checkout URL
- [ ] Session stored in KV (`session:{session_id}` key)
- [ ] Session includes domain, email, audit_id, status='pending'

---

### Test 3: Webhook Endpoint
**Purpose:** Verify `/api/seo/webhook` processes Stripe events

**Manual test (using Stripe CLI):**
```bash
# Install Stripe CLI (https://stripe.com/docs/stripe-cli)
stripe listen --forward-to https://your-domain.com/api/seo/webhook

# In separate terminal:
stripe trigger checkout.session.completed

# Check webhook response logs
```

**Verify:**
- [ ] Webhook receives event (200 OK)
- [ ] HMAC signature verified correctly
- [ ] `checkout.session.completed` triggers enrichment
- [ ] Report saved to KV (`report:{session_id}` key)

---

### Test 4: Report Endpoint (Admin Bypass)
**Purpose:** Verify `/api/seo/report` returns enriched data

```bash
# Create Basic Auth token
echo -n "your_admin_username:your_admin_password" | base64
# Output: eW91cl9hZG1pbl91c2VybmFtZTp5b3VyX2FkbWluX3Bhc3N3b3Jk

curl "https://your-domain.com/api/seo/report?session_id=test&domain=example.com" \
  -H "Authorization: Basic eW91cl9hZG1pbl91c2VybmFtZTp5b3VyX2FkbWluX3Bhc3N3b3Jk"

# Expected response (if report is ready):
# {
#   "status": "ready",
#   "report": {
#     "executive_summary": "...",
#     "overall_grade": "A",
#     "findings": [{ expert_explanation, fix_recommendation, ai_prompt }, ...],
#     ...
#   }
# }

# Expected response (if still processing):
# {
#   "status": "processing",
#   "message": "Analyzing with AI..."
# }
```

**Verify:**
- [ ] Admin bypass works (with correct Basic Auth)
- [ ] Returns 200 with enriched report
- [ ] Report includes: executive_summary, grade, findings[], roadmap, ai_prompts
- [ ] Each finding has: expert_explanation, fix_recommendation, ai_prompt

---

### Test 5: Report Payment Gating (Without Admin)
**Purpose:** Verify `/api/seo/report` rejects unpaid sessions

```bash
# Request WITHOUT admin auth header
curl "https://your-domain.com/api/seo/report?session_id=fake_session&domain=example.com"

# Expected response:
# {
#   "status": "unpaid" or "not_found",
#   "message": "..."
# }
```

**Verify:**
- [ ] Returns 402 or 404 without valid auth
- [ ] Does NOT return enriched data to unpaid users

---

### Test 6: HTML Report Viewer
**Purpose:** Verify `/seo-report.html` loads and renders

**Open in browser:**
```
https://your-domain.com/seo-report.html?session_id=ADMIN_SESSION&domain=example.com
# With admin Authorization header in localStorage (or via browser dev tools)
```

**Verify:**
- [ ] Page loads without errors
- [ ] Polling spinner appears while fetching report
- [ ] Report renders with all sections:
  - [ ] 4 gauge cards (Performance, SEO, Accessibility, Best Practices)
  - [ ] Grade circle + Executive Summary
  - [ ] Quick Wins panel
  - [ ] Findings with expert explanations + AI prompts
  - [ ] Core Web Vitals grid
  - [ ] Speed Opportunities chart
  - [ ] Keywords panel (if keywords found)
  - [ ] Backlinks panel (if data available)
  - [ ] 90-Day Roadmap
  - [ ] AI Prompts Hub
- [ ] AI prompt "Copy" buttons work
- [ ] PDF export via `Ctrl+P` or `Cmd+P`

---

### Test 7: End-to-End (Stripe Test Mode)
**Purpose:** Complete flow from scan → payment → report

1. **Visit dashboard:**
   ```
   https://your-domain.com/seo-dashboard
   ```

2. **Run free scan:**
   - Enter domain: `example.com`
   - Click "Run Free Scan"
   - Verify scan completes (60 sec)
   - Check browser console (F12) for `audit_id`

3. **Click upsell:**
   - Click "Get Full Report — $49"
   - Should redirect to Stripe checkout

4. **Complete payment:**
   - Use test card: `4242 4242 4242 4242`
   - Any future expiry date
   - Any CVC
   - Click "Pay"

5. **Verify redirect:**
   - Should redirect to `/seo-report.html?session_id=...&domain=example.com`
   - Report should load (may show "processing" for 10-30 sec while OpenAI enriches)

6. **Verify report completeness:**
   - All sections render
   - Findings include expert explanations + AI prompts
   - PDF export works

---

### Test 8: Error Scenarios

#### 8A: DataForSEO API Offline
```bash
# Temporarily disable DataForSEO in analyze.js (comment out the call)
# Then run scan

# Expected: Return cached/fallback data instead of crashing
# Verify: analyze endpoint still returns 200 (graceful degradation)
```

#### 8B: OpenAI API Timeout
```bash
# Temporarily increase timeout to 1ms in webhook.js
# Then complete a Stripe payment

# Expected: Report saved with fallback message
# Verify: report endpoint returns 200 with "manual review" message in findings
```

#### 8C: KV Quota Exceeded
```bash
# Manually fill KV to 90% (or mock this in tests)
# Then run full flow

# Expected: Logs error, but endpoint still responds
# Verify: Non-blocking failure (user experience not affected)
```

#### 8D: Missing Stripe Key
```bash
# Remove STRIPE_SECRET_KEY from Cloudflare env vars
# Click "Get Full Report" on dashboard

# Expected: 402 response with Calendly fallback
# Verify: Graceful fallback (no crash, provides alternative)
```

---

### Test 9: Performance Benchmarks

| Operation | Target | Actual |
|-----------|--------|--------|
| Free scan | <5 sec | __ sec |
| Checkout | <1 sec | __ sec |
| Webhook | <10 sec | __ sec |
| Report fetch | <500ms | __ sec |
| Report render | <2 sec | __ sec |

**How to measure:**
- Open browser DevTools (F12)
- Go to **Network** tab
- Perform operation
- Record "Finish" time

---

### Test 10: Data Retention

```bash
# Verify audit data persists for 30 days
# Verify report data persists for 30 days
# Verify session data expires after 7 days

# Check KV keys (via Cloudflare Dashboard):
# - Should see: audit:*, report:*, session:* keys
# - Each with appropriate TTL set
```

---

## Regression Tests (After Each Deploy)

After pushing new code, run:
1. Test 1: Free scan
2. Test 3: Webhook (via Stripe CLI)
3. Test 4: Report endpoint
4. Test 7: End-to-end with Stripe test
5. Test 8: Error scenarios

---

## Test Summary Checklist

- [ ] All syntax checks pass
- [ ] Env vars load correctly
- [ ] KV connection works
- [ ] Free scan returns audit_id
- [ ] Checkout creates Stripe session
- [ ] Webhook processes events correctly
- [ ] Report endpoint returns enriched data (with admin auth)
- [ ] Report endpoint rejects unpaid users
- [ ] HTML report renders all sections
- [ ] PDF export works
- [ ] End-to-end Stripe flow completes
- [ ] Error scenarios handled gracefully
- [ ] Performance meets targets
- [ ] Data retention TTLs working

---

**When all tests pass, you're ready for production!**
