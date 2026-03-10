# Client Management Skills Integration

## Overview

The admin clients page is now integrated with two new AI skills for intelligent client management:

1. **`client-discovery`** — Intelligence brief + profile generation for new clients
2. **`account-review`** — Quarterly business review + health check for active clients

Both skills connect to the admin interface via buttons in the client drawer.

---

## How to Use

### Intelligence Brief (client-discovery)

**Trigger:** Click "Intelligence Brief" button in client Overview tab

**What it does:**
- Researches company business model and market position
- Maps pain points to 5 Cypress services (invoicing, shipping, lead gen, SEO, automation)
- Generates engagement hooks and conversation talking points
- Provides JSON pre-population for client.json fields

**When to use:**
- ✅ New prospect added to admin page
- ✅ Before cold outreach email
- ✅ To populate client fields accurately

**Output:**
- Markdown intelligence brief (scan for 3-5 min before outreach)
- Pre-populated fields ready to copy into admin form

---

### Account Review (account-review)

**Trigger:** Click "Account Review" button in client Overview tab

**What it does:**
- Rolls up all project statuses (Planning, Active, Delivered, Complete)
- Highlights wins and measured impact since engagement start
- Identifies risks, blockers, and delayed projects
- Recommends next 30-day priorities
- Suggests expansion hooks

**When to use:**
- ✅ Before quarterly or annual check-in calls
- ✅ 90 days into engagement (standard rotation)
- ✅ Preparing renewal or upsell conversations
- ✅ When you need talking points fast

**Output:**
- Structured QBR brief (~400 lines, scannable in <3 min)
- Call talking points (copy-paste ready)
- Expansion opportunities with positioning advice

---

## Integration Workflow

### For New Clients (Sales → Admin)

1. **Cold outreach email sent**
2. Admin adds prospect to `/admin/clients` page
3. Click "Intelligence Brief" → opens Claude
4. Run skill with: `company_name`, `website`
5. Get brief + pre-populated fields
6. Paste into client form → Save
7. **Result:** Client profile ready for follow-up

### For Active Clients (Check-in Prep)

1. Open client in `/admin/clients` drawer
2. Click "Account Review" → opens Claude
3. Run skill with: `client_slug`
4. Review output (wins, risks, next steps, expansion)
5. Copy talking points into your calendar event
6. **Result:** Fully prepped for client conversation

### For Expansion/Renewal

1. Open client drawer, click "Account Review"
2. Review "Expansion Opportunities" section
3. Use "Recommended approach" for positioning
4. Pair with `customer-sales` skill for proposal angle
5. **Result:** Data-driven expansion pitch

---

## Connection to Existing Workflows

| Existing Task | New Skill | Benefit |
|---|---|---|
| Before cold outreach | `client-discovery` | Skip generic email; lead with specific research |
| Write discovery call prep | `account-review` | Have conversation hooks ready |
| Prepare renewal email | `account-review` | Highlight wins; frame expansion |
| Sales negotiation | `customer-sales` + brief | Use discovered pain points for positioning |

---

## Skill Locations

Both skills are available in:
- **Claude.ai** → Skills menu (or use command triggers in chat)
- **`/.claude/skills/client-discovery/SKILL.md`** — Full skill instructions
- **`/.claude/skills/account-review/SKILL.md`** — Full skill instructions

---

## Reference: Button Inputs

### Intelligence Brief

```
Input to skill:
- company_name (required): Name of company
- website (optional): Company website
- industry_hint (optional): Industry category
- contact_name (optional): Primary contact name

Output:
- Markdown intelligence brief
- JSON pre-populated client fields
```

### Account Review

```
Input to skill:
- client_slug (required): Directory slug (e.g., "nexairi-mentis")

Output:
- Project status table
- Wins summary + impact
- Risks & blockers
- Next 30-day priorities
- Expansion hooks + positioning
- Call talking points
```

---

## Tips

✅ **Best practice:** Run Intelligence Brief within 24 hours of prospect creation
✅ **Best practice:** Run Account Review 90 days after engagement start, then quarterly
✅ **Save time:** Copy QBR output to Notion/Confluence for team reference
✅ **Pair skills:** Use Discovery brief → Customer-sales skill → Account-review for full lifecycle
✅ **Track results:** Update client.json notes with outcomes from calls

---

## Admin Interface

**Location:** `https://5cypress.com/admin/clients`

**Buttons added:**
- Overview tab → "Intelligence Brief" (research icon)
- Overview tab → "Account Review" (chart icon)

Both open Claude.ai in new window with skill instruction copy-paste ready.
