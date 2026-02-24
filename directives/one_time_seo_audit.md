# One-Time SEO Intelligence Audit ($50-$100)

## Overview
A low-friction, high-value entry point for SMBs to receive a professional SEO audit. This serves as a "Tripwire" offer to convert prospects into long-term monthly retainers.

## Product Tiers
- **Basic (Free)**: Performance score, top 3 issues, limited mobile/desktop speed data.
- **Premium Intelligence Dossier ($50)**: Full breakdown, structural vulnerabilities, keyword gap analysis, competitive benchmarking, and "Instant PDF" generation.

## Workflow

### 1. Lead Capture & Free Scan
- User enters URL and Email on `seo-dashboard.html`.
- System runs `execution/seo_audit_runner.py` with limited scope.
- Frontend displays "Surface Level Results" and a "Unlock Premium Intelligence Dossier" CTA.

### 2. Payment (Stripe)
- User clicks "Unlock Full Report".
- Server creates a Stripe Checkout Session:
  - **Success URL**: `/seo-dashboard?session_id={CHECKOUT_SESSION_ID}&unlock=true`
  - **Cancel URL**: `/seo-dashboard`
- User completes $50 payment.

### 3. Verification & Unlocking
- Server receives Stripe Webhook or verifies session upon redirect.
- Database marks record `seo_audits[session_id]` as `paid`.
- Redirects user to `public/seo-report.html` with full data visibility.

### 4. Continuity (Upsell)
- Report includes a CTA for "Free Strategy Call" to discuss fixing the vulnerabilities found.
- Triggers `directives/discovery_call.md`.

## Technical Implementation
- **Tool**: `execution/seo_audit_runner.py`
- **Database**: `platform.db` table `seo_audits`
- **Payment**: Stripe API (Node.js)
- **Email**: Follow-up email via `send_email` tool with PDF attachment if possible.

## Edge Cases
- **Payment Failure**: Return to dashboard with error toast.
- **Duplicate Audit**: Check if same domain was audited in last 24h, offer "View Existing" if paid.
- **Invalid URL**: Frontend validation for TLD and connectivity.
