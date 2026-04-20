---
name: account-review
description: "Generate lightweight quarterly business reviews (QBRs) and account health checks for active clients in the 5 Cypress system. Use this skill ANY TIME the user wants to prepare for a client check-in call, run a periodic account review, assess client health status, prepare talking points for renewal conversations, or identify expansion opportunities. Also use when they mention 'client review', 'QBR', 'account health', 'client update', 'what should we discuss', or 'where do we stand with this client.' Takes a client slug → reads client.json + projects → outputs a structured QBR with project status rollup, wins since last review, identified risks/blockers, next 30-day priorities, and expansion hooks."
compatibility: "Requires filesystem access to clients/*.json files, project tracking in client.json schema, and 5 Cypress context (CLAUDE.md, agency positioning). Works alongside data-analysis-reporting for deeper performance metrics and customer-sales for renewal/expansion tactics."
---

# Account Review

<!-- SKILL METADATA
skill_id:  account-review
version:   1.0.0
domain:    operations+sales
reviewed:  2026-03-09
status:    READY_FOR_TESTING
changelog:
  1.0.0 - Initial version: lightweight QBR generation for active clients
-->

Generate a lightweight quarterly business review (QBR) for an active client. This is the operations-side health check: How are projects tracking? What wins can we highlight? What risks need proactive management? What's the expansion play?

Unlike `data-analysis-reporting` (which analyzes campaign metrics), this skill focuses on the relationship and operational health—the things you need to know before a client call.

## Overview

Every 90 days (or on-demand before key client conversations), you need to know:
1. **What's actually shipped and working?** (Project status rollup)
2. **What value has been delivered?** (Wins + metrics since engagement start)
3. **What's at risk or delayed?** (Blockers, dependencies, timeline slips)
4. **What should we do in the next 30 days?** (Prioritized action items)
5. **Where can we expand?** (Upsell or scope increase opportunities based on usage patterns and new pain points discovered)

This skill takes a `client_slug` → reads client.json + project history → produces a QBR brief that's immediately usable as talking points for your check-in call or renewal conversation.

## Core Workflow

### Step 1: Load Client Data
- Input: `client_slug` (e.g., "nexairi-mentis")
- Read: `/clients/{slug}/client.json` to access:
  - Client metadata (name, contact, engagement_type, status)
  - Projects array with status, type, created_at, notes
  - Tags (business surface area: automation, marketing, etc.)
  - Engagement history (created_at date = engagement duration)
- Validate: Client exists and has at least one project; if no projects, note as "Recently onboarded, initial project pending"
- Capture engagement duration: Today's date - created_at = weeks/months with client

### Step 2: Project Status Rollup
Organize projects by status (Planning, In Progress, Delivered, Completed):

For each project:
- **Title** + **Type** (e.g., "QuickBooks Invoice Automation" / "workflow")
- **Current Status** + **Age** (weeks since creation)
- **Notes** summary (e.g., "Integrated with Shopify, live handling 500+ orders/month")
- **Health indicator**: Red (blocked), Yellow (at-risk), Green (on-track)

Output as clean status table:

```
| Project | Type | Status | Age | Health |
|---------|------|--------|-----|--------|
| QB Invoice Automation | workflow | Completed | 12 wks | 🟢 |
| Email Nurture Sequence | marketing | In Progress | 4 wks | 🟡 Waiting content |
| Lead Research Pipeline | automation | Delivered | 6 wks | 🟢 |
```

### Step 3: Wins & Value Delivered
Extract wins from project history + notes and quantify where possible:

Look for:
- **Process improvements**: "Reduced order processing time from 3h to 15min" → impact = 12 FTE hours/week
- **Revenue enablement**: "15 new SQLs captured per week via automated lead research"
- **Cost savings**: "Eliminated 5 hours/week manual data entry"
- **Scaling signals**: "QB integration now handling 1,000+ invoices/month with zero errors"

Format:
```
## Wins Since [Engagement Start Date]
- ✅ [Quantified win]: [business impact or metric]
- ✅ [Qualitative improvement]: [operational benefit]
```

If metrics aren't available, use language from client notes and infer impact:
- "Live and processing all xyz" → Stability + scalability win
- "Zero manual intervention" → Reliability + cost savings

