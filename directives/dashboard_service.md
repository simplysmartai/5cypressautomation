# Dashboard Service Directive

**Service:** Custom Data Visualization Dashboards
**Formats:** Power BI (.pbix), Tableau (.twbx), Web (HTML/JS)
**Owner:** Nick (discovery, assembly, client delivery) + AI (data prep, analysis, calculations, web generation)

---

## Overview

We build custom dashboards for SMB clients — tailored to their specific data, KPIs, and business questions.
The AI handles 80–90% of the work (data cleaning, modeling, calculations, visualization code, insight
narratives). Nick handles the final assembly in Power BI/Tableau when needed (~20–30 min) and all
client-facing interactions.

---

## Service Tiers

### One-Time Build (Setup Fee)
| Scope | Price |
|---|---|
| Simple (1–2 data sources, ≤8 KPIs, 1 page) | $1,500 |
| Standard (2–3 sources, 8–15 KPIs, 2–3 pages) | $2,000 |
| Complex (3+ sources, 15+ KPIs, 4+ pages, advanced logic) | $2,500 |

### Monthly Maintenance (After Delivery)
| Tier | Price | What's Included |
|---|---|---|
| **Monitor** | $100–$150/mo | Data refresh verification, break-fix, 1 minor tweak/month |
| **Maintain** | $200–$300/mo | Above + 2–3 metric/view changes, quarterly review call |
| **Evolve** | $400–$500/mo | Above + new pages, advanced analytics, monthly insight summary |

---

## Licensing

### Our Side (5 Cypress)
| Tool | Cost | When |
|---|---|---|
| Power BI Desktop | **Free** | Install now — full authoring, no license key |
| Tableau Creator | **~$75/mo** | Only when first Tableau client signs; cancel if no active clients |
| Chart.js / Plotly.js | **Free** | Web dashboards — no license |
| Python (pandas, etc.) | **Free** | Data processing — already installed |

**Strategy:** Start at $0. Add Tableau Creator only when required; roll cost into that client's setup fee.

### Client Side (Their Responsibility)
| Scenario | What Client Needs | Their Cost |
|---|---|---|
| Power BI — local .pbix file only | Power BI Desktop (free) | $0 |
| Power BI — shared/cloud | Power BI Pro per viewer | ~$10/user/mo |
| Power BI — large datasets or AI features | Power BI Premium Per User | ~$20/user/mo |
| Tableau — view only | Tableau Viewer | ~$15/user/mo |
| Tableau — editing | Tableau Explorer/Creator | $42–$75/user/mo |
| Web dashboard | A browser | $0 |

**Always state clearly in the proposal:** Client licensing costs are separate from 5 Cypress service fees.
Recommend web dashboards when clients have no BI tools and limited budget.

---

## Format Decision Tree

Run this during discovery to determine the right output format:

1. Does the client already have Power BI (Microsoft 365) or Tableau?
   - Yes → Use what they have
   - No → Go to step 2

2. How many people need to view the dashboard?
   - 1–2 people → Power BI Desktop (free, local file) OR web dashboard
   - 3+ people, budget available → Power BI Pro ($10/user/mo) + .pbix
   - 3+ people, no budget → Web dashboard (shareable link, zero cost)
   - Client specifically wants Tableau → Tableau (note: adds $75/mo to our costs, factor into pricing)

3. Does the dashboard need to auto-refresh from a live data source?
   - Yes → Power BI Pro/Premium OR web dashboard with API/script connection
   - No (manual refresh OK) → Power BI Desktop (free) works fine

---

## Phase 1: Discovery

**Tool:** `documents/dashboard-discovery.md`
**Who:** Nick runs the 30–45 min call; fills out the template during or immediately after
**Output:** Completed discovery doc saved to `clients/{client-id}/documents/dashboard-discovery-{date}.md`

Key questions to answer before leaving the call:
- What business decisions will this dashboard inform?
- Who uses it, how often, on what device?
- What data sources exist and in what format?
- What does "good" vs. "bad" look like for their key numbers?
- What BI tools do they have (or is web the path)?
- Any compliance/sensitivity requirements (HIPAA, financial, PII)?
- How often does the underlying data change?

**Scoping output:** Discovery doc feeds directly into the build phase. No ambiguity allowed — if
you don't know the answer to a question, get it on the call or via follow-up before starting the build.

---

## Phase 2: Data Intake

**Security first.** Before any data changes hands:
- NDA signed (use `templates/contracts/nda.md`)
- For financial or medical data: DPA signed (use `templates/contracts/data-processing-agreement.md`)
- All contract signing happens through the Copilot client portal

**Data transfer methods (in order of preference):**
1. Copilot client portal secure file upload (preferred)
2. Password-protected ZIP file via encrypted email
3. Shared OneDrive/SharePoint link with expiration (Microsoft 365 clients)
4. QBO API direct connection (for bookkeeping/CFO clients — no file transfer needed)

