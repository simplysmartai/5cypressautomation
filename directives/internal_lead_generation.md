# Internal Lead Generation Workflow

## Overview
Daily autonomous lead research workflow for 5 Cypress Labs' own sales pipeline. Uses the same Lead Research Service framework to identify and score prospects in the B2B automation/consulting space.

## Objectives

1. **Generate 5-10 qualified leads daily** for the sales team to contact
2. **Build evergreen lead database** (organized by industry/stage) for long-term pipeline building
3. **Identify inbound-ready accounts** that show strong buying signals
4. **Feed into manage_pipeline.md** workflow for tracking and outreach

---

## Target ICP (5 Cypress Labs)

### Industries
- SaaS companies (5-500 employees)
- Digital Agencies
- eCommerce businesses
- Professional services firms
- B2B Consulting
- Insurance/FinTech

### Company Criteria
- Revenue: $1M-$50M (early growth or established)
- Geography: US, Canada, UK, EU
- Growth signals: Recent funding, hiring spree, new product launch, acquisition activity

### Decision Maker Titles
- VP Sales
- VP Operations
- VP Marketing
- VP Revenue
- Founder (startup CEO)
- Head of Business Development
- Chief Operating Officer (COO)

### Buying Signals (Scored High)
- Hired VP Sales or Sales Manager in last 90 days
- Funding event (Series A/B, growth rounds)
- Job postings for sales/operations roles
- Product launch or major feature announcement
- Company expansion into new markets
- M&A activity (acquisition target or acquirer)
- Mention on major news/press sites

---

## Process

### Daily Execution (Automated, 6am)

1. **Run orchestrator**
   ```bash
   python execution/lead_research_orchestrator.py \
       --client-id simply-smart-automation \
       --config config/internal_lead_gen_config.json \
       --output-sheet {LEAD_GEN_SHEET_ID}
   ```

2. **Output**
   - 50-100 leads researched
   - Scored and categorized
   - Appended to Google Sheet (cumulative database)
   - Leads with score >80 trigger immediate Slack notification

3. **Sales team action**
   - Check Slack notification for hot leads
   - Review daily digest in Google Sheets
   - Add high-quality leads to sales pipeline (via manage_pipeline.md)

### Weekly Review

Every Monday 10am:
1. Analyze last week's lead quality (% contacted, % responded, % qualified)
2. Refine targeting if needed (adjust ICP, buying signals)
3. Identify best-performing industries/signals
4. Update config for next week's research

### Monthly Analysis

1. Score leads that were contacted → measure conversion to opps
2. Identify which buying signals correlate with actual wins
3. Rebuild scoring model based on conversions
4. Expand research to new industries or signals if quality drops

---

## Configuration

**File:** `config/internal_lead_gen_config.json`

```json
{
  "client_name": "Simply Smart Automation",
  "icp": {
    "industries": [
      "SaaS",
      "Digital Agencies",
      "eCommerce",
      "Professional Services",
      "Consulting",
      "B2B SaaS"
    ],
    "company_size": [10, 500],
    "revenue_range": ["$1M", "$50M"],
    "geography": ["US", "Canada", "UK", "EU"]
  },
  "target_titles": [
    "VP Sales",
    "VP Operations",
    "VP Marketing",
    "Founder",
    "Chief Revenue Officer",
    "Chief Operating Officer",
    "VP Business Development",
    "Head of Sales",
    "Sales Director"
  ],
  "buying_signals": [
    "recent_hiring_sales",
    "recent_funding",
    "product_launch",
    "job_postings",
    "press_mentions",
    "market_expansion",
    "acquisition_activity"
  ],
  "research_vectors": {
    "linkedin": true,
    "crunchbase": true,
    "news_api": true,
    "industry_reports": true,
    "job_boards": true
  },
  "exclude_list": [
    "existing_customers",
    "existing_prospects",
    "competitors",
    "known_tire_kickers"
  ],
  "daily_lead_target": 50,
  "min_fit_score_for_contact": 75
}
```

---

## Google Sheet Structure

**Master Lead Database:** `Simply Smart Automation - Lead Gen`

### Sheet 1: Weekly Leads (Latest)
Filtered to last 7 days, sorted by score descending

| Company | Contact | Title | Email | LinkedIn | Industry | Funding Status | Buying Signal | Fit Score | Date Added | Status |
|---------|---------|-------|-------|----------|----------|----------------|-------------|----------|-----------|--------|
| TechStart Inc | Sarah Chen | VP Sales | sarah.chen@... | /in/sarah | SaaS | Series B | "Hired 3 SDRs" | 88 | 2025-01-20 | New |
| Acme Corp | John Smith | Founder | john@acme.com | /in/john | eCommerce | Bootstrap | "Product launch" | 82 | 2025-01-20 | Contacted |

