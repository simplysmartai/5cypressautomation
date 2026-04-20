# Architecture Audit (Discovery) Directive

> Structured process for the 5 Cypress Labs "Root Audit" to identify high-leverage automation opportunities.

## Mission

Transform discovery conversations into a technical "Root Audit" dossier. We don't just "fix problems"—we identify the structural weaknesses that prevent limitless scale.

## The Root Audit Framework

### Phase 1: Structural Context

**The Business Canopy**
- Company name, industry, and strategic goals
- Headcount and revenue trajectory (understanding scale pressure)
- Decision-maker profile (who owns the architecture?)
- Integration landscape (current tech stack)

**Root System (Current State)**
- What manual infrastructure is currently being "brute-forced"?
- Where is the data "leaking" or siloed?
- Weekly manual labor hours (identifying the drain)
- Impact of current inefficiencies on growth velocity

### Phase 2: Identifying the Roots of Inefficiency

For each bottleneck identified, document:

```
Root Point: [Structural Bottleneck]
├── Lifecycle: How pervasive is this process?
├── Labor Drain: Hours per month of manual compute
├── Fragility: Likelihood of system failure/error
├── Scaling Penalty: How much does this cost as they grow?
└── System Debt: Current manual workarounds
```

### Phase 3: Technical Integrity Assessment

**Infrastructure Audit**
- Core CRM Data Architecture
- Financial System Integration State
- Communication Pipeline Throughput
- Shadow IT / Unsanctioned manual tools

**Interconnectivity Needs**
- Required logic bridges (flows)
- API maturity levels
- Resilience requirements (Compliance, Redundancy, Security)

### Phase 4: Scope & Growth Readiness

**Investment Capacity**
- Past infrastructure investments
- Strategic priority of this build
- Cost of Inaction (COI) - The penalty of remaining un-automated

**Timeline for Endurance**
- Critical scaling milestones (Upcoming peaks/launches)
- Desired MVP launch date
- Long-term roadmap horizon

### Phase 5: Success Criteria

Define measurable outcomes:
- Time saved per week
- Error reduction percentage
- Revenue impact
- Customer satisfaction improvement
- Stress/workload reduction

## Output Format

After discovery, create a summary in the client folder:

```markdown
# Discovery Summary: [Client Name]

**Date:** [Date]
**Contact:** [Name, Title, Email]
**Source:** [How they found us]

## Business Overview
[2-3 sentences about the company]

## Pain Points
1. **[Pain Point 1]**
   - Current process: [description]
   - Time cost: [X hours/week]
   - Impact: [business impact]

2. **[Pain Point 2]**
   ...

## Current Tech Stack
- [Tool 1]: [what they use it for]
- [Tool 2]: [what they use it for]

## Proposed Solution
[High-level approach - 2-3 sentences]

## Recommended Package
- **Package:** [Starter/Growth/Scale]
- **Estimated Price:** $[amount]
- **Timeline:** [X weeks]
- **Key Deliverables:**
  - [Deliverable 1]
  - [Deliverable 2]

## Next Steps
1. [ ] Send proposal by [date]
2. [ ] Schedule follow-up call for [date]
3. [ ] [Any other actions]

## Notes
[Any other relevant information]
```

## Quick Discovery Questions

When user describes a prospect briefly, ask these if not provided:

1. "What's their biggest operational headache right now?"
2. "What tools are they currently using?"
3. "Any sense of budget or timeline?"
4. "What would success look like for them?"

## Execution

After discovery is complete:
1. Save summary to `clients/[client-slug]/discovery.md`
2. Log activity: `python execution/log_activity.py [client-slug] "Discovery call completed"`
3. Proceed to `directives/create_proposal.md`

## Related Directives
- `create_proposal.md` - Generate proposal from discovery
- `onboard_client.md` - After deal closes
- `manage_clients.md` - Client lifecycle
