# Dashboard Discovery Questionnaire

**Client:** ___________________________
**Date:** ___________________________
**Conducted by:** Nick
**Service tier being scoped:** [ ] Simple ($1,500)  [ ] Standard ($2,000)  [ ] Complex ($2,500)

---

> **Instructions:** Fill this out during or immediately after the discovery call.
> Save completed doc to `clients/{client-id}/documents/dashboard-discovery-{YYYY-MM-DD}.md`.
> Do NOT begin the build until every section is complete. If you don't have an answer, get it.

---

## Section 1: Business Context

**1.1 What business decisions will this dashboard help you make?**

_Example: "Decide where to focus our sales team each week" or "Know if we're on track to hit monthly revenue targets"_

```
[Answer here]
```

**1.2 Who is the primary audience for this dashboard?**
- [ ] Executive / Owner / C-Suite (high-level, summary-focused)
- [ ] Operations Manager (detailed, process-focused)
- [ ] Sales Team (individual performance + pipeline)
- [ ] Finance / CFO (P&L, cash flow, margins)
- [ ] Marketing Team (campaign metrics, lead gen)
- [ ] Other: ___________________________

**1.3 How often will they look at it?**
- [ ] Daily
- [ ] Weekly
- [ ] Monthly
- [ ] Ad hoc / on demand

**1.4 What device(s) will they use?**
- [ ] Desktop/laptop (browser)
- [ ] Tablet
- [ ] Mobile phone
- [ ] TV/monitor on the wall
- [ ] Printed/exported PDF

**1.5 What is the single most important number this dashboard needs to show?**

```
[Answer here]
```

---

## Section 2: KPIs & Metrics

**2.1 List every metric you want to track (brain dump — we'll prioritize together):**

```
1.
2.
3.
4.
5.
6.
7.
8.
```

**2.2 For each key metric, what does "good" look like? What does "bad" look like?**

| Metric | Good (Target / Threshold) | Bad (Alert Level) |
|---|---|---|
| | | |
| | | |
| | | |
| | | |

**2.3 Are there any comparisons that matter?**
- [ ] This month vs. last month
- [ ] This year vs. last year (YoY)
- [ ] Actual vs. budget/target
- [ ] By team member / by rep / by location
- [ ] Other: ___________________________

**2.4 Do you need trend lines (how a metric changes over time) or just current snapshots?**
- [ ] Trends over time (line charts, time series)
- [ ] Current state snapshots (KPI cards, gauges)
- [ ] Both

---

## Section 3: Data Sources

**3.1 Where does the data live right now? (Check all that apply)**
- [ ] Excel spreadsheet(s)
- [ ] CSV exports from a system
- [ ] QuickBooks Online
- [ ] HubSpot / Salesforce / CRM
- [ ] Google Sheets
- [ ] Shopify / e-commerce platform
- [ ] SQL database
- [ ] API / web service
- [ ] Paper records / manual entry
- [ ] Other: ___________________________

**3.2 For each data source, answer:**

| Data Source | File/System Name | How Often Updated | Who Updates It | Access Method |
|---|---|---|---|---|
| | | | | |
| | | | | |
| | | | | |

**3.3 How will data get to us? (Refer to data-handling-policy.md for options)**
- [ ] Copilot portal secure upload (preferred)
- [ ] Password-protected ZIP via encrypted email
- [ ] OneDrive/SharePoint shared link (expiring)
- [ ] QBO API direct connection (for QBO clients)
- [ ] Other: ___________________________

**3.4 Are there multiple data sources that need to be joined/combined?**
- [ ] No — one source
- [ ] Yes — describe the relationship: ___________________________

**3.5 How often does the underlying data change? How often should the dashboard refresh?**
- [ ] Real-time (data changes constantly)
- [ ] Daily (data updated once a day)
- [ ] Weekly
- [ ] Monthly
- [ ] Manual (client will refresh when they want)

---

## Section 4: Tools & Technical Setup

**4.1 What BI tools does the client already have?**
- [ ] Power BI Desktop (free, local only)
- [ ] Power BI Pro ($10/user/mo — cloud sharing)
- [ ] Power BI Premium
- [ ] Tableau Desktop
- [ ] Tableau Server / Cloud
- [ ] None

**4.2 Based on Section 4.1, format decision:**
_(Apply the format decision tree from the directive)_

- [ ] **Web dashboard** (HTML/JS — no license, shareable link)
- [ ] **Power BI** (.pbix — client assembles in PBI Desktop)
- [ ] **Tableau** (.twbx — client has Tableau Desktop)
- [ ] Power BI + Web (deliver both)

**4.3 Does the client need us to host the dashboard?**
- [ ] No — they'll host it / use it in their own tools
- [ ] Yes — host on 5 Cypress infrastructure
- [ ] Yes — host on their website (provide embed code)

**4.4 Does the client have IT support or are they self-service?**
- [ ] Has dedicated IT (can set up database connections, manage security)
- [ ] Self-service (no IT — keep it simple, Google Sheets data layer recommended)

---

## Section 5: Compliance & Security

**5.1 What type of data will be in the dashboard?**
- [ ] Business metrics / operational data (standard NDA sufficient)
- [ ] Financial data / P&L / revenue (DPA required)
- [ ] Patient / health data (HIPAA — DPA + BAA required)
- [ ] Personal identifiable information (PII) about employees or customers (DPA required)
- [ ] Other sensitive data: ___________________________

**5.2 Contracts required before data intake:**
- [ ] NDA — signed ✓ / pending / not yet initiated
- [ ] DPA — signed ✓ / pending / not required
- [ ] HIPAA BAA — signed ✓ / pending / not required

**5.3 Any specific security or compliance requirements from the client's industry?**

```
[Answer here]
```

---

## Section 6: Scope Confirmation

**6.1 Number of distinct data sources:** _____

**6.2 Estimated number of KPIs/metrics:** _____

**6.3 Estimated number of dashboard pages/tabs:** _____

**6.4 Complexity level (circle):**  Simple / Standard / Complex

**6.5 Estimated setup fee:**  $___________

**6.6 Monthly maintenance tier:** Monitor / Maintain / Evolve  →  $___________/mo

**6.7 Estimated turnaround time:**
- Simple: 3–5 business days from data receipt
- Standard: 5–7 business days from data receipt
- Complex: 7–10 business days from data receipt

---

## Section 7: Open Questions / Follow-Ups

_List anything that was unclear or needs a follow-up before starting the build:_

```
1.
2.
3.
```

**Follow-up deadline (must be resolved before build starts):** ___________________________

---

## Section 8: Nick's Internal Notes

_Observations, instincts, red flags, or opportunities not captured above:_

```
[Notes here]
```

**Client readiness assessment:**
- [ ] Ready to proceed — all information captured, contracts signed, data in hand
- [ ] Waiting on: ___________________________
- [ ] Concerns: ___________________________