### Sheet 2: All Leads (Cumulative)
Master database, all leads ever researched, never deleted (for historical reference)

### Sheet 3: Analytics
- Daily lead count trend
- Average fit score trend
- Conversion rate (contacted → response → qualified)
- Best-performing industries
- Best-performing buying signals

### Sheet 4: Pipeline Integration
Links to `manage_pipeline.md` sheet, shows which leads have been added to sales pipeline and their progression

---

## Scoring Breakdown (0-100)

### ICP Fit (40%)
- Company size match: +0-25 points
- Industry match: +0-20 points
- Geographic fit: +0-15 points
- Revenue range fit: +0-20 points

### Buying Signals (35%)
- Recent funding: +30 points
- Recent hiring (VP Sales/Operations): +25 points
- Product launch: +20 points
- Job postings for sales roles: +15 points
- M&A activity: +20 points
- News mentions: +10 points

### Title Match (15%)
- Perfect match (VP Sales, CRO, COO): +15 points
- Good match (Sales Dir, VP Operations): +10 points
- Okay match (Sales Manager, Head of Biz Dev): +5 points

### Engagement (10%)
- LinkedIn activity (recent posts, engagement): +10 points
- Company social activity: +5 points

---

## Success Metrics

| Metric | Current | Target | How Measured |
|--------|---------|--------|-------------|
| Leads researched daily | TBD | 50-100 | Count from orchestrator output |
| Avg fit score | TBD | 65+ | Average of all daily leads |
| High-quality leads (80+) | TBD | 8-15 per week | Count of leads scoring 80+ |
| Contact rate | TBD | >40% | % of leads contacted within 2 weeks |
| Response rate | TBD | >15% | % of contacted leads that respond |
| Qualified opportunity rate | TBD | >5% | % of responses that become opps |
| Monthly pipeline contribution | TBD | $250K+ | Pipeline value from internal lead gen |

---

## Actions by Score

| Score | Recommendation | Action | Timeline |
|-------|----------------|--------|----------|
| 80-100 | Contact immediately | Cold email + LinkedIn outreach | Within 48 hours |
| 60-79 | Add to nurture | LinkedIn connection, follow content | Ongoing |
| 40-59 | Monitor | Re-score monthly | Monthly |
| <40 | Archive | Keep in database, don't contact | — |

---

## Integration with Other Directives

- **manage_pipeline.md** - Import high-scoring leads into pipeline tracker
- **discovery_call.md** - Framework for initial outreach to leads
- **sales-to-qbo.md** - Track lead-to-revenue metrics
- **lead_research_service.md** - Same framework, applied to this internal workflow

---

## Optimization Loop

### Weekly (Every Monday)
1. Check last week's leads → how many were contacted?
2. Which buying signals had highest conversion?
3. Which industries are hottest right now?
4. Refine research vectors if needed

### Monthly (First Monday)
1. Full analysis of scored leads vs actual outcomes
2. Update ICP based on best customers
3. Rebuild scoring model with win data
4. Expand to new industries if opportunity identified

### Quarterly
1. Deep dive: which signals predict best customer fit?
2. Compare lead quality across seasons
3. Benchmark against industry (if data available)
4. Plan improvements for next quarter

---

## Execution Checklist

- [ ] Internal lead gen config created
- [ ] Google Sheets master database set up
- [ ] Daily orchestrator scheduled (6am cron job)
- [ ] Slack notifications configured (score >80)
- [ ] Sales team trained on how to use leads
- [ ] First week of leads collected and reviewed
- [ ] Scoring model tuned to initial results
- [ ] Weekly review process documented
- [ ] Pipeline integration tested
- [ ] Metrics dashboard created

---

## Estimated Impact (Annual)

**Assumptions:**
- 50 leads/day researched = 1,200 leads/month
- 15% are high quality (80+ score) = 180/month
- 40% contact rate = 72 contacted/month
- 15% response rate = 11 responses/month
- 5% qualified opportunity rate = 0.55 opps/month (~7/year)
- $100K average deal size = **$700K annual pipeline**

**Cost:** ~2 hours/month human review + orchestration time  
**ROI:** Significant if even 1-2 deals close per year

---

## Future Enhancements

- [ ] Integrate with Apollo.io / Hunter.io for verified emails
- [ ] Add company technographic scoring (tech stack analysis)
- [ ] Connect to LinkedIn Sales Navigator for account research
- [ ] Build predictive scoring (ML model trained on past wins)
- [ ] Auto-trigger email sequences to leads (via Zapier/n8n)
- [ ] Integrate with Salesforce/HubSpot for automatic CRM sync
