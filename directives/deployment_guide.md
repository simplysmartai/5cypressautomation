# Deployment Guide: 5 Cypress Automation

> **CRITICAL: Static files require updates in TWO places** — DigitalOcean (Node.js server) AND Cloudflare (CDN edge cache). Backend changes only require DO.

## Deployment Architecture

```
GitHub (source of truth)
  ↓
  ├─→ Cloudflare Pages (static files: CSS, JS, HTML in /public)
  └─→ DigitalOcean Droplet (Node.js server + SQLite DB)
```

- **GitHub**: `github.com/simplysmartai/5cypressautomation` (main branch)
- **DO Droplet**: `134.199.192.11` (ssh user: `jimmy`, key: `~/.ssh/id_ed25519`)
- **Server Process**: PM2 process named `5cypress` running on port 3000 (behind nginx reverse proxy)

---

## Deployment Process

### Step 1: Commit & Push to GitHub

```bash
cd /path/to/5cypressautomation
git add <files>
git commit -m "descriptive message"
git push origin main
```

### Step 2: Deploy to DigitalOcean

**SSH into the droplet:**
```bash
ssh -i ~/.ssh/id_ed25519 jimmy@134.199.192.11
```

**Pull latest code and restart server:**
```bash
cd /home/jimmy/5cypress
git pull origin main
npm install --production
pm2 restart 5cypress
pm2 status 5cypress
```

**Verify deployment (on droplet or locally):**
```bash
curl -s https://5cypress.com/admin/admin-light.css | head -5
# Should return CSS content with status 200
```

### Step 3: Cloudflare Cache Invalidation (if needed)

Static files on Cloudflare may be cached. If visitors see stale CSS after deployment:

1. **Option A - Auto**: Cloudflare's cache should purge within 1-2 hours (depends on TTL rules)
2. **Option B - Manual**: 
   - Log into Cloudflare dashboard
   - Go to **Caching → Purge Cache**
   - Select **Purge whole site** or specify `/public/*` and `/admin/*`

---

## What Requires DO Update vs. Cloudflare?

| Change | Where | DO Update | CF Purge |
|--------|-------|-----------|----------|
| CSS/JS/HTML in `/public/` | Static files | ✅ Yes | ✅ Recommended |
| Admin HTML pages | `public/admin/` | ✅ Yes | ✅ Recommended |
| API routes, webhooks | `routes/` | ✅ Yes | ❌ No |
| Database schema | `db.js` | ✅ Yes | ❌ No |
| Package dependencies | `package.json`, `requirements.txt` | ✅ Yes | ❌ No |
| Server config | `.env`, `server.js` | ✅ Yes | ❌ No |

---

## Deployment Checklist

- [ ] Changes committed locally with clear message
- [ ] `git push origin main` succeeded
- [ ] SSH connection to DO: `ssh -i ~/.ssh/id_ed25519 jimmy@134.199.192.11`
- [ ] Executed: `git pull origin main`
- [ ] Executed: `npm install --production` (no errors)
- [ ] Executed: `pm2 restart 5cypress`
- [ ] Verified with: `pm2 status 5cypress` (should show `online`)
- [ ] Tested live site (curl or browser)
- [ ] If static files changed: purge Cloudflare cache if stale content shows

---

## Troubleshooting

**Port 8000 already in use (local dev):**
```bash
Get-Process -Name node | Stop-Process -Force
```

**PM2 won't restart:**
```bash
ssh -i ~/.ssh/id_ed25519 jimmy@134.199.192.11
pm2 logs 5cypress  # Check error logs
pm2 kill           # Kill all PM2 processes and restart
pm2 start /home/jimmy/.pm2/conf.js
```

**Stale CSS on live site after deployment:**
- Wait 5 minutes (Cloudflare cache TTL)
- Force refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
- Purge Cloudflare cache manually in dashboard

**Git pull fails:**
```bash
# Check current branch and status
git status
git log --oneline -5

# If merge conflicts, reset and retry
git reset --hard origin/main
git pull origin main
```

---

## Credentials & IPs

- **DO Droplet IP**: `134.199.192.11`
- **DO SSH User**: `jimmy`
- **SSH Key**: `~/.ssh/id_ed25519` (ED25519), `~/.ssh/id_rsa` (RSA backup)
- **Admin Credentials**: See `.env` file (`ADMIN_USER`, `ADMIN_PASS`)
- **GitHub Repo**: `github.com/simplysmartai/5cypressautomation`
- **Live Domain**: `https://5cypress.com`

---

## Recent Deployments

| Commit | Date | Changes |
|--------|------|---------|
| 966123f | 2026-03-09 | Admin UI refinement: larger fonts, light grey cables |
| ca98155 | 2026-03-09 | Fix typo: anthrophic → anthropic |
| 61fa802 | 2026-03-09 | Admin redesign: light theme, leads management |

---

## Notes

- **No GitHub Actions automation yet** — all DO deployments are manual
- **Cloudflare Pages** serves static only; Node.js server on DO handles all backend
- **SQLite database** persists on DO droplet at `~/5cypress/leads.db` (not backed up to GitHub)
- **Env vars** stored in `.env` on DO; never commit to GitHub
