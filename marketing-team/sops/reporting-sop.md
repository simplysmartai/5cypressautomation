# SOP: Data Analysis & Reporting
# 5 Cypress Automation — Standard Operating Procedure

---

## Purpose
This SOP defines the process for analyzing marketing performance data and producing client-ready reports and dashboards. Reports from 5 Cypress don't just show numbers — they tell a story, highlight what matters, and give clients clear direction on what to do next.

---

## When to Use This SOP
- Monthly marketing performance report
- Campaign wrap-up report (post-campaign analysis)
- Quarterly business review (QBR) deck support
- Ad hoc performance deep-dive

---

## Inputs Required Before Starting
- [ ] Client context file loaded
- [ ] Data provided by client or pulled from connected tools (CSV, spreadsheet, or raw numbers pasted in)
- [ ] Reporting period defined (e.g., "October 2025" or "Q3 2025")
- [ ] KPIs to report on confirmed (from strategy brief or client request)
- [ ] Previous period data for comparison (if available)

---

## Output Format
Deliver either:
- A Markdown report: `marketing-teammarketing-team/output/[client-name]/report-[period].md`
- An interactive HTML dashboard: `marketing-teammarketing-team/output/[client-name]/dashboard-[period].html`
- Or both, depending on client preference

---

## B2B Reporting Principles
1. **Lead with the headline.** The most important finding goes first, not buried at the end.
2. **Context beats raw numbers.** A 30% open rate means nothing without a benchmark.
3. **Show trends, not just snapshots.** Month-over-month or period-over-period comparison is essential.
4. **Every chart needs a sentence.** Don't make the client interpret — tell them what the data means.
5. **End with next steps.** A report without recommendations is just a spreadsheet.

---

## Process: Step by Step

### Phase 1 — Data Intake & Cleaning (5-10 min)
1. Review all data provided
2. Identify the reporting period and KPIs to cover
3. Note any data gaps or anomalies — flag these in the report
4. Organize data by channel/metric for analysis

### Phase 2 — Performance Analysis

Analyze each relevant channel/metric:

**Email Marketing Metrics**
- Open Rate (benchmark: 20-30% for B2B)
- Click-Through Rate (benchmark: 2-5% for B2B)
- Reply Rate (if tracked)
- Unsubscribe Rate (flag if >0.5%)
- Conversion Rate (clicks to desired action)
- List growth/decay

**Lead Generation Metrics**
- Total leads generated
- Lead source breakdown
- Lead quality indicators (if available)
- Cost per lead (if ad spend data provided)

**Website / Content Metrics** (if provided)
- Sessions, unique visitors
- Top pages / content
- Conversion events

**Campaign-Specific Metrics**
- Impressions, reach, clicks (if ad data)
- Campaign ROI (if revenue data available)

### Phase 3 — Insights Generation
For each major metric, answer:
- Is this good, bad, or neutral — and why?
- What's the trend vs. prior period?
- What's driving this result?
- What should the client do about it?

### Phase 4 — Build the Report / Dashboard

**For Markdown Report:**
Follow the output structure below.

**For HTML Dashboard:**
Build an interactive single-page HTML dashboard with:
- Summary scorecard (KPIs with status indicators: ✅ on track, ⚠️ watch, 🔴 needs attention)
- Charts using Chart.js or similar (bar, line, pie as appropriate)
- Insight callouts next to each major visualization
- Brand colors from client context file (or 5 Cypress defaults if not defined)
- Fully self-contained (no external dependencies beyond CDN links)

### Phase 5 — Recommendations
Produce a prioritized list of 3-5 recommended actions based on the data:
- **Priority 1:** [Most impactful action]
- **Priority 2:** [Second most impactful]
- etc.

Each recommendation includes: what to do, why (data rationale), and expected impact.

---

## Output Document Structure (Markdown Report)

```
# Marketing Performance Report — [Client Name]
# Period: [Reporting Period] | Prepared by 5 Cypress Automation | [Date]

## Executive Summary
[3-5 sentences: overall performance, top win, top concern, headline recommendation]

## KPI Scorecard
| Metric | Target | Actual | vs. Prior Period | Status |
|--------|--------|--------|-----------------|--------|

## Channel Performance

### Email Marketing
[Analysis + key insight]

### [Other Channel]
[Analysis + key insight]

## Key Wins This Period
[2-3 specific things that worked and why]

## Areas of Concern
[2-3 things underperforming with honest assessment]

## Recommendations & Next Steps
[Prioritized action list]

## Data Notes
[Any gaps, anomalies, or caveats the client should know]
```

---

## Quality Checklist
- [ ] Executive summary leads with the most important finding
- [ ] Every metric compared to a benchmark or prior period (not shown in isolation)
- [ ] Every chart/visualization has an accompanying insight sentence
- [ ] Recommendations are specific and prioritized
- [ ] Report is client-ready (no internal notes, clean formatting)
- [ ] Saved to correct output folder
