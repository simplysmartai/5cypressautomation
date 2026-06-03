/**
 * services.ts — single source of truth for all service data
 * Imported by /services, /services/[slug], homepage, nav, footer
 */

export interface Service {
  slug: string;
  tag: string;
  title: string;
  shortTitle: string;
  tagline: string;
  description: string;
  detail: string;
  painPoints: string[];
  outcomes: string[];
  stack: string[];
  setupPrice: string;
  monthlyPrice?: string;
  timeline: string;
}

export const services: Service[] = [
  {
    slug: 'practice-kpi-dashboard',
    tag: 'Dashboard',
    title: 'Practice KPI Dashboard',
    shortTitle: 'KPI Dashboard',
    tagline: 'Every critical metric — live, in one place.',
    description:
      'Real-time realization rate, WIP, AR aging, and billing metrics — pulled from QBO and your practice management system and surfaced to every partner in one live panel.',
    detail:
      'Partners at most firms are flying blind until month-end. By then, the decisions that could have been made in week 2 are three weeks late. We build a live dashboard that pulls directly from QuickBooks Online and your practice management system (Karbon, TaxDome, Clio, or CCH) — no manual exports, no spreadsheet juggling. Every partner sees realization rate, WIP balance, AR aging buckets, and billing trend in real time.',
    painPoints: [
      'Realization rate unknown until the billing run is closed',
      'WIP is tracked in a spreadsheet updated manually each week',
      'AR aging reports require a staff member to run and email',
      'Partners have no shared view — everyone is working from different data',
    ],
    outcomes: [
      'Live realization rate, WIP, AR aging updated every sync cycle',
      'Shared partner view — one URL, always current',
      'Automated alerts when WIP spikes or AR aging crosses a threshold',
      'Historical trend lines — see month-over-month without pulling reports',
    ],
    stack: ['QuickBooks Online', 'Karbon / TaxDome / Clio', 'Power BI or custom web dashboard', 'Python / FastAPI sync layer'],
    setupPrice: '$1,500–$2,500',
    monthlyPrice: '$200–$400/mo',
    timeline: '14 business days',
  },
  {
    slug: 'monthly-client-snapshot',
    tag: 'Reporting',
    title: 'Monthly Client Snapshot',
    shortTitle: 'Client Snapshots',
    tagline: 'Reports delivered before clients ask for them.',
    description:
      'One trigger after QBO close: auto-generated PDF report and branded web dashboard per client, delivered before the 5th — no manual data pulls, no formatting.',
    detail:
      "The most common complaint we hear from accounting clients: 'I'm still building the same report I built last month.' We build a system that listens for QBO period close, pulls the relevant data, generates a branded PDF and a live web dashboard, and emails it to the client — automatically. You review, not rebuild.",
    painPoints: [
      'Same report built manually for every client, every month',
      'Hours spent reformatting QBO exports into branded templates',
      `Clients emailing "do you have our March numbers?" before you've sent them`,
      'No audit trail for when reports were delivered',
    ],
    outcomes: [
      'Reports generated and delivered automatically after each QBO close',
      'Branded PDF + live web dashboard per client',
      'Delivery logged — you always know what was sent and when',
      'Partner review step before send (optional) — approve in one click',
    ],
    stack: ['QuickBooks Online API', 'OpenAI (narrative summaries)', 'Python / FastAPI', 'SendGrid / email delivery'],
    setupPrice: '$1,200–$1,800',
    monthlyPrice: '$150–$300/mo',
    timeline: '10–14 business days',
  },
  {
    slug: 'document-intake-ai-sort',
    tag: 'AI · Intake',
    title: 'Document Intake & AI Sort',
    shortTitle: 'Doc Intake',
    tagline: 'Clients upload once. Files land in the right place.',
    description:
      'Clients upload to a shared portal. OpenAI Vision classifies each file and routes it to the right job in Karbon, TaxDome, or SharePoint — in seconds.',
    detail:
      'Tax season document chaos is a solved problem. Instead of clients emailing files to whoever is available, we set up a client-facing upload portal. Every file is scanned by OpenAI Vision — it reads the document, identifies the type (W-2, 1099, bank statement, K-1, etc.), and routes it to the correct job folder in your practice management system. Staff spend zero time sorting.',
    painPoints: [
      "Clients emailing documents to staff's personal inboxes",
      'Staff manually sorting and renaming files into job folders',
      'Wrong documents filed to wrong clients during tax season',
      'No visibility into which clients have submitted all required documents',
    ],
    outcomes: [
      'Client-facing upload portal (branded, simple)',
      'AI classification: document type identified in <5 seconds',
      'Auto-routing to correct job in Karbon / TaxDome / SharePoint',
      'Missing document tracker — know who still needs to submit',
    ],
    stack: ['OpenAI Vision API', 'Karbon / TaxDome / SharePoint', 'Cloudflare R2 (file storage)', 'Python / FastAPI'],
    setupPrice: '$1,800–$2,800',
    monthlyPrice: '$250–$500/mo',
    timeline: '14–21 business days',
  },
  {
    slug: 'engagement-onboarding-flow',
    tag: 'Onboarding',
    title: 'Engagement → Onboarding Flow',
    shortTitle: 'Onboarding Flow',
    tagline: 'Signed letter. Zero manual setup.',
    description:
      'When a DocuSign engagement letter is signed, the system auto-creates the Karbon job, adds the client to QBO, and books their kickoff call via Calendly — hands-free.',
    detail:
      "A signed engagement letter used to mean 30–45 minutes of setup work: create the client in QBO, create the job in Karbon, send the kickoff link, update the pipeline. We collapse that to zero. The moment DocuSign registers a completed envelope, a webhook fires that creates the Karbon job with the right template, creates or updates the QBO customer record, and sends the client a Calendly link with a personalized note. You're notified when the kickoff is booked.",
    painPoints: [
      '30–45 min of manual setup every time a new client signs',
      'Client record created in QBO days after signing because staff are busy',
      'Karbon job opened with wrong template or missing fields',
      'Kickoff not booked for days because the link was sent manually',
    ],
    outcomes: [
      'DocuSign signed → Karbon job created (correct template) in <60 seconds',
      'QBO customer record created or updated automatically',
      'Calendly kickoff link sent to client with personalized message',
      'Partner notified when kickoff is booked — no chasing',
    ],
    stack: ['DocuSign Webhooks', 'Karbon API', 'QuickBooks Online API', 'Calendly API', 'Python / FastAPI'],
    setupPrice: '$1,200–$2,000',
    monthlyPrice: '$150–$250/mo',
    timeline: '10–14 business days',
  },
  {
    slug: 'missed-lead-text-back',
    tag: 'Lead Recovery',
    title: 'Missed-Lead Text-Back',
    shortTitle: 'Lead Text-Back',
    tagline: 'Respond before they call the next firm.',
    description:
      'A prospect calls after hours or submits a form. They get a personalized text in under 60 seconds — before they move on to your competitor.',
    detail:
      "Most accounting firm leads are lost not because the firm was the wrong fit, but because they were the second to respond. We build a text-back system that monitors your phone line and contact forms around the clock. When a call is missed or a form is submitted, a personalized SMS goes out in under 60 seconds — professionally worded, branded to your firm, with a simple reply-to-book mechanism. This system is already live at several firms and consistently converts referral leads that would otherwise have called the next name on the list.",
    painPoints: [
      'Missed calls after 5pm — no response until next morning',
      'Contact form submissions acknowledged hours or days later',
      'Referral leads calling competitors while waiting for a callback',
      'No system for tracking which leads were contacted and when',
    ],
    outcomes: [
      'Personalized SMS in <60 seconds for missed calls and form submissions',
      '24/7 coverage — weekends, evenings, holidays',
      'Branded, professional message — not a generic autoresponder',
      'Lead log: every contact attempt recorded with timestamp',
    ],
    stack: ['Twilio', 'n8n (workflow automation)', 'Python / FastAPI', 'Your existing phone system'],
    setupPrice: '$997–$1,500',
    monthlyPrice: '$100–$200/mo',
    timeline: '5–7 business days',
  },
  {
    slug: 'month-end-close-accelerator',
    tag: 'Close · Flagship',
    title: 'Month-End Close Accelerator',
    shortTitle: 'Close Accelerator',
    tagline: 'A 10-day close, compressed to 3.',
    description:
      'An agentic close engine that runs reconciliations, flags variances, drafts adjusting journal entries for review, and pushes a partner-ready close package — same day QBO is locked.',
    detail:
      "The month-end close is the single most expensive recurring workflow in a small accounting firm. We replace 10 days of senior-staff execution with a same-day agentic close. The system pulls bank, credit card, and payroll feeds, auto-reconciles to QBO, flags every variance over your threshold, drafts adjusting journal entries with explanations for partner review, and assembles the close package — all before the partner reviews their first email of the day. You approve, you don't rebuild.",
    painPoints: [
      'Close runs 7–10 days into the next month — partners reviewing too late to advise',
      'Senior staff spending hours on reconciliations a junior could supervise if it were drafted',
      'Adjusting JEs created from memory — no documented reasoning trail',
      'Close package assembled by hand into a deck or PDF every cycle',
    ],
    outcomes: [
      'Bank, credit card, and payroll feeds auto-reconciled before partner review',
      'Variance flags surfaced with prior-period context — no manual diffing',
      'Adjusting JEs drafted with reasoning notes, queued for one-click approval',
      'Branded close package PDF generated automatically — ready to deliver to client',
    ],
    stack: ['QuickBooks Online API', 'OpenAI (variance reasoning + JE drafts)', 'Python / FastAPI', 'Karbon / TaxDome integration'],
    setupPrice: '$2,500–$4,500',
    monthlyPrice: '$400–$700/mo',
    timeline: '21–30 business days',
  },
  {
    slug: 'ar-collections-agent',
    tag: 'AR · Cashflow',
    title: 'AR / Collections Agent',
    shortTitle: 'Collections Agent',
    tagline: 'Aging invoices chased — without the awkward partner email.',
    description:
      'A graduated collections agent that monitors AR aging, sends personalized reminders at 15/30/45/60 days, tracks promise-to-pay commitments, and escalates only when a partner actually needs to step in.',
    detail:
      "Most small firms write off 4–8% of revenue every year because nobody enjoys chasing AR. We build an agent that lives on top of your QBO AR and runs a graduated collections cadence — friendly nudge at 15 days, structured reminder at 30, payment plan offer at 45, partner escalation at 60. Every message is tone-matched to the client relationship using OpenAI, sent via SMS or email per client preference, and logged back to QBO. Partners only get involved when the agent has exhausted the standard cadence — and the data needed for that conversation is one click away.",
    painPoints: [
      '4–8% of revenue lost to write-offs because nobody chases past 30 days',
      'Generic dunning emails that damage long-standing client relationships',
      'No structured promise-to-pay tracking — same client makes the same promise monthly',
      'Partners blindsided when AR aging hits 90+ days with no warning',
    ],
    outcomes: [
      'Graduated reminder cadence at 15/30/45/60 days, fully automated',
      'Tone-matched messaging — formal for new clients, warmer for long-term relationships',
      'Promise-to-pay tracker — every commitment logged, every broken promise surfaced',
      'Partner-ready escalation report when the agent has done all it can',
    ],
    stack: ['QuickBooks Online API', 'Twilio + SendGrid', 'OpenAI (tone-matched copy)', 'Python / FastAPI'],
    setupPrice: '$1,800–$3,000',
    monthlyPrice: '$300–$500/mo',
    timeline: '14–21 business days',
  },
  {
    slug: 'cashflow-forecast-agent',
    tag: 'Advisory · Forecast',
    title: 'Cashflow Forecast Agent',
    shortTitle: 'Cashflow Forecast',
    tagline: 'A 13-week forecast you actually trust — refreshed every morning.',
    description:
      'A rolling 13-week cashflow forecast per client, pulled live from QBO actuals, AR/AP aging, payroll cadence, and recurring revenue — with auto-alerts for low balance projections and covenant risks.',
    detail:
      "Cashflow forecasting is the highest-margin advisory service most firms can't deliver consistently because the spreadsheets fall behind the moment a client's reality changes. We build an agent that maintains a rolling 13-week forecast per client, refreshed every morning from QBO actuals, AR/AP aging, payroll schedules, and known recurring lines. When projected balance crosses a threshold or a debt covenant is at risk, you and the client are alerted before it becomes a Friday-afternoon scramble. Forecasts are partner-reviewable, client-shareable, and historical accuracy is tracked so the model improves.",
    painPoints: [
      'Cashflow models built in Excel are stale within a week of delivery',
      'Clients only ask for forecasts during a crisis — too late to advise well',
      'No early warning when balances will trend negative or covenants will breach',
      'Advisory revenue capped because the workflow doesn\'t scale past 5–10 clients',
    ],
    outcomes: [
      '13-week rolling forecast per client, refreshed every morning from live QBO data',
      'Auto-alerts for low balance projections and covenant risk thresholds',
      'Client-facing dashboard — they see the forecast, you don\'t have to email it',
      'Forecast accuracy tracked over time — model improves, advisory credibility grows',
    ],
    stack: ['QuickBooks Online API', 'OpenAI (narrative commentary)', 'Python / FastAPI + pandas', 'Custom web dashboard'],
    setupPrice: '$2,000–$3,500',
    monthlyPrice: '$350–$600/mo',
    timeline: '21–30 business days',
  },
  {
    slug: 'business-intelligence-dashboard',
    tag: 'BI · Analytics',
    title: 'Business Intelligence Dashboard',
    shortTitle: 'BI Dashboard',
    tagline: 'The numbers that run your business — finally in one place.',
    description:
      'A Power BI, Tableau, or Looker Studio dashboard built around the operational metrics that actually drive your business — modeled, automated, and refreshed without anyone touching a spreadsheet.',
    detail:
      "Most small businesses run on a Frankenstein of CRM exports, QuickBooks downloads, and Excel pivot tables nobody fully trusts. We design and build a real BI dashboard the way an enterprise data team would — proper data model, automated refresh, role-based views, drill-downs that actually work — but scoped and priced for a small business. Built by a former data analyst who's done this in three industries, now with Claude as a co-pilot to deliver it 3x faster than agency rates.",
    painPoints: [
      'Same numbers reported three different ways across departments',
      'Monthly board pack rebuilt by hand from CRM, QBO, and Excel exports',
      'Dashboards built in Excel that break the moment one column moves',
      'Leadership making decisions on month-old or wrong data',
    ],
    outcomes: [
      'Single source of truth dashboard — operational, financial, and sales metrics in one place',
      'Automated daily/weekly refresh from your CRM, QBO, Stripe, ad platforms, and more',
      'Role-based views — partners see margin, ops sees throughput, sales sees pipeline',
      'Documented data model — when a metric is questioned, you can show exactly how it\'s built',
      'Portfolio-safe synthetic dashboard demo available at /dashboards/b2b-growth-command-center/',
    ],
    stack: ['Power BI / Tableau / Looker Studio', 'SQL + Python data layer', 'Connectors: QBO, HubSpot, Stripe, GA4, Meta Ads', 'Scheduled refresh + alerting'],
    setupPrice: '$1,800–$3,500',
    monthlyPrice: '$200–$400/mo',
    timeline: '14–21 business days',
  },
  {
    slug: 'excel-spreadsheet-automation',
    tag: 'Excel · Automation',
    title: 'Excel & Spreadsheet Automation',
    shortTitle: 'Excel Automation',
    tagline: 'The spreadsheet you spend 8 hours on — done in 8 seconds.',
    description:
      'Custom Excel and Google Sheets automations using Power Query, Office Scripts, VBA, or Apps Script — built by a data analyst who has automated these workflows in three previous corporate roles.',
    detail:
      "Every business has at least one spreadsheet that takes someone half a day, every week, to update. Sales reports rebuilt from CRM exports. Inventory reconciliations across three systems. Commission calculations, payroll prep, KPI rollups. We replace those workflows with one-click (or zero-click, scheduled) automations using the right tool for the job — Power Query for messy data shaping, Office Scripts or VBA for native Excel automation, Apps Script for Google Sheets, Python for anything that needs to break out of the cell. Pay once per workflow, no subscription required.",
    painPoints: [
      'A senior employee spending 4–8 hours/week on a single recurring spreadsheet',
      'Manual copy-paste between three systems to produce one report',
      'Spreadsheets that break every time the underlying export format changes',
      'No version control — three "final" copies of the same file in shared drives',
    ],
    outcomes: [
      'Recurring spreadsheet workflows reduced from hours to seconds (one click or scheduled)',
      'Resilient design — handles export format changes, missing columns, blank rows gracefully',
      'Documented + handed off — your team owns it, no consultant lock-in',
      'Optional scheduled execution + email delivery — runs without anyone opening the file',
    ],
    stack: ['Excel: Power Query, Office Scripts, VBA', 'Google Sheets: Apps Script', 'Python (pandas) for heavy lifts', 'Scheduled triggers + email delivery'],
    setupPrice: '$750–$2,500',
    monthlyPrice: 'Optional retainer',
    timeline: '5–10 business days',
  },
];

export function getService(slug: string): Service | undefined {
  return services.find((s) => s.slug === slug);
}