### Step 4: Risks & Blockers
Scan project statuses and notes for:

**Explicit blockers:**
- Project in "Planning" for >8 weeks → needs re-engagement
- Status labeled "at-risk" or "blocked"
- Age (weeks) dramatically exceeding similar projects → timeline slip signal

**Implicit risks:**
- No projects in last 30 days → engagement momentum stalled?
- Single project → upsell opportunity missed?
- Type imbalance (only workflow, no marketing) → underutilized relationship?

Format risks as:
```
🔴 [Risk]: [Specific blocker or gap]
   Action: [What we should do about it]
```

### Step 5: Next 30 Days Priorities
Based on project status + engagement history + engagement_type:

For each engagement type, suggest:

**Retainer clients** (ongoing):
1. [Project 1]: Complete [specific milestone]
2. [Project 2]: Begin discovery for [new area]
3. Check-in: Review metrics + discuss expansion opportunities

**Trial program clients** (time-limited testing):
1. [Project]: Complete proof of value
2. Validation call: Confirm ROI + discuss full migration
3. Proposal: Scope for expanded rollout if successful

**Custom project clients** (one-off scope):
1. [Project]: Complete deliverables per contract
2. Post-project review: Measure outcomes, document lessons
3. Proposal: Suggest complementary ongoing services (retainer pivot)

### Step 6: Expansion Opportunities
Based on tags + current projects + engagement duration, identify:

**Horizontal expansion** (adjacent service):
- If workflow automation embedded → pitch marketing automation or lead gen
- If marketing running → pitch automation for underlying ops
- If sales process automated → pitch CRM + billing automation

**Vertical expansion** (deeper in current service):
- If one QB automation live → other integrations (ShipStation, Stripe, etc.)
- If email campaign running → propose nurture sequence + lead scoring

**Scope expansion** (existing project):
- If project stable and handling volume well → "Ready to expand to [adjacent workflow]?"

**Retention risk** (proactive messaging):
- If engagement_type = trial AND no expansion discussion in 60 days → risk of churn

Format:
```
## Expansion Hooks
**Horizontal**: [Adjacent service pitch]
**Vertical**: [Adjacent workflow within current service]
**Scope**: [Expansion of current project]
```

### Step 7: Generate QBR Report

Output a single, scannable Markdown document:

```markdown
# Quarterly Account Review: [Client Name]
**Engagement Date**: [created_at] | **Duration**: [X weeks] | **Status**: [active/trial/paused]
**Engagement Type**: [retainer/trial_program/custom_project]

---

## 📊 Project Status Rollup

[Status table from Step 2]

**Summary**: [1-sentence health of overall account—all green, one blocker, etc.]

---

## ✅ Wins Since [Start Month]

[List from Step 3, quantified where possible]

**Total Impact**: [Estimate of business value or operational efficiency gain]

---

## 🔴 Risks & Blockers

[List from Step 4 with actions]

**Immediate action**: [What we need to do this week]

---

## 📅 Next 30 Days

[Prioritized list from Step 5]

---

## 💡 Expansion Opportunities

[From Step 6]

**Recommended approach**: [How and when to surface the expansion in conversation]

---

## 📞 Call Talking Points

- [Specific win to lead with]
- [Question about expansion area based on current usage]
- [Risk to address proactively or milestone to celebrate]

---

**Next Review**: [90 days from today]
**Prepared by**: Claude | **Date**: [Today]
```

## Examples

### Example 1: Retainer Client – Automation-Focused

**Input:**
```
client_slug: "nexairi-mentis"
```

**Client data:**
```json
{
  "name": "Nexairi Mentis",
  "status": "active",
  "engagement_type": "retainer",
  "created_at": "2025-12-29",
  "projects": [
    {
      "id": "proj-001",
      "title": "QuickBooks Invoice Automation",
      "type": "workflow",
      "status": "Completed",
      "created_at": "2025-12-29",
      "notes": "Live with Shopify integration. Processing 500+ orders/month with zero errors."
    },
    {
      "id": "proj-002",
      "title": "Email Nurture Sequence",
      "type": "marketing",
      "status": "In Progress",
      "created_at": "2026-02-15",
      "notes": "Waiting for content outline from client. Delayed 1 week."
    }
  ]
}
```

