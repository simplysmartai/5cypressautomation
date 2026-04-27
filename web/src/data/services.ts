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
];

export function getService(slug: string): Service | undefined {
  return services.find((s) => s.slug === slug);
}
