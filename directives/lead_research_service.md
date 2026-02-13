# Lead Research & Scoring Service

## Overview
Autonomous lead research engine that identifies, researches, and scores qualified prospects for B2B sales teams. Delivers weekly lead lists with contact info and fit scoring.

## Service Tier

**Monthly Fee:** $1,500 - $3,000  
**Deliverable:** Google Sheet (updated weekly) with scored leads + monthly PDF summary  
**Agent Template:** Search Specialist + Deep Research Team  

---

## Inputs (Client Provides)

### Required
1. **Target Industries** (array)
   - Example: `["SaaS", "Digital Agencies", "eCommerce", "Professional Services"]`

2. **Ideal Customer Profile (ICP)**
   - Company size: `[10-100 employees]`
   - Revenue range: `[$1M-$10M ARR]`
   - Geographic focus: `[US, Canada, UK]`
   - Key buying signals: `[recent funding, new hire in sales, product launch]`

3. **Contact Criteria**
   - Titles to target: `["VP Sales", "Sales Manager", "Business Development", "Founder"]`
   - Email format preferences: `[firstname.lastname@company, etc]`

4. **Integration Details** (for CRM/email platform)
   - Salesforce account ID / HubSpot workspace ID (optional)
   - Zapier webhook endpoint (for auto-sync)

### Optional
- Exclude list (competitors, past contacts)
- Geographic exclusions
- Company blacklist (bad fit customers)

---

## Process

### Step 1: Research Design (Orchestration Layer)
*Directive triggers orchestrator: `execution/lead_research_orchestrator.py`*

1. Parse ICP from client config
2. Identify 5-10 research vectors:
   - Company tech stack + growth signals
   - Recent funding/hiring announcements
   - Product launches or expansion signals
   - Engagement on relevant content/events
   - LinkedIn activity from target titles

### Step 2: Data Gathering (Search Specialist Agent)
Agent uses:
- LinkedIn searches (ICP profile matching)
- CrunchBase/news APIs (funding, hiring)
- Industry databases (ZoomInfo equivalent)
- Public web research (company news, job postings)

**Constraints:**
- No paid data sources (use free/API-based only, or client pays data costs)
- Respect rate limits (space requests over week)
- Verify email accuracy to <5% bounce rate

### Step 3: Lead Scoring (Business Analyst Agent)
Score each prospect 0-100 on:

| Factor | Weight | How Scored |
|--------|--------|-----------|
| **ICP Fit** | 40% | Company size, industry, revenue match |
| **Buying Signal** | 35% | Recent funding, hiring, product news, job posting |
| **Title Match** | 15% | Is prospect decision-maker? |
| **Engagement** | 10% | LinkedIn activity, content engagement |

**Scoring Logic:**
- 80-100: Contact immediately (hot prospect)
- 60-79: Add to nurture sequence
- 40-59: Monitor, re-score monthly
- <40: Archive

### Step 4: Enrichment & Export
For each lead:
- Company name, website, industry
- Contact name, title, email (verified), LinkedIn
- Company size, revenue estimate, funding status
- Buying signals found
- Fit score + reason
- Recommended next action (cold email / LinkedIn / inbound trigger)

**Output Format:** Google Sheet (see Template below)

### Step 5: Delivery
- **Weekly:** Auto-update Google Sheet (every Monday)
- **Monthly:** PDF summary (top 20 leads, trends, insights)
- **Real-time:** Zapier webhook when score >75 (auto-add to Salesforce, HubSpot)

---

## Output Template

**Google Sheet Name:** `{ClientName}_Weekly_Leads_{WeekOf}`

| Company | Contact | Title | Email | LinkedIn | Company Size | Funding Status | Buying Signal | Fit Score | Recommended Action | Follow-up Week |
|---------|---------|-------|-------|----------|--------------|----------------|----------------|-----------|------------------|----------------|
| Acme Corp | John Smith | VP Sales | john.smith@acmecorp.com | /in/johnsmith | 50-200 | Series B (6mo) | "Hired 3 SDRs" | 88 | Cold email | Week 2 |
| TechStart Inc | Sarah Chen | VP Marketing | sarah.chen@techstart.io | /in/sarahchen | 10-50 | Series A (2yr) | Product launch (blog post) | 72 | LinkedIn touch | Week 3 |

---

## Execution Checklist

- [ ] Client config sheet created (ICP, criteria, exclusions)
- [ ] Google Sheet template created (branded with client logo)
- [ ] Research vectors configured (which APIs/data sources enabled)
- [ ] Lead scoring formula tuned to client's past win profiles
- [ ] First batch of 50+ leads researched and scored
- [ ] Zapier/webhook integration tested (auto-sync to CRM)
- [ ] Weekly automation scheduled (Monday 9am)
- [ ] Sample PDF monthly summary generated
- [ ] Client training call (how to use, customize, iterate)

---

## Success Metrics

- **Lead Quality:** % of leads that respond to outreach (target: >15%)
- **Fit Accuracy:** % of scored leads that match ICP (target: >90%)
- **Speed:** Time from research → export (target: <24hrs for batch)
- **Refresh Rate:** % new leads weekly that haven't been contacted (target: 20-30 new/week)

---

## Continuous Improvement Loop

**Weekly Review:**
1. Check % of scored leads that convert to opps
2. Identify scoring model biases (e.g., overweighting tech stack)
3. Refine buying signals based on actual conversions
4. Adjust inclusion/exclusion rules

**Monthly Tune-up:**
1. Compare actual winners vs predicted fit scores
2. Rebuild scoring formula with 12-month win data
3. Expand research vectors if high-quality leads plateau
4. Client feedback call (what's working, what to change)

---

## Edge Cases & Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Low lead quality | ICP too broad | Narrow to 1-2 industries, verify past customers fit criteria |
| High duplicate rate | Research vectors overlap | Consolidate data sources, deduplicate by email |
| Email bounce rate >10% | Data source inaccuracy | Switch to premium data source or client provides verified list |
| Leads already contacted | No exclusion list provided | Add company blacklist + contact deduplication |
| Slow research | Too many research vectors | Prioritize 3 best vectors, remove low-signal ones |

---

## Related Directives

- `directives/internal_lead_generation.md` - SSA's own lead gen (uses same framework)
- `directives/sales_analytics_service.md` - Track which leads convert (feedback loop)

## Related Execution Scripts

- `execution/lead_research_orchestrator.py` - Main orchestrator
- `execution/search_specialist_agent.py` - Data gathering wrapper
- `execution/business_analyst_agent.py` - Scoring logic
- `execution/lead_export_formatter.py` - Google Sheets export