**Never:** Unprotected email attachments, public Google Drive links, Slack file shares, Dropbox public links

**After receiving data:**
- Download to local machine only
- Save raw file to `clients/{client-id}/data/raw/`
- Run `execution/dashboard_data_processor.py` immediately
- Delete raw file after processing if it contains sensitive data (retain cleaned output only)

---

## Phase 3: Data Processing

**Script:** `execution/dashboard_data_processor.py`
**Input:** Raw CSV/Excel file(s) from `clients/{client-id}/data/raw/`
**Output:** Cleaned dataset + data quality report in `clients/{client-id}/data/processed/`

The script handles:
- Auto-detect column types (date, currency, category, measure, ID)
- Data quality report: nulls, duplicates, outliers, type mismatches, blank rows
- Cleaning: standardize date formats, normalize currency values, handle nulls
- Relationship mapping (if multiple files/tables)
- Schema documentation (column names, types, sample values, suggested KPI role)
- Pydantic validation on all fields

**Review the data quality report before proceeding.** Common issues to flag to the client:
- Columns with >10% nulls (ask if intentional or a data export issue)
- Duplicate rows (ask if each row should be unique)
- Date range gaps (ask if expected)
- Inconsistent category naming (e.g., "New York" vs. "NY" vs. "new york")

---

## Phase 4: Dashboard Build

**Script:** `execution/generate_dashboard.py`
**Input:** Processed data + completed discovery doc + format decision (PBI / Tableau / Web)
**Output:** Format-specific build package in `clients/{client-id}/deliverables/dashboard-{version}/`

### Web Dashboard Path (Fully Automated)
- Complete self-contained HTML file with Chart.js/Plotly.js
- Interactive filters, mobile-responsive, brandable (client colors/logo)
- No client software required — works in any browser
- Nick reviews output, sends to client directly
- **Turnaround from processed data: same session**

### Power BI Path (Paint-by-Numbers Kit)
The AI produces a structured prep package:
- `data-model.csv` — cleaned, modeled dataset ready for PBI import
- `relationships.md` — table relationships and join keys
- `dax-measures.txt` — all measures and calculated columns, ready to paste
- `power-query.txt` — M code for any transformations needed in Power Query
- `layout-wireframe.md` — exact page layout, chart types, filter placement
- `design-spec.md` — colors, fonts, branding, conditional formatting rules
- `data-validation.md` — expected row counts, totals to verify after import

Nick opens Power BI Desktop, follows the prep package, assembles in ~20–30 min.
**Target: less than 30 minutes of Nick's time in PBI Desktop.**

### Tableau Path (Paint-by-Numbers Kit)
The AI produces:
- `data-source.csv` — cleaned dataset
- `calculated-fields.md` — all Tableau calculated field definitions (LOD expressions, table calcs)
- `layout-wireframe.md` — sheet and dashboard layout
- `design-spec.md` — colors, fonts, formatting
- `filter-spec.md` — filter types, dependencies, actions

Nick opens Tableau Desktop, follows the spec.
**Target: less than 30 minutes of Nick's time in Tableau Desktop.**

---

## Phase 5: Review & Revision

Before presenting to client:
- Nick reviews the dashboard for accuracy (numbers match expectations)
- Cross-check against data quality report (totals, row counts)
- Verify all filters and interactions work
- Test on mobile (for web dashboards)
- Test print/PDF export (if client needs it)

**Standard: 2 revision rounds included in setup fee.**
Additional revisions: $150/round (add to project scope doc).

---

## Phase 6: Client Presentation

**Who:** Nick (30–60 min screenshare or in-person)
**Agenda:**
1. Walk through each page/view (5–10 min)
2. Demonstrate filters, drill-downs, interactions
3. Explain what each KPI means and what drives it
4. Collect feedback (use this session for revision round 1 if needed)
5. Confirm approval before deployment

**Tip:** Lead with business insights, not chart mechanics. "Your Q4 close rate dropped 8 points
vs. Q3 — this chart shows it's concentrated in the Enterprise segment" is a better opening
than "Here's your funnel chart."

---

## Phase 7: Deployment & Setup

**Goal:** Client's dashboard is running live, data refreshes without manual intervention where possible.

### Web Dashboard Deployment
- Host on client's website (Nick provides HTML file + setup instructions)
- OR host on 5 Cypress infrastructure (password-protected page under their subdomain)
- For live data: connect to Google Sheets, Airtable, or API endpoint that client updates

### Power BI Deployment
- If local only: Hand off .pbix file + instructions for data refresh
- If cloud: Publish to client's Power BI Service workspace (they need Pro licenses)
- Set up scheduled refresh if data source is a file (SharePoint/OneDrive) or database
- Provide `deployment-guide.md` (generated by AI) with screenshots