**Output:**

```markdown
# Quarterly Account Review: Nexairi Mentis
**Engagement Date**: Dec 29, 2025 | **Duration**: 10 weeks | **Status**: active
**Engagement Type**: retainer

---

## 📊 Project Status Rollup

| Project | Type | Status | Age | Health |
|---------|------|--------|-----|---------|
| QuickBooks Invoice Automation | workflow | Completed | 10 wks | 🟢 Live |
| Email Nurture Sequence | marketing | In Progress | 3 wks | 🟡 Awaiting content |

**Summary**: Core invoicing automation is stable and handling significant volume. Email campaign in progress but blocked on client feedback.

---

## ✅ Wins Since Dec 2025

- ✅ **QB Integration Live**: Processing 500+ orders/month with zero manual intervention
- ✅ **Shopify Sync**: Eliminated daily manual order entry (est. 10 FTE hours/week savings)
- ✅ **Invoice Accuracy**: 100% error-free processing since go-live

**Total Impact**: ~$15K/year in labor cost reduction + risk elimination (no billing errors)

---

## 🔴 Risks & Blockers

🟡 **Email campaign delayed**: Waiting on content outline from client since Feb 15 (11 days)
   Action: Send reminder email today; offer templated outline to accelerate

---

## 📅 Next 30 Days

1. **Email Nurture**: Complete content, launch sequence by Mar 20
2. **QB Expansion**: Discuss ShipStation integration for order-to-shipment automation
3. **Check-in call (Mar 25)**: Celebrate invoicing wins; surface shipping opportunity; discuss H2 retainer priorities

---

## 💡 Expansion Opportunities

**Horizontal**: ShipStation automation (order fulfillment) | **Hook**: "Your invoicing is flawless. Next step—automate the shipment side?"
**Vertical**: Stripe payment sync to QB | **Hook**: "Given the volume you're handling, let's ensure payment reconciliation is automatic too."
**Scope**: Multi-location QB support | **Hook**: "If you expand operations, we scale the integration cost-free."

---

## 📞 Call Talking Points

- "Your QB integration is processing 500+ orders/month with zero errors—best in class for your volume."
- "That's saved you roughly 10 hours a week in manual order entry. What's next on your wish list?"
- "We're getting excited about the shipping side—same automation principle could knock days off your fulfillment cycle. Interested in exploring?"
- "Email campaign launching soon. Once we prove lead quality, we could talk inbound strategy expansion."

---

**Next Review**: June 9, 2026
**Prepared by**: Claude | **Date**: Mar 9, 2026
```

### Example 2: Trial Program Client – New Engagement

**Input:**
```
client_slug: "acme-manufacturing"
```

**Client data:**
```json
{
  "name": "Acme Manufacturing",
  "status": "active",
  "engagement_type": "trial_program",
  "created_at": "2026-02-03",
  "projects": [
    {
      "id": "proj-101",
      "title": "Sales Lead Research Automation",
      "type": "automation",
      "status": "Delivered",
      "created_at": "2026-02-03",
      "notes": "Identifying 15 qualified leads/week via automated research. Quality confirmation pending client validation."
    }
  ]
}
```

**Output:**

