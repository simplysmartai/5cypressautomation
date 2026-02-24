# Directive: Page CRO Analyzer
# 5 Cypress Automation

---

## Purpose
Analyze a client's landing pages, service pages, or conversion-critical website pages and produce a prioritized conversion rate optimization (CRO) audit. Output identifies friction points, copywriting gaps, structural issues, and specific improvements — with a clear implementation priority order.

**Pricing:** $300–$800 per page audit (standalone) or included in SEO/marketing retainer.

---

## When to Use This Directive
- Client has a page that isn't converting (demo requests, contact forms, signups, purchases)
- Client is launching a new landing page and wants a pre-launch review
- Campaign is driving traffic to a page with poor results
- Quarterly review of core conversion pages

---

## Inputs Required

Collect before starting:
- [ ] URL(s) of page(s) to analyze
- [ ] Page goal (what action should a visitor take?)
- [ ] Current conversion rate if known
- [ ] Traffic source (organic / paid / email / referral)
- [ ] Target audience for this page
- [ ] Client context file loaded from `clients/[client-name]/`
- [ ] Any heatmap/session data (if client has it — Hotjar, Clarity, etc.)

---

## Process

### Step 1 — Page Capture
Use Perplexity MCP or browser access to:
- Open the page URL
- Read all copy, headlines, CTAs, and structural elements
- Note: above-the-fold section, value proposition clarity, social proof, CTA placement, form fields, page speed indicators

### Step 2 — CRO Audit (score each category 1–10)

**2a. Headline & Value Proposition**
- Is the main benefit immediately clear?
- Does it speak directly to the target audience's pain point?
- Is it specific or generic?

**2b. Copy & Messaging**
- Does copy flow from pain → solution → proof → CTA?
- Is it written for the audience or for the company?
- Are there unnecessary buzzwords or vague claims?
- Does every section earn its place?

**2c. Call-to-Action**
- Is the CTA visible without scrolling (above the fold)?
- Is there one clear primary CTA?
- Does the CTA language specify the action and value? ("Book a Free Demo" vs. "Submit")
- Are there secondary CTAs competing for attention?

**2d. Social Proof & Trust**
- Are testimonials or case studies present and specific?
- Are logos, certifications, or numbers shown?
- Is the source/context of proof credible?

**2e. Visual Hierarchy & Design**
- Does the eye flow naturally toward the CTA?
- Is important information being buried?
- Are there distracting elements?

**2f. Form & Friction**
- If there's a form: is it minimal? (Only ask what's essential)
- Is there reassurance near the form? (Privacy note, what happens next)
- How many steps or fields to convert?

**2g. Mobile Experience**
- Is the page usable on mobile?
- Is the CTA accessible on small screens?
- Does content reflow correctly?

### Step 3 — Prioritized Recommendations

Produce a priority-ranked list (P1 / P2 / P3):

| Priority | Issue | Why It Matters | Recommended Fix | Effort |
|----------|-------|----------------|-----------------|--------|
| P1 | | | | Low/Med/High |
| P2 | | | | |
| P3 | | | | |

P1 = High impact, low effort (do immediately)
P2 = High impact, higher effort (plan next sprint)
P3 = Nice-to-have or edge case improvements

### Step 4 — Rewrite Key Elements

Provide improved copy drafts for:
- Headline (3 variants)
- Primary CTA button text (3 variants)
- Any above-the-fold section that has critical gaps

Do not rewrite the entire page unless explicitly requested.

### Step 5 — Save Output
Save to: `marketing-team/output/[client-name]/cro-audit-[page-name]-[YYYY-MM].md`

---

## Integration Points
- Use **page_cro_analyzer.py** in `execution/` for automated technical checks (meta tags, load time, etc.)
- Pair with `directives/seo_optimization_service.md` for combined SEO + CRO reviews
- Results can feed into A/B test planning

---

## Quality Standards
- Every recommendation must be grounded in a specific observation from the page
- Prioritization must be honest — if only 2 things matter, say so
- Rewritten copy must match the client's tone and audience (load context file)
- Report must be usable without additional explanation from the analyst
