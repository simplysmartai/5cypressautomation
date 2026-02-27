# 5 Cypress Lighthouse Audit Setup

This guide explains how to run automated Lighthouse audits on 5cypress.com and set up weekly monitoring.

---

## Quick Start

### Manual Audit (One-Time)

**PowerShell (Windows):**
```powershell
npm run audit:ps
```

**Cross-platform (via npm/npx):**
```bash
npm run audit
```

Both commands generate a report in `./audits/` with scores and detailed metrics.

---

## Automation Setup

### Weekly Audits via Windows Task Scheduler

1. **Open Task Scheduler** (Win+R → `taskschd.msc`)
2. **Create Basic Task**
   - Name: "5Cypress Weekly Lighthouse Audit"
   - Trigger: Weekly, Sunday @ 2:00 AM (off-hours)
   - Action: 
     ```
     Program: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
     Arguments: -ExecutionPolicy Bypass -File "C:\path\to\scripts\audit-lighthouse-weekly.ps1"
     Start in: C:\path\to\SimplySmartAutomation
     ```
3. **Check "Run whether user is logged in or not"**
4. **Enable: "Run with highest privileges"**

### Audit History Tracking

After each audit run, results are saved to:
- **JSON report:** `./audits/lighthouse-YYYYMMDD-HHMMSS.json` (full details)
- **CSV summary:** `./audits/summary.csv` (trending)

View the CSV to see score trends over time:
```
Timestamp,Performance,Accessibility,BestPractices,SEO
20260227-140530,91,100,74,92
20260305-140530,91,100,74,92
```

---

## Alert Thresholds

The audit script monitors these thresholds and flags regressions:

| Metric | Threshold | Notes |
|--------|-----------|-------|
| Performance | 85 | LCP, CLS, TBT; font loading is critical here |
| Accessibility | 90 | WCAG 2.2 AA compliance |
| Best Practices | 70 | Third-party cookies (Calendly) cap this at ~74 |
| SEO | 90 | Canonical, robots.txt, structured data |

**If any score drops below threshold:**
1. Script exits with error code 1
2. Task Scheduler can log the alert or send email (configure "On success/failure" actions)
3. Full report is saved to `./audits/lighthouse-TIMESTAMP.json`

---

## Understanding the Reports

### Quick Look: CSV Summary
```bash
cat audits/summary.csv
```
Spot trends at a glance.

### Deep Dive: JSON Report
```bash
# View in browser
npx lighthouse https://5cypress.com --view
```

Or parse the JSON directly:
```powershell
$report = Get-Content audits/lighthouse-20260227-140530.json | ConvertFrom-Json
$report.lighthouseResult.audits | Where-Object { $_.score -lt 0.9 }  # Show failed audits
```

---

## Common Issues

**"Lighthouse not found"**
```bash
npm install -g lighthouse
```

**"Chrome not found"**
- Ensure Chrome/Chromium is installed and in PATH
- Or specify path: `--chrome-path=/Applications/Chrome.app/Contents/MacOS/Google\ Chrome`

**"Permission denied"**
- PowerShell: Run as Administrator
- Others: `chmod +x scripts/audit-lighthouse-weekly.ps1`

---

## Fixing Regressions

When a threshold is breached:

1. **Check the report** for which audits failed
2. **Run the senior-frontend or senior-architect skills** against the identified issues
3. **Commit and deploy** fixes
4. **Re-run audit** to verify: `npm run audit:ps`
5. **Update the skill files** with the new finding (self-growth protocol)

Example:
```powershell
# Audit flags "LCP too high"
# → Run senior-frontend audit on the site
# → Identify slow image or third-party script
# → Fix in code
# → Commit
# → Re-audit to confirm fix
```

---

## Integrating with Slack/Email

To alert on failures, add a post-audit step:

**PowerShell example (add to audit script):**
```powershell
if ($alerts.Count -gt 0) {
    $message = "🚨 5cypress.com Lighthouse alert: $($alerts -join ', ')`nReport: $reportFile"
    # Send to Slack webhook / email / pagerduty here
}
```

---

## Self-Growing Protocol

Update the audit script when:
- Lighthouse releases a major version (weights may change)
- New critical third-party dependency added (adjust thresholds)
- Core Web Vitals pass threshold changes (Google announces quarterly)
- New audits fail consistently (add them to alert logic)

Review audit results versus the `/senior-frontend` and `/senior-architect` skill files every 90 days. If patterns emerge, update the skills' checklists to catch issues earlier.

---

## Next Steps

- [ ] Install Lighthouse: `npm install -g lighthouse`
- [ ] Test manual audit: `npm run audit:ps`
- [ ] Review first report in `./audits/`
- [ ] Set up Windows Task Scheduler (or cron) for weekly runs
- [ ] Monitor `/audits/summary.csv` for trends
- [ ] Integrate alerts (Slack/email) once stable
