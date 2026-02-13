# 🌐 Cloudflare Pages Deployment Guide

Your site is ready to deploy on **Cloudflare Pages** - the fastest, most reliable edge network with generous free tier.

---

## 🚀 Quick Deploy Option A: Wrangler CLI (Recommended for Developers)

**Install & Deploy in 3 minutes:**

```bash
# 1. Install Wrangler CLI
npm install -g @cloudflare/wrangler

# 2. Authenticate with Cloudflare
wrangler login

# 3. Deploy
npm run deploy
# or directly:
npx wrangler deploy

# 4. Done! Check your site at:
# https://5cypress.pages.dev
```

**What this does:**
- Builds: `npm install`
- Deploys to Cloudflare Pages
- Sets up auto-deployments on `git push main`
- Manages versions at `npx wrangler versions upload`

**Configuration:**
All settings are in `wrangler.toml` (already configured for you).

**Add Environment Variables Locally:**
Create `.env` file:
```
MODAL_API_TOKEN=your_token_here
MODAL_WEBHOOK_URL=https://nick-90891--claude-orchestrator-directive.modal.run
NODE_VERSION=18
```

Then deploy (wrangler reads these automatically):
```bash
npm run deploy
```

**View Logs:**
```bash
wrangler tail  # Real-time logs
```

**Roll Back to Previous Version:**
```bash
wrangler rollback
```

---

## 🚀 Quick Deploy Option B: Cloudflare Dashboard (5 Minutes)

### **Step 1: Connect GitHub to Cloudflare Dashboard**

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com)
2. Sign up or log in
3. Click **Workers & Pages** in sidebar
4. Click **Create Application** → **Pages** → **Connect to Git**
5. Authorize GitHub access
6. Select repository: `simplysmartai/5cypressautomation`

### **Step 2: Cloudflare Will Auto-Detect Configuration**

Cloudflare reads `wrangler.toml` automatically:
- **Build command:** `npm install`
- **Deploy command:** `npx wrangler deploy`
- **Production branch:** `main`

The dashboard will display these settings for you to confirm.

### **Step 3: Add Environment Variables (Dashboard)**

**Environment variables:** (Click "Add variable")
```
NODE_VERSION = 18
MODAL_API_TOKEN = your_modal_token_here
MODAL_WEBHOOK_URL = https://nick-90891--claude-orchestrator-directive.modal.run
```

### **Step 4: Deploy via Dashboard**

Click **Save and Deploy**

Your site will be live in 2-3 minutes at:
```
https://5cypress.pages.dev
```

---

## 🔧 Cloudflare Functions Setup

Your API endpoints are now Cloudflare Functions (serverless):

**File Structure:**
```
functions/
├── api/
│   ├── skills.js              → /api/skills (GET)
│   └── skills/
│       └── [id]/
│           └── run.js          → /api/skills/:id/run (POST)
```

These functions run on Cloudflare's edge network globally.

---

## 🌍 Custom Domain Setup

### **If you own a domain (e.g., simplysmartautomation.com):**

1. In Cloudflare Pages dashboard, click **Custom domains**
2. Click **Set up a custom domain**
3. Enter your domain: `simplysmartautomation.com`
4. Cloudflare will guide you to:
   - Transfer nameservers to Cloudflare (if not already)
   - Add DNS records automatically

**SSL/TLS:** Automatic (Cloudflare handles it)

### **If you don't have a domain:**

Use the free `.pages.dev` subdomain:
```
https://5cypressautomation.pages.dev
```

---

## 📋 Environment Variables

Add these in Cloudflare dashboard → **Settings** → **Environment variables**:

| Variable | Value | Where to Get |
|----------|-------|--------------|
| `NODE_VERSION` | `18` | Cloudflare default |
| `MODAL_API_TOKEN` | Your token | Run `modal token new` |
| `MODAL_WEBHOOK_URL` | `https://nick-90891--claude-orchestrator-directive.modal.run` | From Modal deploy |
| `APIFY_API_TOKEN` | Your token | [apify.com/settings](https://apify.com/settings/integrations) |

---

## ✅ Post-Deployment Testing

Once live, test these URLs:

1. **Homepage:**
   ```
   https://5cypressautomation.pages.dev/
   ```

2. **Skills Dashboard:**
   ```
   https://5cypressautomation.pages.dev/skills-dashboard.html
   ```

3. **Skills API:**
   ```
   https://5cypressautomation.pages.dev/api/skills
   ```
   Should return JSON with 30 skills

4. **Skill Activation:**
   ```bash
   curl -X POST https://5cypressautomation.pages.dev/api/skills/amazon_product_scraper/run \
     -H "Content-Type: application/json" \
     -d '{"keyword":"laptop","max_results":"5"}'
   ```

---

## 🔄 Auto-Deployments

Every `git push` to `main` branch triggers automatic deployment:

```bash
git add .
git commit -m "Update site"
git push origin main
```

Cloudflare deploys changes in **60-90 seconds**.

**Preview deployments:** Every branch gets a preview URL automatically.

---

## 🆚 Cloudflare vs Railway vs Vercel

| Feature | Cloudflare Pages | Railway | Vercel |
|---------|-----------------|---------|--------|
| **Cost** | Free (100K req/day) | $5-20/mo | $20/mo |
| **Edge Network** | 300+ cities | 18 regions | 80+ cities |
| **Build Time** | 60-90s | 2-3 min | 30-60s |
| **API Routes** | Cloudflare Functions | Full Node.js | Serverless Functions |
| **Python Support** | Via Workers | ✅ Native | ❌ No |
| **Custom Domain** | Free SSL | Free SSL | Free SSL |
| **Auto Deploy** | ✅ | ✅ | ✅ |

**Recommendation:** Use Cloudflare Pages for frontend + Modal for Python automation backend.

---

## 🐛 Troubleshooting

**Build fails?**
- Check build logs in Cloudflare dashboard
- Verify `package.json` exists
- Ensure `public/` folder has files

**API endpoints 404?**
- Verify `functions/` folder structure
- Check function file names match routes
- Redeploy from Cloudflare dashboard

**Skills dashboard blank?**
- Check browser console for errors
- Verify `/api/skills` returns JSON
- Check `skills/skills.json` is in `public/` folder

**Modal webhook not working?**
- Deploy Modal first: `modal deploy execution/modal_webhook.py`
- Set `MODAL_API_TOKEN` in Cloudflare environment variables
- Test Modal webhook directly first

---

## 📊 Performance Monitoring

Cloudflare provides free analytics:

- **Web Analytics:** Page views, visitors, performance
- **Workers Analytics:** Function invocations, errors, latency
- **Real User Monitoring (RUM):** Core Web Vitals

Access in dashboard → **Analytics**

---

## 💰 Cost Breakdown

**Free Tier Includes:**
- Unlimited sites
- Unlimited bandwidth
- 100,000 requests/day
- 500 builds/month
- Custom domains
- SSL certificates
- DDoS protection

**Paid ($20/mo) if you exceed:**
- 100K requests/day
- Need more build minutes
- Want advanced features

**For most SMBs: $0/month** 🎉

---

## 🎯 Next Steps

1. ✅ Deploy to Cloudflare Pages (you're doing this now)
2. ⏭️ Deploy Modal webhooks: `modal deploy execution/modal_webhook.py`
3. 🧪 Test skills dashboard works on production
4. 🌐 Set up custom domain (optional)
5. 📈 Monitor analytics and performance
6. 🚀 Start selling automation! 💸

---

## Support

- Cloudflare Docs: [developers.cloudflare.com/pages](https://developers.cloudflare.com/pages)
- Community: [community.cloudflare.com](https://community.cloudflare.com)
- Status: [cloudflarestatus.com](https://cloudflarestatus.com)