```markdown
# Quarterly Account Review: Acme Manufacturing
**Engagement Date**: Feb 3, 2026 | **Duration**: 5 weeks | **Status**: active
**Engagement Type**: trial_program (PROOF-OF-VALUE PHASE)

---

## 📊 Project Status Rollup

| Project | Type | Status | Age | Health |
|---------|------|--------|-----|---------|
| Sales Lead Research Automation | automation | Delivered | 5 wks | 🟢 Live |

**Summary**: MVP delivered on schedule. Currently validating output quality with client.

---

## ✅ Wins Since Feb 3

- ✅ **Lead Research System Live**: Generating ~15 qualified leads per week
- ✅ **On-Time Delivery**: MVP completed in 4 weeks per contract
- ✅ **Adoption Signal**: Client requesting lead export weekly (signal of engagement)

**Total Impact**: ~60 qualified leads in first month (vs. their est. 5-10 lead/month baseline)

---

## 🔴 Risks & Blockers

🟡 **Lead Quality Validation Pending**: Client has not yet confirmed lead quality metrics. Critical for trial success.
   Action: Schedule validation call this week; use agreed-upon criteria to measure false positive rate

---

## 📅 Next 30 Days (Critical)

1. **Validation Meeting (Due Mar 12)**: Review lead quality with client; confirm ROI threshold is met
   - Success metric: >70% of leads are "relevant" per their definition
   - Decision point: Proceed to expansion or adjust research parameters?
2. **Expansion Proposal (If approved)**: Pitch ShipStation automation or sales pipeline CRM automation
3. **Renewal/Scope Decision (By Mar 30)**: Transition from trial → custom project or retainer

---

## 💡 Expansion Hooks

**Alternative Play 1**: If lead quality validates, propose **Sales Process Automation** (pipeline CRM sync)
**Alternative Play 2**: If lead volume proves insufficient, pivot to **Inbound Content** (attract leads organically)
**Retention Risk**: Trial ends in 9 weeks; need clear success/failure decision by EOQ

---

## 📞 Call Talking Points

- "We've delivered 60 qualified leads in your first month. How are your sales reps responding?"
- "Let's validate these are hitting your quality bar—then we can talk scale or next automation."
- "If this proves the ROI, next phase could be: pipeline CRM automation or inbound strategy. Interested?"

---

**Critical Date**: Trial Decision Point by Mar 30, 2026
**Next Review**: June 3, 2026 (only if successful renewal)
**Prepared by**: Claude | **Date**: Mar 9, 2026
```

## Edge Cases & Mitigation

**No projects yet (recently onboarded):**
- Return: "Engagement initiated [X days ago]. No completed projects yet. Recommend first check-in around day 30 to validate initial deliverables are tracking."

**All projects stalled for >60 days:**
- Flag as engagement risk
- Recommendation: "Proactive outreach needed. Assess if engagement is still valued or if scope mismatch exists."

**Trial program past expected duration:**
- Check if trial was extended or converted
- Recommend: "Clarify trial status immediately and propose conversion path."

**Client status = "paused" or "completed":**
- Return: "This engagement is [paused/completed]. QBR not actionable. Recommend reactivation discussion or archival."

**Multiple projects of same type:**
- Group by type in table summary
- Example: "3 workflow automation projects live, 2 at-risk"

## Output Quality Checklist

Before returning to user:
- [ ] Project status table is complete + accurate against client.json
- [ ] All wins are quantified or have business impact statement
- [ ] Risks have explicit mitigation actions
- [ ] Next 30 days are specific, assignable tasks (not vague goals)
- [ ] Expansion hooks are tailored to actual client data (not generic)
- [ ] Call talking points are immediately usable (copy-paste friendly)
- [ ] QBR is under 400 lines and scannable in <3 minutes
- [ ] Engagement type determines tone (trial = urgent validation; retainer = proactive expansion)

## Integration with Admin Clients Page

**Workflow trigger:**
1. Admin opens client drawer (from /admin/clients table)
2. Clicks "Account Review" button in Overview tab
3. Triggers this skill with client_slug
4. Returns QBR as markdown → displayed in modal or downloadable
5. User can copy/paste talking points into call notes

**Integration points:**
- Feeds into: `customer-sales` skill for renewal/expansion conversations
- Complements: `data-analysis-reporting` for deeper metric analysis
- Pair with: `client-discovery` for newly added clients

## Reference: Project Status Definitions

Use these standardized statuses consistently:

| Status | Meaning | Action Needed |
|--------|---------|----------------|
| **Planning** | Scoped but not started | Confirm kickoff date or note blocker |
| **In Progress** | Active development/delivery | Track blockers, timeline, dependencies |
| **Delivered** | Completed and handed off | Monitor adoption, measure impact |
| **Completed** | Delivered + proven stable in production | Track for wins, assess expansion |
| **Paused** | Temporarily halted | Note reason, recovery timeline |
| **Blocked** | Cannot progress without external input | Timeline for resolution |
