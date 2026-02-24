# Reference: Reporting Templates & Dashboard Patterns
# 5 Cypress Automation — Knowledge Base

These patterns define how 5 Cypress builds reports and dashboards. Use these as structure and design reference when producing deliverables with the Data Analysis & Reporting skill.

---

## Report Narrative Structure

Every 5 Cypress report follows this story arc:

1. **The Headline** — What's the single most important thing to know this period?
2. **The Scorecard** — How did we do against goals?
3. **The Story** — What happened and why?
4. **The Wins** — What's working?
5. **The Concerns** — What needs attention?
6. **The Plan** — What do we do now?

This structure ensures clients don't have to dig for meaning — the meaning is served to them.

---

## KPI Scorecard Format

Always present KPIs in a table with status indicators:

| Metric | Goal | Actual | vs. Prior Period | Status |
|--------|------|--------|-----------------|--------|
| Email Open Rate | 28% | 31% | +4pts | ✅ |
| Email CTR | 3% | 2.1% | -0.4pts | ⚠️ |
| New Leads | 15 | 9 | -6 | 🔴 |
| Pipeline Value | $50K | $72K | +$22K | ✅ |

**Status Key:**
- ✅ On Track — at or above goal
- ⚠️ Watch — below goal but trending right or minor gap
- 🔴 Needs Attention — significantly below goal, needs action

---

## Chart Type Selection Guide

Use the right chart for the data:

| Data Type | Best Chart | When to Use |
|-----------|------------|-------------|
| Performance over time | Line chart | Monthly trends, weekly metrics |
| Comparing categories | Bar chart | Channel comparison, campaign comparison |
| Part of a whole | Pie / Donut | Traffic sources, lead sources |
| Two variables | Scatter | Correlation analysis |
| Progress to goal | Gauge / Progress bar | KPI dashboards |
| Distribution | Histogram | Audience demographics |

**Rules:**
- Never use pie charts with more than 5 slices
- Always label data points directly on charts (not just in legends)
- Always include the time period in chart titles

---

## Dashboard Color System

**Default 5 Cypress Dashboard Colors:**
- Primary: `#1a3c5e` (dark navy)
- Accent: `#4a9b8e` (teal)
- Success: `#27ae60` (green)
- Warning: `#f39c12` (amber)
- Alert: `#e74c3c` (red)
- Background: `#f8f9fa` (light gray)
- Card background: `#ffffff` (white)

If the client has defined brand colors in their context file, use those instead for chart colors while keeping the structural colors above for status indicators.

---

## HTML Dashboard Template Structure

```html
<!DOCTYPE html>
<html>
<head>
  <!-- Chart.js CDN -->
  <!-- Custom styles: clean, professional, mobile-responsive -->
</head>
<body>
  <!-- Header: Client name, report period, prepared by 5 Cypress -->
  
  <!-- Section 1: KPI Scorecard -->
  <!-- Grid of metric cards with value, goal, status indicator, delta -->
  
  <!-- Section 2: Performance Charts -->
  <!-- 2-column grid: chart + insight callout beside each -->
  
  <!-- Section 3: Channel Breakdown -->
  <!-- Channel-by-channel performance with mini charts -->
  
  <!-- Section 4: Recommendations -->
  <!-- Numbered priority list with rationale -->
  
  <!-- Footer: 5 Cypress branding, date generated -->
</body>
</html>
```

---

## Insight Sentence Formula

Every chart needs one sentence. Use this formula:

> "[Metric] [went up/down/stayed flat] [by X%] [compared to prior period], [driven by / despite / suggesting] [root cause or interpretation]."

**Examples:**
> "Email open rates rose to 31%, up 4 points from last month, likely driven by the more specific subject lines tested in the second campaign."

> "Lead volume declined to 9 from 15 the prior period, suggesting the top-of-funnel content shift in October has not yet converted to lead activity."

Never show a number without a sentence like this nearby.

---

## Recommendations Format

Present recommendations in priority order:

```
## Recommendations & Next Steps

**Priority 1: [Action Title]**
What: [Specific action to take]
Why: [Data rationale — reference a specific number]
Expected Impact: [What improvement to expect]
Owner: [5 Cypress / Client / Both]

**Priority 2: [Action Title]**
...
```

---

## B2B Marketing Benchmarks Reference

Use these when client data lacks context:

**Email (B2B)**
- Open rate: 20-30% average; 35%+ excellent
- CTR: 2-5% average; 5%+ excellent
- Unsubscribe: <0.5% healthy

**LinkedIn (B2B)**
- Organic post engagement rate: 1-5%
- Follower growth: 2-5%/month healthy
- Click-through: 0.5-1% on boosted content

**Lead Generation (B2B)**
- Landing page conversion: 5-15% for gated content
- Email to demo conversion: 1-5% typical
- Lead to opportunity: 10-30% depending on qualification

**Sales Cycle (B2B Tech/Medical)**
- Average deal cycle: 2-6 months
- Typical touches before decision: 8-12