### Tableau Deployment
- Hand off .twbx packaged workbook to client
- If Tableau Server/Cloud: Publish to their environment
- Provide `deployment-guide.md`

**Data refresh setup checklist (save to `clients/{client-id}/documents/`):**
- [ ] Data source location documented
- [ ] Refresh frequency confirmed with client
- [ ] Refresh tested at least once successfully
- [ ] Client knows how to trigger a manual refresh if needed
- [ ] Contact for data source issues identified (usually their IT or data owner)

---

## Phase 8: Monthly Maintenance

**Time target: <1 hour per client per month**

**Monthly checklist (use `documents/dashboard-maintenance-checklist.md`):**
1. Verify data refresh ran successfully
2. Check for data quality drift (new nulls, schema changes, new categories)
3. Review any client requests queued in Copilot portal
4. Prep changes (new metrics, chart adjustments, new pages) with AI
5. Apply changes in PBI/Tableau or regenerate web dashboard
6. Brief status update to client (2–3 sentences via Copilot portal message)

**Scope boundaries by tier:**
- Monitor ($100–150): Refresh verification + break-fix only. New work billed at $150/hr.
- Maintain ($200–300): Up to 2 hrs of changes included. Overage at $150/hr.
- Evolve ($400–500): Up to 4 hrs of changes included. Overage at $150/hr.

---

## Edge Cases

### Client Has Dirty / Inconsistent Data
- Run `dashboard_data_processor.py` and share the data quality report with client
- Do NOT proceed with the build until data issues are resolved or explicitly accepted
- Offer data cleaning as a paid add-on ($300–500 flat) if the cleanup is extensive

### Client Has No Data Yet
- Offer to build the dashboard structure with synthetic data as a prototype
- When real data is ready, plug in and go live
- Prototype builds: $500 flat (credited toward full build when they're ready)

### HIPAA / Medical Clients
- Require HIPAA-compatible file transfer (Copilot + BAA, or ShareFile with BAA)
- DPA must be signed before any data intake
- Never store PHI (Protected Health Information) in plaintext on local disk
- Store processed data as anonymized/aggregated only
- Flag for legal review if client's dashboard will display identifiable patient data

### Client Wants Live Data Without IT Help
- Google Sheets as the data layer: Client updates a Sheet, dashboard pulls automatically
- Web dashboards can connect to Google Sheets API directly (no IT required)
- Power BI can connect to Google Sheets via connector (requires Pro license)
- This is often the best SMB solution — document the pattern in the deployment guide

### Client Loses Access to the Dashboard
- Web: Re-send the link or regenerate the HTML
- Power BI: Re-send the .pbix or re-publish from saved file
- Keep a copy of every delivered artifact in `clients/{client-id}/deliverables/`

### Schema Change Breaks the Dashboard
- Client adds or renames a column in their data source
- Web dashboard: Regenerate with updated schema
- PBI/Tableau: Update data source connection and column references
- Add to DPA/scope: "Client must notify 5 Cypress 5 business days before making schema changes"

---

## File Structure per Client

```
clients/{client-id}/
├── client.json                          # Contact info, service tier, API access
├── documents/
│   ├── dashboard-discovery-{date}.md   # Completed discovery questionnaire
│   ├── dashboard-maintenance-checklist.md
│   └── deployment-guide.md            # Generated per dashboard
├── data/
│   ├── raw/                           # Client's original files (delete sensitive after processing)
│   └── processed/                     # Cleaned datasets (keep; source of truth)
└── deliverables/
    └── dashboard-v{n}/                # Versioned dashboard artifacts
        ├── dashboard.html             # Web dashboard (if applicable)
        ├── data-model.csv            # PBI/Tableau data file
        ├── dax-measures.txt          # Power BI measures (if applicable)
        ├── calculated-fields.md      # Tableau fields (if applicable)
        ├── power-query.txt           # PBI Power Query M code (if applicable)
        ├── layout-wireframe.md       # Design spec
        └── design-spec.md           # Colors, fonts, formatting
```

---

## Execution Scripts

| Script | Purpose |
|---|---|
| `execution/dashboard_data_processor.py` | Data cleaning, quality reporting, schema modeling |
| `execution/generate_dashboard.py` | Dashboard generation (web) + PBI/Tableau prep packages |

---

## Self-Annealing

When something breaks:
1. Identify: data issue, calculation error, or rendering bug?
2. Fix the script or spec
3. Re-run and verify output
4. Update this directive with what you learned
5. Add the edge case to the appropriate section above

Common failures to watch for:
- Date format mismatches between client data and script expectations
- Currency columns stored as text (need cleaning before aggregation)
- Power BI data model relationships creating duplicate rows (check cardinality)
- Chart.js canvas rendering issues in certain browsers (test in Chrome + Edge)
