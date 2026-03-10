---
name: client-discovery
description: "Generate structured intelligence briefs for new clients and prospects added to the admin page. Use this skill ANY TIME a new client is added to the system, a prospect enters the pipeline, or you need to research a company for initial positioning. Also use when the user says 'research this client', 'what should we pitch to them', 'intelligence brief', or 'first-call profile.' Takes a company name and URL → outputs a structured brief matching client.json schema with business model analysis, pain points aligned to 5 Cypress services, recommended engagement approach, and pre-populated client fields ready for the admin form."
compatibility: "Requires access to web search (semantic search, fetch_webpage tools), 5 Cypress context files (CLAUDE.md, context/agency.md), and client.json schema. Works alongside customer-sales skill for deeper outreach prep."
---

# Client Discovery

<!-- SKILL METADATA
skill_id:  client-discovery
version:   1.0.0
domain:    sales+operations
reviewed:  2026-03-09
status:    READY_FOR_TESTING
changelog:
  1.0.0 - Initial version: intelligence brief generation for new clients
-->

Generate a structured intelligence brief for a new client or prospect entering the 5 Cypress pipeline. This bridges discovery and onboarding by turning public company data into actionable client profiles that immediately feed into the admin clients interface.

## Overview

When a new client is added to the admin page or a prospect enters the pipeline, you need three things fast:
1. **What does this company actually do?** (Business model, size, market position)
2. **Why are they likely to need us?** (Pain points → 5 Cypress service fit)
3. **How should we position in the first call?** (Recommended engagement angle + key talking points)

This skill takes a company name + website → produces a client intelligence brief (Markdown report) that pre-populates the client.json fields and arms your sales team with context before outreach.

## Core Workflow

### Step 1: Validate & Gather Company Data
- Accept inputs: `company_name` (required), `website` (optional), `contact_name` (optional), `industry_hint` (optional)
- If website provided, fetch the homepage → extract: description, services, team size signals, recent features/news
- If website absent, use semantic search for the company + industry to find their online presence
- Capture: business description, target market, product/service category, team size signals, recent moves (funding, new products, partnerships)

### Step 2: Business Model Analysis
- Identify revenue model: B2B SaaS, B2C, services, hybrid, etc.
- Assess operational complexity: simple/manual workflows vs. complex multi-system dependencies
- Note: revenue per employee, order frequency, operational scale (factors determining automation ROI)
- Document: current systems signals (if visible from website: mentions of Shopify, QuickBooks, Salesforce, etc.)

### Step 3: Pain Point Mapping
For each identified operational area, map to 5 Cypress capabilities:

| 5 Cypress Service | Triggered When Company Has... | Keywords to Detect |
|---|---|---|
| **QuickBooks Invoicing** | Order management + payment processing mentioned | "invoicing", "payment", "billing", "orders" |
| **ShipStation Automation** | Order fulfillment or shipping mentioned | "shipping", "fulfillment", "logistics", "warehouse", "3PL" |
| **Lead Generation** | Sales-driven business, mentions of pipeline/prospecting | "sales", "leads", "pipeline", "customer acquisition" |
| **SEO/Content** | B2B positioning, mentions of marketing/thought leadership | "marketing", "content", "visibility", "rankings" |
| **Automation (Workflow)** | Manual processes mentioned or visible inefficiency signals | "process", "workflow", "integration", "data entry" |

### Step 4: Recommended Engagement Approach
Based on identified pain points + business model, recommend:
- **Primary service angle**: Which 5 Cypress service to lead with
- **Secondary opportunities**: 2-3 follow-on services once primary is embedded
- **Conversation hook**: Specific challenge to ask about in first call (signals you've done homework)
- **Timeline estimate**: How quickly could ROI be demonstrated (impacts pitch positioning)

### Step 5: Generate Client Profile Report & Populated Fields
Output two things:

**A) Intelligence Brief (Markdown Report)**
```markdown
# Client Intelligence Brief: [Company Name]

## Executive Summary
[1-2 sentence overview of company, size, market position]

## Business Model
- **Revenue model**: [B2B/B2C/Services/Hybrid]
- **Operational complexity**: [Assessment]
- **Team size signal**: [Estimated headcount from signals]
- **Current systems**: [Visible platforms mentioned]

## Key Pain Points Aligned to 5 Cypress
- **[Service Name]**: [Specific trigger] → [Why this is likely costing them]
- **[Service Name]**: [Specific trigger] → [Why this is likely costing them]

## Recommended Engagement
- **Primary hook**: [Specific challenge to lead with]
- **First-call objective**: Get them to confirm [specific operational bottleneck]
- **Timeline for proof**: [e.g., "Can show ROI in 2-3 weeks on order processing"]
- **Secondary opportunities**: [2-3 follow-on services]

## Talking Points & Research
- [3-5 specific hooks from company website/news]
- [Industry context if relevant]
- [Recent signals: funding, product launches, hiring, partnerships]

## Next Steps
1. Research contact(s): [use LinkedIn/company site to find right person]
2. Personalize outreach using [specific talking point]
3. Schedule discovery call with focus on [primary pain point]
```

**B) Pre-Populated Client Fields (JSON)**
```json
{
  "name": "[Company Name]",
  "website": "[URL or null]",
  "industry": "[Extracted industry]",
  "status": "prospect",
  "engagement_type": "[Recommended: trial_program | custom_project | retainer]",
  "business": {
    "industry": "[Full industry descriptor]",
    "pain_points": ["[Identified pain point]", "..."],
    "current_systems": ["[Visible platforms]", "..."],
    "monthly_order_volume": null,
    "estimated_team_size": "[e.g., '5-10', '50-100']"
  },
  "contact": {
    "name": "[If provided]",
    "email": "[If found]",
    "company": "[Company Name]"
  },
  "tags": ["[Primary service area]", "[Secondary area]", "[Industry tag]"],
  "notes": "[3-5 sentence summary of engagement strategy and key hooks]"
}
```

