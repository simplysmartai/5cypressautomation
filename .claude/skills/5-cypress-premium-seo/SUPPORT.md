# Support & Troubleshooting — Premium SEO Skill

Common issues and solutions for the skill.

---

## Frequently Asked Questions

### Q: My Stripe checkout isn't working. What's wrong?

**A: Check these in order:**

1. **Is `STRIPE_SECRET_KEY` set?**
   - Cloudflare Pages → Settings → Environment Variables
   - Should start with `sk_live_` or `sk_test_`
   - If missing, `/api/seo/checkout` returns 402 with Calendly fallback

2. **Is the function deployed?**
   ```bash
   # Check that checkout.js exists
   ls functions/api/seo/checkout.js
   # If not, push again: git push
   ```

3. **Did you redeploy after adding the env var?**
   - Cloudflare doesn't apply new env vars without a redeploy
   - Pages → Deployments → click "Retry deployment"
   - Or push a dummy commit: `git commit --allow-empty -m "redeploy" && git push`

4. **Is your webhook registered?**
   - Stripe Dashboard → Developers → Webhooks
   - Should have endpoint: `https://your-domain.com/api/seo/webhook`
   - Event: `checkout.session.completed`

---

### Q: The report page shows "processing" forever. Why?

**A: The webhook hasn't finished enriching.**

1. **Check webhook logs:**
   - Stripe Dashboard → Developers → Webhooks → select your endpoint
   - Look for recent events under your session ID
   - If failed, click the event to see error message

2. **Are env vars set? (for webhook)**
   - `OPENAI_API_KEY` — required for enrichment
   - `STRIPE_SECRET_KEY` — required to verify webhook signature
   - `ADMIN_USER` / `ADMIN_PASS` — required for admin bypass

3. **Did you wait long enough?**
   - OpenAI enrichment takes 10-30 seconds
   - Report page polls every 5 seconds
   - Max polling time: 2 minutes before "timeout" error

4. **Is OpenAI API working?**
   ```bash
   # Test your OpenAI key
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer sk-proj-YOUR_KEY"
   # Should return list of models (200 OK)
   ```

5. **Check Cloudflare logs:**
   - Pages → Analytics → Requests
   - Filter for `/api/seo/webhook`
   - Look for 500 errors in webhook.js

---

### Q: Admin bypass isn't working. I get 401.

**A: Authorization header is incorrect.**

1. **Verify your credentials:**
   - `ADMIN_USER=your_username` (check spelling)
   - `ADMIN_PASS=your_password` (case-sensitive)

2. **Verify Basic Auth encoding:**
   ```bash
   # Correct format
   echo -n "your_username:your_password" | base64
   # Example output: eW91cl91c2VybmFtZTp5b3VyX3Bhc3N3b3Jk
   
   # Then use
   curl https://your-domain.com/api/seo/report?session_id=test&domain=example.com \
     -H "Authorization: Basic eW91cl91c2VybmFtZTp5b3VyX3Bhc3N3b3Jk"
   ```

3. **Check env vars in Cloudflare:**
   - Pages → Settings → Environment Variables
   - Verify both `ADMIN_USER` and `ADMIN_PASS` are set
   - Redeploy if you just added them

---

### Q: Getting "KV namespace not found" error.

**A: The KV binding is missing or misconfigured.**

1. **Check `wrangler.toml`:**
   ```toml
   [[kv_namespaces]]
   binding = "SEO_AUDITS_KV"
   id = "adb56962135c4b6c8e610202123121ed"  # your actual ID
   ```

2. **Verify namespace exists:**
   ```bash
   npx wrangler kv:namespace list
   # Should show SEO_AUDITS_KV
   ```

3. **Redeploy:**
   ```bash
   git add wrangler.toml
   git commit -m "fix: kv namespace binding"
   git push
   ```

4. **Check Cloudflare Pages Dashboard:**
   - Pages → your project → Settings → Functions
   - Should show "KV namespace bindings:" with SEO_AUDITS_KV
   - If missing, add it manually in the dashboard

---

### Q: Report shows "No audit data found" even though I ran a scan.

**A: The audit wasn't saved to KV, or the session ID doesn't match.**

1. **Verify audit was saved:**
   - Run a free scan, copy the `audit_id` from browser console
   - Check KV in Cloudflare Dashboard (KV → browse data)
   - Look for key starting with `audit:`

2. **Verify session/audit_id match:**
   - When you click "Get Full Report", the `audit_id` should be passed to checkout
   - Then passed to webhook
   - Webhook uses it to fetch the audit data

3. **Check analyze.js:**
   ```javascript
   // Should include this:
   await env.SEO_AUDITS_KV.put(`audit:${auditId}`, JSON.stringify({ data, url: href }), ...);
   ```
   - If missing, re-deploy the analyze.js fix

---

### Q: PDF export isn't working.

**A: Browser can't print.**

1. **Try different browser:**
   - Chrome/Chromium: `Ctrl+P` (Windows) or `Cmd+P` (Mac)
   - Firefox: `Ctrl+P` or `Cmd+P`
   - Safari: `Cmd+P`

2. **Check CSS media queries:**
   - Report HTML should have `@media print { ... }`
   - This hides non-essential elements on print

3. **Check print preview:**
   - It should show all sections (even collapsed `<details>`)
   - `beforeprint` event forces all `<details>` open

4. **If still failing:**
   - Right-click anywhere on page
   - Select "Print" or "Save as PDF"
   - Or use browser extensions (Awesome Screenshot, etc.)

---

### Q: Getting 500 errors from `/api/seo/webhook`.

**A: Webhook function has a runtime error.**

