# Wrangler CLI Setup & Deployment

**Wrangler** is Cloudflare's command-line tool. It's the fastest way to deploy your site.

---

## 📦 Installation

```bash
# Install Wrangler globally (or use npx)
npm install -g @cloudflare/wrangler

# Verify installation
wrangler --version
```

---

## 🔐 Authentication

```bash
# Login to Cloudflare
wrangler login

# This opens a browser window to authorize Wrangler
# Select "Create a new token" if you haven't already
# Grant permissions for:
#   - Account Settings
#   - Workers and Pages
```

**Token created automatically in:**
```
~/.wrangler/config.toml
```

---

## 🚀 Deploy in One Command

```bash
# From project root:
npm run deploy

# Or directly:
npx wrangler deploy

# Or with Wrangler CLI:
wrangler deploy
```

**What happens:**
1. Reads `wrangler.toml` configuration
2. Runs build command: `npm install`
3. Uploads to Cloudflare
4. **Site goes live in 60-90 seconds**

**Your site is now at:**
```
https://5cypress.pages.dev
```

---

## 🛠️ Common Commands

**View logs:**
```bash
wrangler tail
```

**Keep watching logs (real-time tail):**
```bash
wrangler tail --follow
```

**List all deployments:**
```bash
wrangler deployments list
```

**Rollback to previous version:**
```bash
wrangler rollback
```

**Check current version:**
```bash
wrangler deployments view
```

**Upload version history:**
```bash
npm run versions
# or
npx wrangler versions upload
```

---

## 📋 Configuration File

All settings in `wrangler.toml`:

```toml
name = "5cypressautomation"
type = "javascript"
account_id = ""  # Auto-filled on first deploy
workers_dev = true
route = ""

[env.production]
route = "5cypress.pages.dev/*"
zone_id = ""

[build]
command = "npm install"
cwd = "./"
watch_paths = ["**/*.js", "**/*.json", "public/**/*", "functions/**/*"]

[build.upload]
format = "modules"
main = "./server.js"
```

**Don't modify unless needed.** Wrangler auto-configures most settings.

---

## 🔒 Environment Variables

### **Option 1: Deploy with .env file**

Create `.env` in project root:
```
MODAL_API_TOKEN=your_token_here
MODAL_WEBHOOK_URL=https://nick-90891--claude-orchestrator-directive.modal.run
NODE_VERSION=18
```

**Note:** `.env` is in `.gitignore` (won't be committed)

### **Option 2: Set in wrangler.toml**

```toml
[env.production]
vars = { MODAL_WEBHOOK_URL = "https://nick-90891--claude-orchestrator-directive.modal.run" }
```

### **Option 3: Cloudflare Dashboard**

1. Go to [dash.cloudflare.com](https://dash.cloudflare.com)
2. Find your Pages project
3. Settings → Environment variables
4. Add variables there

**Recommended:** Use .env locally + Dashboard for production secrets

---

## 🔄 Automatic Deployments

**Every `git push` triggers a deploy automatically:**

```bash
git add .
git commit -m "Update site"
git push origin main
```

Cloudflare redeploys within 60-90 seconds.

---

## 🐛 Troubleshooting

**"Failed to authenticate"**
```bash
# Clear authentication and login again
rm ~/.wrangler/config.toml
wrangler login
```

**"Build failed"**
```bash
# Check build command works locally
npm install

# View full Wrangler logs
wrangler deploy --verbose
```

**"Site says 404"**
- Verify `public/` folder exists
- Check `public/skills-dashboard.html` exists
- Verify `/api/skills` returns JSON

**"Environment variables not loading"**
- Check `.env` file syntax
- Verify variable names match
- Use `wrangler tail` to see actual values

---

## 📊 Monitoring

**Real-time logs:**
```bash
wrangler tail
```

**Analytics in Dashboard:**
1. [dash.cloudflare.com](https://dash.cloudflare.com)
2. Find your Pages project
3. **Analytics** tab shows:
   - Page views
   - Requests per second
   - Error rates
   - Performance

---

## 🎯 Next Steps

1. **Deploy now:**
   ```bash
   npm run deploy
   ```

2. **Watch deployment:**
   ```bash
   wrangler tail
   ```

3. **Test site:**
   ```
   https://5cypress.pages.dev/
   https://5cypress.pages.dev/skills-dashboard.html
   https://5cypress.pages.dev/api/skills
   ```

4. **Set up Modal webhooks:**
   ```bash
   pip install modal
   modal token new
   modal deploy execution/modal_webhook.py
   ```

5. **Deploy Modal version history:**
   ```bash
   npm run versions
   ```

---

## 💡 Pro Tips

**Deploy without using `-g` flag:**
```bash
# Use npx (already in package.json scripts)
npm run deploy
```

**Check what will be deployed:**
```bash
wrangler publish --dry-run
```

**Test site locally before deploying:**
```bash
npm run start
# Visit http://localhost:3000
```

**Keep Wrangler updated:**
```bash
npm install -g @cloudflare/wrangler@latest
```

---

## 📞 Help & Resources

- Docs: [developers.cloudflare.com/workers](https://developers.cloudflare.com/workers)
- CLI Reference: [developers.cloudflare.com/workers/wrangler/commands](https://developers.cloudflare.com/workers/wrangler/commands)
- Community: [discord.gg/cloudflaredev](https://discord.gg/cloudflaredev)
