# SEO Sales Machine (Outreach Automation)

## Overview
Automated lead generation and outreach for the SEO Intelligence Service. This workflow identifies domains with poor SEO performance and sends a personalized "Teaser Dossier" to the owner, inviting them to unlock the full report.

## Process

### 1. Market Research (Lead Identification)
- **Goal**: Identify 50-100 local or niche websites weekly.
- **Tool**: `execution/google_maps_scraper.py`
- **Output**: A list of domains and phone/address info.

### 2. Preliminary Audit (The Teaser)
- **Goal**: Run a lightweight scan to get an "SEO Score" and 3 critical issues.
- **Tool**: `execution/seo_audit_runner.py` (Scope: Instant)
- **Persistence**: Store results in `platform.db` table `seo_audits` with status `prospect`.

### 3. Personalization & Outreach
- **Goal**: Generate a high-converting outreach email/message.
- **Template**: `templates/seo_teaser.md`
- **Logic**: 
    - "Your site scored {{score}}/100."
    - "We found {{issue_count}} critical vulnerabilities including: {{issue_1}}."
    - "View your public summary: `https://simplysmartautomation.com/seo-report.html?domain={{domain}}`"

### 4. Conversion (To Phase 2)
- User visits summary -> Clicks "Unlock Full Dossier" -> Stripe Checkout ($50).
- Successful payment triggers "Verified Audit" status and sends full PDF.

## Technical Tasks
- [ ] Create `templates/seo_teaser.md` (Luxury/Professional tone).
- [ ] Update `execution/seo_audit_runner.py` to handle "teaser-only" runs (if needed).
- [ ] Create `execution/seo_outreach_prepper.py` to orchestrate audit + email drafting.

## ROI Targets
- **Lead Cost**: $0 (internal scraping)
- **Conversion Rate**: 2-5% to Paid Audit.
- **LTV**: Paid Audit ($50) -> Retainer ($1,200/mo).
