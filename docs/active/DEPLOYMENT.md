# 🚀 Deployment Guide

Your code is now live on GitHub: **https://github.com/simplysmartai/5cypressautomation**

## Option 1: Deploy to Railway (Recommended)

**Why Railway:** Handles both Node.js + Python, auto-deploys on git push, $5-50/mo

### Steps:

1. **Sign up**: Go to [railway.app](https://railway.app) and sign in with GitHub

2. **New Project**: Click "New Project" → "Deploy from GitHub repo"

3. **Select Repo**: Choose `simplysmartai/5cypressautomation`

4. **Environment Variables**: In Railway dashboard, add these variables:
   ```
   NODE_ENV=production
   PORT=3000
   APIFY_API_TOKEN=your_apify_token_here
   GOOGLE_SHEETS_API_KEY=your_sheets_key_here
   MODAL_API_TOKEN=your_modal_token_here
   ```

5. **Deploy**: Railway auto-deploys. Your site will be live at:
   ```
   https://5cypressautomation-production.up.railway.app
   ```

6. **Custom Domain** (Optional): In Railway settings, add custom domain:
   - `simplysmartautomation.com`
   - Railway provides SSL automatically

---

## Option 2: Deploy to Vercel (Frontend Only)

**For static site + serverless functions**

```bash
npm install -g vercel
vercel login
vercel --prod
```

Your site will be live at: `https://5cypressautomation.vercel.app`

**Note:** Vercel doesn't support long-running Python scripts. Use Modal for backend workflows.

---

## Option 3: Deploy Modal Webhooks

**For automation workflows (form submissions, scheduled reports, scrapers)**

### Setup:

```bash
# Install Modal CLI
pip install modal

# Authenticate
modal token new

# Deploy webhooks
modal deploy execution/modal_webhook.py

# Your webhooks are live at:
# https://nick-90891--claude-orchestrator-directive.modal.run?slug={slug}
```

### Test webhook:

```bash
curl -X POST \
  "https://nick-90891--claude-orchestrator-directive.modal.run?slug=test-email" \
  -H "Content-Type: application/json" \
  -d '{"to":"your@email.com","subject":"Test","body":"Hello from Modal"}'
```

### Register new webhooks:

Edit `execution/webhooks.json`:

```json
{
  "webhooks": [
    {
      "slug": "form-submit",
      "directive": "directives/live_demo_automation.md",
      "tools": ["send_email", "update_sheet", "create_invoice"]
    }
  ]
}
```

Then redeploy: `modal deploy execution/modal_webhook.py`

---

## Environment Variables You Need

| Variable | Where to Get It |
|----------|-----------------|
| `APIFY_API_TOKEN` | [apify.com/settings/integrations](https://apify.com/settings/integrations) |
| `GOOGLE_SHEETS_API_KEY` | [console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials) |
| `MODAL_API_TOKEN` | Run `modal token new` |
| `OPENAI_API_KEY` | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) (if using AI features) |

---

## Post-Deployment Checklist

- ✅ Test skills dashboard at `/skills-dashboard.html`
- ✅ Verify `/api/skills` returns 30 skills
- ✅ Test a skill activation (Amazon Product Scraper)
- ✅ Set up custom domain (optional)
- ✅ Deploy Modal webhooks for automation workflows
- ✅ Test form submissions → Modal webhook → email/sheet updates
- ✅ Set up monitoring (Railway has built-in logs)

---

## Troubleshooting

**Skills dashboard blank?**
- Check browser console for errors
- Verify `/api/skills` endpoint returns JSON
- Ensure `skills/skills.json` exists

**Modal webhook not working?**
- Check Modal logs: `modal logs`
- Verify webhook is registered in `execution/webhooks.json`
- Test locally: `python execution/{script_name}.py`

**Environment variables not loading?**
- Railway: Check "Variables" tab in dashboard
- Vercel: Check "Environment Variables" in project settings
- Modal: Create `.secrets.toml` file (not in git)

---

## Updating the Site

After making changes locally:

```bash
git add .
git commit -m "Your update message"
git push origin main
```

Railway auto-deploys within 2-3 minutes.

---

## Cost Estimates

| Platform | Estimated Monthly Cost |
|----------|----------------------|
| Railway (Node.js + site hosting) | $5-20 |
| Modal (automation workflows) | $10-30 |
| Apify (scraping) | $10-50 (pay-per-use) |
| Custom Domain | $12/year |
| **Total** | **$25-100/month** |

---

## Next Steps

1. Deploy to Railway (5 minutes)
2. Test skills dashboard works on production URL
3. Deploy Modal webhooks (10 minutes)
4. Wire website forms to Modal endpoints
5. Set up custom domain
6. Go live! 🎉
