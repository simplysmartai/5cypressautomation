# Setup Zoho Calendar Integration

**System:** Zoho Workplace (Calendar component)  
**Auth:** OAuth 2.0 with organization scope  
**Time:** 15 minutes  
**Frequency:** Once per client

## Prerequisites

- Client has Zoho Workplace plan (not free tier)
- Zoho admin access (Organization admin or Super admin)
- 15-minute Zoom call scheduled with admin

## Overview

This directive guides you through setting up **organization-wide** Zoho Calendar access. One admin authorization grants access to all employee calendars—no individual logins required.

## Architecture

```
Zoho Calendar (All Employees) →
  OAuth Admin Consent →
    Refresh Token (never expires) →
      Your System Can Access All Calendars →
        Real-Time Webhook Updates →
          Dashboard Auto-Refreshes
```

## Steps

### 1. Create Zoho OAuth App

**Client admin does this (5 minutes):**

1. Go to https://api-console.zoho.com
2. Click "Add Client" → "Server-based Applications"
3. Fill in:
   - **Client Name:** "5 Cypress Calendar Sync"
   - **Homepage URL:** https://5cypressautomation.com
   - **Authorized Redirect URI:** http://localhost:8000/callback
4. Click "Create"
5. Copy **Client ID** and **Client Secret**
6. Share credentials with you (encrypted via 1Password link or similar)

### 2. Add Calendar Scopes

**Client admin continues:**

1. In app settings, click "Add Scope"
2. Select Zoho Calendar scopes:
   - `ZohoCalendar.calendar.ALL` (read/write all calendars)
   - `ZohoCalendar.event.ALL` (read/write all events)
3. Click "Save"

### 3. Identify Data Center

**Important:** Zoho has different data centers by region.

Ask client admin: "Which Zoho domain do you log into?"
- **zoho.com** → US data center (use `ZOHO_DC=com`)
- **zoho.eu** → Europe data center (use `ZOHO_DC=eu`)
- **zoho.in** → India data center (use `ZOHO_DC=in`)
- **zoho.com.au** → Australia data center (use `ZOHO_DC=au`)
- **zoho.jp** → Japan data center (use `ZOHO_DC=jp`)

### 4. Save Credentials to .env

Add to your `.env` file:

```bash
# Zoho Calendar Integration
ZOHO_CLIENT_ID=1000.ABC123XYZ
ZOHO_CLIENT_SECRET=abc123def456ghi789jkl012
ZOHO_DC=com  # or eu, in, au, jp
```

### 5. Authorize App (Admin Consent)

**Run setup script:**

```bash
python execution/setup_zoho_calendar_admin.py
```

**Script will:**
1. Print authorization URL
2. You send URL to client admin
3. Admin opens URL in browser
4. Admin clicks "Accept" (grants org-wide access)
5. Admin is redirected to `http://localhost:8000/callback?code=ABC123...`
6. Admin copies the `code=...` value from URL
7. Admin sends code to you
8. You paste code into script
9. Script exchanges code for refresh token
10. Refresh token saved to `.env` automatically

**Expected output:**
```
📧 Send this URL to Remy Lasers admin:
https://accounts.zoho.com/oauth/v2/auth?scope=ZohoCalendar...

After they authorize, they'll see authorization code. Paste it here:
Authorization code: 1000.abc123...

✅ Refresh token saved to .env

✅ Found 12 users in organization:
   - Sarah Johnson (sarah@remylasers.com)
   - John Smith (john@remylasers.com)
   - Mike Chen (mike@remylasers.com)
   ...

✅ Sarah Johnson: 2 calendars
   - Primary (cal_abc123)
   - Team Meetings (cal_def456)
```

### 6. Register Webhooks

**Run webhook setup:**

```bash
python execution/setup_zoho_calendar_webhook.py
```

**Script will:**
1. Get list of all organization users
2. Register webhook for each user's primary calendar
3. Webhooks fire when events created/updated/deleted
4. Modal endpoint receives and processes changes

**Expected output:**
```
✅ Registered webhook for sarah@remylasers.com
✅ Registered webhook for john@remylasers.com
✅ Registered webhook for mike@remylasers.com
...
✅ 12 webhooks registered successfully
```

### 7. Sync Initial Calendar Data

**Run initial sync:**

```bash
python execution/sync_zoho_calendars.py
```

**Script will:**
1. Pull all events for next 30 days from all calendars
2. Calculate availability slots for each employee
3. Save to `.tmp/calendar_cache.json`
4. Dashboard can now display real-time availability

**Expected output:**
```
✅ Syncing calendars for 12 employees...
✅ Sarah Johnson: 28 events
✅ John Smith: 15 events
✅ Mike Chen: 42 events
...
✅ Synced 12 calendars with 247 total events
✅ Calendar cache saved to .tmp/calendar_cache.json
```

### 8. Deploy Webhook Handler to Modal

**Deploy Modal webhook:**

```bash
modal deploy execution/zoho_calendar_webhook.py
```

**Script will:**
1. Deploy webhook endpoint to Modal
2. Print public URL (e.g., `https://your-app--zoho-webhook.modal.run`)
3. Copy this URL for webhook registration

**Update webhook URL:**
1. Open `execution/setup_zoho_calendar_webhook.py`
2. Replace `webhook_url` with your Modal URL
3. Re-run webhook setup script

## Testing Checklist

Test the integration:

- [ ] Can list all organization users
- [ ] Can read each user's primary calendar
- [ ] Can read events for next 30 days
- [ ] Webhooks registered for all users
- [ ] **Manual test:** Admin creates test event in Zoho Calendar
- [ ] **Verify:** Webhook fires within 5 seconds
- [ ] **Verify:** `.tmp/calendar_cache.json` updates
- [ ] **Verify:** Dashboard shows new event
- [ ] **Manual test:** Admin deletes test event
- [ ] **Verify:** Dashboard updates within 5 seconds

## Tools Used

### Execution Scripts
- `execution/setup_zoho_calendar_admin.py` - Admin OAuth setup
- `execution/setup_zoho_calendar_webhook.py` - Register webhooks
- `execution/sync_zoho_calendars.py` - Pull calendar data
- `execution/zoho_calendar_webhook.py` - Modal webhook handler

### Outputs
- `.env` - Stores refresh token (never expires)
- `.tmp/calendar_cache.json` - Cached calendar data

## Troubleshooting

### "Invalid client" error
**Cause:** Client ID or Secret incorrect, or wrong data center

**Fix:**
1. Verify credentials in `.env` have no extra spaces
2. Check `ZOHO_DC` matches client's login domain
3. Ensure client copied full Client ID (starts with `1000.`)

### "Scope not authorized" error
**Cause:** Admin didn't click "Accept" or scopes not added in API Console

**Fix:**
1. Verify scopes added in Zoho API Console (Step 2)
2. Re-run authorization flow
3. Ensure admin clicks "Accept" (not "Deny")

### "Calendar not found" error
**Cause:** User has no primary calendar or is suspended

**Fix:**
1. Admin checks user is active in Zoho admin console
2. User logs into Zoho Calendar once (creates primary calendar)
3. Re-run sync script

### Webhook not firing
**Cause:** Modal endpoint not publicly accessible or URL incorrect

**Fix:**
1. Run `modal deploy execution/zoho_calendar_webhook.py`
2. Copy Modal URL from output
3. Update `webhook_url` in setup script
4. Re-run `python execution/setup_zoho_calendar_webhook.py`
5. Test with manual event creation in Zoho Calendar

### "Token expired" error
**Cause:** Access token expired (1 hour lifespan)

**Fix:**
- Script auto-refreshes using refresh token
- If still failing, check refresh token is in `.env`
- Re-run admin setup if refresh token lost

## Maintenance

**Refresh token:** Never expires (unless admin revokes)

**Access token:** Expires every 1 hour (scripts auto-refresh)

**Webhooks:** Permanent until revoked (no renewal needed)

**New employees:** Automatically included
- Re-run: `python execution/setup_zoho_calendar_webhook.py`
- Registers webhook for new user's calendar

**Webhook monitoring:** Check Modal logs for failed deliveries

## Security

### What Admin Can Control

**Revoke access anytime:**
1. Go to https://api-console.zoho.com
2. My Clients → "5 Cypress Calendar Sync"
3. Click "Revoke"
4. Your system loses access immediately

**View audit logs:**
- Zoho tracks all API calls
- Admin can see which calendars accessed and when

### What You Can Access

**With these scopes:**
- All users' calendars (read/write)
- Event details (title, time, attendees, location)
- Create/update/delete events

**Cannot access:**
- Email, files, contacts (unless those scopes added)
- Billing information
- User passwords
- Admin settings

### Credentials Storage

**Best practices:**
- Store refresh token in `.env` (gitignored)
- Never commit credentials to git
- Encrypt `.env` at rest (use BitLocker/FileVault)
- Never log tokens to console or files
- Use environment variables in production (Railway, Modal)

## Success Metrics

After setup complete:

- ✅ 100% of employees' calendars accessible
- ✅ < 5 seconds webhook → dashboard update latency
- ✅ Zero failed API calls in first 24 hours
- ✅ Dashboard accuracy: 100% (matches Zoho Calendar exactly)
- ✅ Real-time sync verified (create event → dashboard updates < 5 sec)

## Integration with Calendar Dashboard

Once setup complete:

1. **Dashboard loads** → Reads `.tmp/calendar_cache.json`
2. **Displays availability** → Color-coded grid (green = available, red = busy)
3. **Employee updates calendar** → Zoho sends webhook
4. **Modal processes** → Updates cache within 2 seconds
5. **WebSocket pushes update** → Dashboard refreshes automatically
6. **All users see change** → No manual refresh needed

## Pricing Impact

**Zoho Calendar integration:**
- One-time setup: **Included** in calendar module ($1,500)
- Monthly recurring: **$0** (no ongoing costs)
- API calls: **Free** (within Zoho's rate limits)

**Compared to alternatives:**
- Google Workspace: Same (free API)
- Microsoft 365: Same (free Graph API)
- Calendly: Same (free API)

## Next Steps

After Zoho integration complete:

1. ✅ Test webhook with manual event creation
2. ✅ Verify dashboard shows real-time updates
3. ✅ Send confirmation to client: "Calendar sync active"
4. ✅ Schedule follow-up in 1 week to verify stability
5. ✅ Add calendar dashboard link to client's main dashboard

## Support

**If client asks about data privacy:**
- Your app only reads calendar events (titles, times, attendees)
- Data cached locally in `.tmp/` (regenerated on demand)
- No data sent to third parties
- Admin can revoke access anytime

**If client asks about reliability:**
- Webhooks deliver within 2-5 seconds
- Backup: Cron job syncs every 5 minutes (if webhook fails)
- 99.9% uptime (Modal SLA)
- Failed webhooks logged and auto-retried

**If client asks about scaling:**
- Current design supports up to 100 employees
- API rate limit: 5,000 requests/day (plenty for 100 users)
- If client grows beyond 100 employees, upgrade to paid Zoho API tier
