# Send Contract Directive

> Generate and send contracts after proposal acceptance.

## Purpose

When a prospect accepts a proposal, generate the appropriate contract documents and send for signature.

## Contract Types

### 1. Master Service Agreement (MSA)
- One-time agreement covering all future work
- General terms, liability, IP ownership
- Template: `templates/contracts/master-service-agreement.md`

### 2. Statement of Work (SOW)
- Project-specific scope and deliverables
- Timeline and milestones
- Pricing for this specific project
- Template: `templates/contracts/statement-of-work.md`

### 3. Non-Disclosure Agreement (NDA)
- When handling sensitive data
- Optional, use when appropriate
- Template: `templates/contracts/nda.md`

## Standard Flow

1. **New Client:** MSA + SOW (both required)
2. **Returning Client:** SOW only (MSA already signed)
3. **Sensitive Project:** Add NDA before discovery

## Execution

### Generate Contract
```bash
python execution/create_contract.py \
  --client "client-slug" \
  --type "sow" \
  --proposal "proposal-2026-01-21"
```

**Parameters:**
- `--client`: Client slug
- `--type`: msa, sow, nda, or bundle (msa+sow)
- `--proposal`: Reference proposal for SOW details
- `--output`: pdf, google-doc, or docusign

### Script Actions

1. Load client info from `clients/[slug]/client.json`
2. Load proposal from `clients/[slug]/proposals/[proposal].md`
3. Populate contract template
4. Generate document
5. Save to `clients/[slug]/contracts/`
6. Send via email or DocuSign
7. Log activity

## Contract Fields

### MSA Variables
- `{{client_name}}` - Legal business name
- `{{client_address}}` - Business address
- `{{client_contact}}` - Signer name and title
- `{{effective_date}}` - Contract start date
- `{{agency_name}}` - Simply Smart Automation LLC

### SOW Variables
- All MSA variables, plus:
- `{{project_name}}` - Project title
- `{{scope}}` - Detailed scope from proposal
- `{{deliverables}}` - Bullet list of deliverables
- `{{timeline}}` - Project timeline with milestones
- `{{price}}` - Total project price
- `{{deposit}}` - Deposit amount
- `{{payment_schedule}}` - Payment terms

## Signature Options

### Option 1: DocuSign (Preferred for enterprise)
- Professional appearance
- Audit trail
- Automated reminders
- Cost: ~$10/envelope

### Option 2: Email Acceptance
- Send PDF via email
- Client replies "I accept" 
- Screenshot/email serves as acceptance
- Free, faster for small deals

### Option 3: Manual
- Print, sign, scan
- For clients who prefer traditional

## After Signature

1. Save signed copy to `clients/[slug]/contracts/`
2. Update client status: `python execution/update_client.py [slug] --status active`
3. Send deposit invoice: `directives/send_invoice.md`
4. Begin onboarding: `directives/onboard_client.md`
5. Log activity

## Output

Contracts saved to:
```
clients/[slug]/contracts/
├── msa-2026-01-21.pdf
├── msa-2026-01-21-signed.pdf
├── sow-project-name-2026-01-21.pdf
└── sow-project-name-2026-01-21-signed.pdf
```

## Related Directives
- `create_proposal.md` - Create proposal first
- `send_invoice.md` - Send deposit after signing
- `onboard_client.md` - Begin project kickoff
