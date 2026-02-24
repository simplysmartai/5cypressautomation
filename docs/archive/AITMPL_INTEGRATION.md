# aitmpl Template Integration Guide

## Overview
This guide explains how to integrate the aitmpl.com agent templates into Simply Smart Automation's 3-layer architecture to build and sell high-value B2B automation services.

---

## Layer Architecture Recap

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: DIRECTIVES (What to do)                            │
│ Natural language SOPs that define goals, inputs, outputs     │
│ Files: directives/*.md                                       │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│ Layer 2: ORCHESTRATION (Decision making)                    │
│ AI agents route work through intelligent logic               │
│ YOU as the orchestrator (reading directives, calling tools)  │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│ Layer 3: EXECUTION (Doing the work)                         │
│ Deterministic Python scripts + aitmpl agents                │
│ Files: execution/*.py (call aitmpl APIs)                    │
└─────────────────────────────────────────────────────────────┘
```

---

## How aitmpl Templates Fit In

**aitmpl agents = Layer 3 execution tools**

Instead of writing all business logic from scratch, use aitmpl's pre-built agents:
- **Search Specialist** agent → Lead research execution
- **Business Analyst** agent → Data analysis & scoring
- **Legal Advisor** agent → Document review & compliance
- **Content Marketer** agent → Copy generation
- **etc.**

Your orchestrator scripts (Layer 3) call these agents via API, transforming their outputs into your specific formats and workflows.

---

## Integration Steps (Quick Summary)

### Step 1: Install aitmpl Templates
```bash
# Install by category
npx claude-code-templates@latest --agent=ai-specialists/search-specialist --yes
npx claude-code-templates@latest --agent=business-marketing/business-analyst --yes
npx claude-code-templates@latest --agent=business-marketing/legal-advisor --yes
npx claude-code-templates@latest --agent=business-marketing/content-marketer --yes
npx claude-code-templates@latest --agent=business-marketing/marketing-attribution-analyst --yes
npx claude-code-templates@latest --agent=business-marketing/payment-integration --yes
npx claude-code-templates@latest --agent=business-marketing/customer-support --yes
```

These templates install into your VS Code environment and are now available via API.

### Step 2: Map Templates to Directives
Each directive calls 1-2 aitmpl agents in its execution layer:

| Directive | Primary Agent | Secondary Agent | Purpose |
|-----------|---------------|-----------------|---------|
| `lead_research_service.md` | Search Specialist | Business Analyst | Find + score prospects |
| `sales_analytics_service.md` | Business Analyst | Marketing Attribution Analyst | Pipeline KPIs |
| `automated_documents_service.md` | Legal Advisor | Content Marketer | PDF generation |
| `internal_lead_generation.md` | Search Specialist | Business Analyst | SSA's own lead gen |

### Step 3: Wrap Agents with Execution Scripts
Each execution script (Python) acts as a bridge:
- Accepts directive inputs (client config, data)
- Calls aitmpl agent with structured prompt
- Transforms agent output to your format
- Delivers to Google Sheets/PDF/etc.

Example: `execution/lead_research_orchestrator.py`
```python
# Pseudocode
def research_phase():
    # Call aitmpl Search Specialist agent
    results = call_aitmpl_agent(
        agent_name="search_specialist",
        task="Find prospects matching ICP",
        params=config['icp']
    )
    return results

def scoring_phase(leads):
    # Call aitmpl Business Analyst agent
    scored = call_aitmpl_agent(
        agent_name="business_analyst",
        task="Score leads on fit",
        params=leads
    )
    return scored
```

### Step 4: Deploy as Services
Each directive becomes a sellable service:
- **Lead Research Service** - $1,500-3,000/mo
- **Sales Analytics Service** - $600-2,000/mo
- **Automated Documents Service** - $500-2,000/mo
- **Email Campaign Service** - $400-1,500/mo
- **etc.**

---

## API Integration Examples

### Calling aitmpl Agents from Python

**Option 1: Via Claude API (recommended)**
```python
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Example: Call Search Specialist
def call_search_specialist(company_profile: dict) -> list:
    response = client.messages.create(
        model="claude-opus-4.1",
        max_tokens=4096,
        system="""You are a Search Specialist agent. Your job is to:
        1. Research companies matching the provided profile
        2. Find contact information
        3. Identify buying signals
        Use web search, LinkedIn, CrunchBase, and news sources.""",
        messages=[
            {
                "role": "user",
                "content": f"""Find 50 prospects matching this ICP:
                {json.dumps(company_profile, indent=2)}
                
                Return results as JSON array with fields:
                - company_name
                - contact_name
                - title
                - email
                - linkedin_url
                - buying_signals
                """
            }
        ]
    )
    
    # Parse results from Claude
    results = json.loads(response.content[0].text)
    return results
```

**Option 2: Direct aitmpl SDK (if available)**
```python
from aitmpl import agents

search_specialist = agents.SearchSpecialist()
leads = search_specialist.research(
    industries=["SaaS", "Digital Agencies"],
    company_size=[10, 500],
    target_titles=["VP Sales"],
)
```

### Transforming Agent Outputs

Agents return unstructured data → your scripts transform to your format:

```python
def format_for_sheets(agent_results: dict) -> list:
    """Transform Search Specialist output to Google Sheets format."""
    return [
        {
            'Company': result['company_name'],
            'Contact': result['contact_name'],
            'Email': result['email'],
            'Fit Score': calculate_score(result),  # Your scoring logic
            'Recommended Action': get_action(score),
        }
        for result in agent_results['leads']
    ]
```

---

## Directive Examples

### Example 1: lead_research_service.md

**Input:** Client config (ICP, titles, geography)  
**Flow:**
1. Call aitmpl Search Specialist → Find 50-100 prospects
2. Call aitmpl Business Analyst → Score each lead 0-100
3. Format for Google Sheets
4. Auto-add to client's CRM (Zapier)

**Output:** Weekly Google Sheet with scored leads

---

### Example 2: sales_analytics_service.md

**Input:** CRM credentials (HubSpot, Salesforce, etc)  
**Flow:**
1. Fetch deals from CRM API
2. Call aitmpl Business Analyst → Calculate KPIs
3. Call aitmpl Marketing Attribution Analyst → Bottleneck analysis
4. Generate forecast
5. Create multi-tab Google Sheets dashboard

**Output:** Real-time dashboard + monthly PDF executive summary

---

### Example 3: automated_documents_service.md

**Input:** Document type + client details (company name, counterparty, fee, etc)  
**Flow:**
1. Call aitmpl Content Marketer → Generate document content
2. Call aitmpl Legal Advisor → Review for compliance
3. Apply branding (logo, colors)
4. Generate PDF with signature fields
5. Store in Google Drive + send to client

**Output:** Professional branded PDF ready to sign

---

## Deployment Options

### Option A: Webhook-Based (Recommended for SaaS)

```
Client requests document → POST to webhook → Orchestrator runs → Outputs to Drive
```

**Setup:**
1. Deploy orchestrator as Modal webhook
2. Client calls webhook with params
3. Orchestrator returns URL to generated document

**Benefit:** Scalable, serverless, automatic

---

### Option B: Scheduled (For batch processing)

```
Daily 6am: Orchestrator runs → Updates Google Sheet with new leads
```

**Setup:**
1. Schedule via cron / GitHub Actions / Modal
2. Orchestrator fetches latest data from research APIs
3. Stores results in shared Google Sheet

**Benefit:** Predictable, cost-efficient

---

### Option C: Direct Integration (For clients with n8n)

```
n8n workflow → Calls execution script → Orchestrator handles heavy lifting
```

**Setup:**
1. Client's n8n instance calls your orchestrator
2. Passes through CRM data, client config, etc
3. Gets back processed results

**Benefit:** Deep integration with client's existing workflows

---

## Service Packaging Examples

### Service 1: Lead Research Service ($1,500/mo)

**What client gets:**
- Weekly Google Sheet with 30-50 new leads
- Scored 0-100 on fit
- Included: company info, contact, email, LinkedIn
- Auto-sync to Salesforce/HubSpot (if connected)

**Your costs:**
- API calls: ~$50/mo (aitmpl usage)
- Hosting: ~$20/mo (Modal)
- Your time: 30 min/week (review + optimize)

**Margin:** ~95%

---

### Service 2: Sales Analytics Dashboard ($1,200/mo)

**What client gets:**
- Real-time Google Sheets dashboard
- Updated every 24 hours from their CRM
- KPIs, bottleneck analysis, forecasting
- Monthly PDF executive summary

**Your costs:**
- API calls: ~$30/mo
- Hosting: ~$20/mo
- Your time: 1 hour/month (tuning)

**Margin:** ~96%

---

### Service 3: Automated Documents ($800/mo)

**What client gets:**
- Unlimited document generation (contracts, proposals, policies)
- Branded PDFs
- Legal compliance (GDPR, CCPA, etc)
- 24-hour turnaround

**Your costs:**
- API calls: ~$40/mo
- Hosting: ~$20/mo
- Your time: 30 min/mo (template updates)

**Margin:** ~92%

---

## Revenue Projection

**Conservative estimate (Year 1):**

| Service | Launch | Clients (Yr 1) | Price | Annual Revenue |
|---------|--------|----------------|-------|----------------|
| Lead Research | Month 1 | 5 | $1,500/mo | $90K |
| Sales Analytics | Month 2 | 8 | $1,200/mo | $115K |
| Auto Documents | Month 3 | 12 | $800/mo | $115K |
| Email Campaigns | Month 5 | 6 | $900/mo | $65K |
| Landing Pages | Month 6 | 10 | $600/mo | $72K |
| Support System | Month 8 | 8 | $500/mo | $48K |
| **TOTAL** | — | **49** | — | **$505K** |

*Assumptions: 20% adoption rate, no churn, no upgrades*

---

## Implementation Checklist

### Week 1-2: Setup
- [ ] Install aitmpl templates locally
- [ ] Review agent capabilities (read their docs)
- [ ] Set up API keys and credentials
- [ ] Create config templates for each service

### Week 2-4: Development
- [ ] Build 3 execution orchestrators (lead gen, analytics, documents)
- [ ] Write directives for each service
- [ ] Test with mock data
- [ ] Create Google Sheets templates

### Week 4-5: Testing
- [ ] Test with real client data (1-2 pilot clients)
- [ ] Measure output quality
- [ ] Refine scoring models / templates
- [ ] Document any edge cases

### Week 5-6: Launch
- [ ] Price services
- [ ] Create sales materials
- [ ] Onboard first 3-5 paying clients
- [ ] Set up support/feedback loop

---

## Key Files Created

```
agents/
├── document-generation/
├── lead-generation/
├── sales-analytics/
├── marketing-automation/
├── payment-operations/
└── customer-success/

directives/
├── lead_research_service.md
├── sales_analytics_service.md
├── automated_documents_service.md
├── internal_lead_generation.md
├── [future: email_campaign_service.md]
├── [future: landing_page_service.md]
└── [future: customer_support_service.md]

execution/
├── lead_research_orchestrator.py
├── sales_analytics_orchestrator.py
├── document_generator.py
├── [TODO: agent wrappers for each aitmpl agent]
└── [TODO: Google Sheets API integration]

config/
├── internal_lead_gen_config.json
└── [clients will have individual configs]

.tmp/
├── lead_research/        # Intermediate lead files
├── sales_analytics/      # Intermediate CRM data
└── documents/            # Generated PDFs (transient)

SERVICES_ROADMAP.md       # This roadmap
AITMPL_INTEGRATION.md     # This guide
```

---

## Next Steps

1. **Install aitmpl templates** (30 min)
   - Run installation commands above

2. **Test agent APIs** (1 hour)
   - Call each agent with sample data
   - Review output format

3. **Build agent wrappers** (4 hours)
   - Create Python functions that call agents
   - Handle errors and formatting

4. **Extend execution scripts** (completed)
   - Replace mock data with real agent calls

5. **Test with real clients** (ongoing)
   - Pilot 2-3 services with early adopters
   - Gather feedback
   - Iterate

6. **Launch publicly** (Week 6)
   - Create website landing pages per service
   - Set up payment system (Stripe)
   - Start selling

---

## Support & Resources

- **aitmpl docs:** https://docs.aitmpl.com/
- **Claude API docs:** https://docs.anthropic.com/
- **Google Sheets API:** https://developers.google.com/sheets
- **Your 3-layer architecture guide:** See AGENTS.md, CLAUDE.md, GEMINI.md

---

## Questions to Ask Yourself

1. **Which service should we launch first?**
   - Answer: Lead Research (fastest ROI, easiest implementation)

2. **How do we handle customer support?**
   - Answer: Start with async Slack support, plan for dedicated support agent later

3. **What if an agent produces low-quality output?**
   - Answer: Implement quality checks in execution scripts, implement feedback loop to retrain

4. **How do we price these services?**
   - Answer: Start with 30-day free trial for early customers, gather usage data, optimize pricing

5. **Can we white-label these services?**
   - Answer: Yes—execution scripts don't care about branding, just replace logo/colors in templates

---

## Success Metrics

Track these to measure implementation success:

| Metric | Target | Timeline |
|--------|--------|----------|
| # of services launched | 3 | Week 6 |
| # of pilot clients | 2-3 | Week 5 |
| Avg client satisfaction | 90%+ | Month 2 |
| MRR from services | $5K+ | Month 3 |
| # of agent API calls/month | 10K+ | Month 3 |
| Customer acquisition cost (CAC) | <$500 | Month 2 |
| Gross margin per service | >90% | Ongoing |

---

## Stay Updated

As you implement, keep these documents updated:
- **SERVICES_ROADMAP.md** - Update timelines and learnings
- **Individual directives** - Document edge cases and improvements
- **Execution scripts** - Comment on what worked, what didn't
- This guide - Add lessons learned, gotchas, best practices

The system improves as you execute. Self-anneal constantly.