## Examples

### Example 1: SaaS Company with Order Management Pain

**Input:**
```
company_name: "Clarity Analytics"
website: "https://clarity-analytics.com"
```

**Output (Brief excerpt):**
```markdown
# Client Intelligence Brief: Clarity Analytics

## Executive Summary
Clarity Analytics is a B2B SaaS analytics platform serving financial services, ~40 employees, founded 2020.

## Business Model
- Revenue model: SaaS (subscription + usage-based)
- Operational complexity: High (multi-system integrations for customer data)
- Team size signal: ~40-50 based on LinkedIn/website
- Current systems: AWS, Salesforce (inferred from case studies), Stripe

## Key Pain Points Aligned to 5 Cypress
- **QuickBooks + Invoicing**: "Automate recurring subscriptions and usage-based billing reconciliation" → Manual billing workflows likely causing month-end delays
- **Lead Gen + Content**: "Thought leadership positioning for B2B financial market" → Can accelerate inbound through content + SEO
- **Workflow Automation**: "Data integration across customer systems" → Hidden opportunity for internal automation

## Recommended Engagement
- **Primary hook**: "How are you handling usage-based billing reconciliation across Stripe and your accounting system? Most analytics platforms struggle with this."
- **Timeline for proof**: 2-3 weeks; can show clean billing workflow by end of month

## Talking Points
- Recent case study mentions financial services integrations
- Website emphasizes "reliability"—positions well for our "resilience" messaging
- No mention of automation infrastructure—gap we can fill
```

**Pre-populated fields:**
```json
{
  "name": "Clarity Analytics",
  "website": "https://clarity-analytics.com",
  "industry": "B2B SaaS / Analytics",
  "status": "prospect",
  "engagement_type": "trial_program",
  "tags": ["saas", "billing-automation", "data-integration", "financial-services"],
  "notes": "Analytics SaaS with usage-based billing pain. Lead with QuickBooks + invoicing automation. Secondary opportunity in internal workflow automation. Contact: VP Product via LinkedIn."
}
```

### Example 2: eCommerce with Fulfillment Gaps

**Input:**
```
company_name: "Premium Outdoor Gear Co"
website: "https://premiumoutdoorgear.com"
industry_hint: "ecommerce"
```

**Output (Brief excerpt):**
```markdown
## Key Pain Points Aligned to 5 Cypress
- **ShipStation Automation**: Multiple fulfillment mentions → likely juggling Shopify + manual shipping
- **Inventory Integration**: "Manage 500+ SKUs" on site → syncing inventory across channels is complex
- **Lead Gen**: B2C brand with weak email list capture signals → opportunity to build content-driven customer acquisition

## Recommended Engagement
- **Primary hook**: "You mention handling 500+ SKUs across channels—how are you syncing inventory between Shopify and your warehouse? Are you doing that manually?"
- **Timeline for proof**: 1 week; can show reduced order-to-ship time immediately
```

## Edge Cases & Mitigation

**Private companies or minimal online presence:**
- Use industry + location signals to infer business model
- Note in brief: "Limited public info available; prioritize discovery call discovery"
- Recommendation: Lead with broad industry pain points, refine in first call

**Competitors or similar companies:**
- Acknowledge positioning without negativity
- Reframe as: "More volume → more complex automation needs"
- Opportunity: White-label, partnership play

**Unidentifiable industry or business model:**
- Default to broad automation pain points (lead gen, workflow, billing)
- Defer specificity to sales call
- Note: "Research inconclusive; recommend extended discovery"

**Duplicate clients or existing prospects:**
- Check client.json slug existence before creating
- Return: "This client already exists in system [link to profile]"

## Output Quality Checklist

Before returning to user:
- [ ] Business model clearly identified
- [ ] Minimum 2 pain points mapped to 5 Cypress services
- [ ] Primary engagement hook is specific (not generic)
- [ ] Pre-populated JSON is valid and matches client.json schema
- [ ] Brief is scannable (max 200 lines, clear headers)
- [ ] Talking points are taken directly from company website/recent news (not generic)
- [ ] Next steps are explicit and assignable

## Integration with Admin Clients Page

**Workflow trigger:**
1. Admin clicks "New Client" modal on /admin/clients
2. Fills form: company_name, website (optional)
3. Submits form → calls `POST /admin/api/clients/` route
4. Route creates client.json stub
5. **Optional**: Admin can trigger this skill manually
   - "Run Intelligence Brief" button in client drawer
   - Pre-populates industry, pain_points, tags, engagement_type from output
   - Admin reviews and confirms fields before saving

**Integration points:**
- Feeds into: `customer-sales` skill for personalized initial outreach
- Pair with: `account-review` skill for periodic check-ins once client becomes active
- Complements: `manage_clients` directive for structured client tracking

## Reference: 5 Cypress Services Mapping

Use this to map company signals to services:

| Service | Primary Signal | Secondary Signal |
|---------|---|---|
| QBO Invoicing | Billing/payments/invoicing mentioned | Order volume > 10/day |
| ShipStation | Shipping/fulfillment/logistics | Multi-channel mentions (Shopify + Amazon) |
| Lead Gen | "Sales", "prospecting", "pipeline growth" | B2B company, new GTM |
| SEO/Content | "Marketing", "visibility", "thought leadership" | B2B, competitive market |
| Workflow | "Integration", "automation", "manual", "data entry" | Multi-system mentions |