1. **Check webhook signature verification:**
   - Stripe sends `stripe-signature` header
   - webhook.js validates signature using Web Crypto API
   - If signature is invalid, should return 400 (not 500)

2. **Check OpenAI call:**
   - `enrichReport()` calls OpenAI
   - If API key missing or invalid, OpenAI throws error
   - Webhook should catch and return fallback report (not crash)

3. **Check log for error:**
   - Cloudflare Pages → Analytics → Requests
   - Find request to `/api/seo/webhook`
   - Click to see full error message

4. **Test webhook locally:**
   ```bash
   npx wrangler pages dev public
   # Then POST to http://localhost:8787/api/seo/webhook with test data
   ```

---

### Q: DataForSEO API is returning errors. How do I fix it?

**A: DataForSEO may be down or your quota exceeded.**

1. **Check DataForSEO status:**
   - https://status.dataforseo.com/
   - If down, wait for them to recover

2. **Check your quota:**
   - DataForSEO Dashboard → Account → Usage
   - If you've exceeded monthly calls, upgrade plan

3. **Check API key:**
   - Verify `DATAFORSEO_API_KEY` is set (if you're using it)
   - Or check in analyze.js that credentials are correct

4. **Graceful fallback:**
   - If DataForSEO fails, analyze.js should return error message
   - Client should see friendly error ("API unavailable, try again later")
   - NOT crash

---

### Q: OpenAI API hitting rate limits.

**A: You're calling OpenAI too fast.**

1. **Check your rate limit:**
   - OpenAI Dashboard → Usage
   - Compare against your plan limits

2. **Upgrade your plan:**
   - If using free credits, switch to paid account
   - Set monthly spend limit

3. **Reduce concurrency:**
   - If many webhooks run at once, they all call OpenAI
   - Add queue/retry logic if needed
   - Currently no built-in retry; each payment triggers immediate enrichment

4. **Fallback on timeout:**
   - If OpenAI takes >10 sec, webhook.js returns fallback
   - Report includes note: "Manual review within 24 hours"

---

### Q: Stripe webhook not triggering. I completed a test payment but no event arrived.

**A: Webhook endpoint not registered correctly.**

1. **Verify webhook exists in Stripe:**
   - Stripe Dashboard → Developers → Webhooks
   - Should show endpoint with URL
   - Should have `checkout.session.completed` event selected

2. **Check webhook status:**
   - Click the endpoint
   - Look at "Recent events" section
   - If no events, webhook never triggered (Stripe didn't call it)

3. **Check for signature verification errors:**
   - Each event shows status: "Created", "Processed", "Failed"
   - If failed, click to see why

4. **Verify you used test card in test mode:**
   - Test webhooks only trigger if you use `sk_test_...` Stripe key
   - And you pay with test card: `4242 4242 4242 4242`
   - Live webhooks need `sk_live_...` key + real card

5. **Re-register webhook:**
   - Delete current webhook
   - Create new endpoint at `https://your-domain.com/api/seo/webhook`
   - Select `checkout.session.completed` event
   - Make a test payment
   - Check webhook logs

---

## Common Error Messages

### "Missing API key"
- Add `OPENAI_API_KEY` and/or `STRIPE_SECRET_KEY` to Cloudflare env vars
- Redeploy

### "Invalid stripe-signature"
- Check `STRIPE_WEBHOOK_SECRET` is correct
- Re-register webhook in Stripe, copy new secret
- Update env var, redeploy

### "KV quota exceeded"
- Upgrade Cloudflare plan or delete old audit/report records manually
- Temporary fix: wait 7 days (session records auto-expire)

### "OpenAI connection timeout"
- Check if api.openai.com is reachable
- Increase timeout: change `timeout: 10000` to `timeout: 20000` in webhook.js
- Redeploy

### "404 Not Found" on `/api/seo/report`
- Check query params: `?session_id=...&domain=...` are present
- Verify session was saved to KV after checkout
- Verify admin auth header if using bypass

---

## Performance Optimization

### Slow scan (>5 sec)?
- DataForSEO API latency varies by domain size
- Large sites (10K+ pages) take longer
- Normal range: 60-300 seconds for full crawl

### Slow webhook (>10 sec)?
- OpenAI enrichment time varies
- Increase timeout if it's timing out
- Monitor OpenAI API response time in your dashboard

### Slow report page (>2 sec)?
- Rendering gauges/charts
- Polling KV every 5 sec
- Normal: 2-5 sec for full report render

---

## Monitoring & Health Checks

**Weekly checklist:**
- [ ] Check Stripe Dashboard for failed webhooks
- [ ] Monitor Cloudflare Analytics for 5xx errors
- [ ] Check KV usage (if close to quota, delete old data)
- [ ] Monitor OpenAI API costs
- [ ] Spot-check a few reports for quality

**Monthly:**
- [ ] Review error logs
- [ ] Check average report quality (gauge grades, findings count)
- [ ] Monitor uptime (Cloudflare Pages status)
- [ ] Calculate margin (revenue - API costs)

---

## Getting Help

**For technical issues:**
1. Check this file first
2. Review error logs in Cloudflare Pages Analytics
3. Test functions locally: `npx wrangler pages dev public`
4. Check API status pages (Stripe, OpenAI, DataForSEO)
5. Post on Cloudflare community forum

**For Stripe-specific issues:**
- Stripe Support Dashboard (direct chat)
- Stripe documentation: stripe.com/docs

**For OpenAI issues:**
- OpenAI help center: https://help.openai.com/
- OpenAI API documentation: https://platform.openai.com/docs

---

**Still stuck? Add debugging logs to functions and re-deploy to see live errors.**
