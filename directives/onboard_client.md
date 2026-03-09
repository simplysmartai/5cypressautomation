# Client Onboarding Directive

## Goal
Onboard a new partner by initiating the Root Audit and scheduling the Architecture Kickoff.

## Inputs
- `client_email`: Email address of the new client
- `client_name`: Full name of the client
- `company_name`: Client's company name

## Agent Mode

> This directive has 4+ steps and touches external APIs. Follow the two-phase protocol.

**MODE: PLANNING** — Before running any script, confirm:
- [ ] All three inputs (email, name, company) are present and valid
- [ ] Which onboarding path applies (Automation / Dashboard / Bookkeeping)
- [ ] Contracts required for this service type are identified
- [ ] Credentials for email and calendar scripts are available in `.env`
- [ ] Client does not already exist in the system (check for duplicates)

**MODE: EXECUTION** — Once planning is confirmed:
- Work through steps sequentially; only one step `in_progress` at a time
- Mark each step `completed` before moving to the next
- On any script failure, log the error and surface to user — do not retry silently more than 3 times
- Update this directive if new edge cases are discovered

## Process

### Step 1: Validate Input & Initialize Profile
- Ensure client_email is valid
- Format names and company details for the CRM
- Prepare the internal "Root Audit" dossier template

### Step 2: Send Architecture Welcome
Use: `execution/send_email.py`

Email should include:
- **Subject**: "Welcome to 5 Cypress Automation | Initiating Your Architecture Audit"
- **Mission**: High-level focus on resilience and scale
- **The Journey**: The 5-stage Cypress implementation
- **Next Steps**: Link to the Architecture Kickoff session

Template structure:
```
Hi [Client Name],

Welcome to 5 Cypress Automation. We are ready to begin the process of architecting your resilient operations.

**Our Mission**
At 5 Cypress Automation, we don't just "automate"—we build the infrastructure that allows your business to endure and scale. Our focus is on creating deep-rooted reliability and branching logic that grows with you.

**The Cypress Journey**
1. Root Identification (Audit) - Deep dive into your existing infrastructure and bottlenecks.
2. Architecture Design (Blueprint) - Mapping the resilient triggers and logic flows.
3. System Branching (Build) - Developing the core automation engines and redundant failovers.
4. Scale Hardening (Testing) - Rigorous stress tests and edge-case validation.
5. Endurance Support (Launch) - Deployment and ongoing heartbeat monitoring.

**Immediate Next Step: Schedule Your Architecture Kickoff**
Please use the secure link below to book your 45-minute kickoff session. During this time, we will initiate your Root Audit:
[Calendar Link]

We look forward to building the systems that power your growth.

Best regards,
The 5 Cypress Automation Team
```

### Step 3: Create Architecture Session Link
Use: `execution/create_calendar_link.py`

- Create a scheduling link for a 45-minute "Architecture Kickoff & Root Audit"
- Include meeting description with system access requirements
- Set availability for the next 2 weeks
- Return the link to include in the welcome email

### Step 4: Log Partner Initiation
- Record the partnership start with timestamp
- Store partner details in the Endurance Dashboard
- Track status through the "Rooting" phase

## Service-Specific Onboarding Paths

### Automation Services (default path)
Follow Steps 1–4 above. Proceed to the relevant directive after kickoff.

### Dashboard Analytics Service
After Step 1 (validate input), branch to:

1. **Send dashboard intro email** (modify Step 2 template → reference dashboard service)
2. **Set up Copilot client portal workspace** — create client workspace at portal.io before kickoff call
3. **Share discovery questionnaire** — send `documents/dashboard-discovery.md` via Copilot portal;
   ask client to review before the kickoff call
4. **Sign contracts before data transfer:**
   - NDA — always required (use `templates/contracts/nda.md`)
   - DPA — required if client will share financial, health, or customer data
     (use `templates/contracts/data-processing-agreement.md`)
   - MSA — for ongoing engagements (use `templates/contracts/master-service-agreement.md`)
   - Deliver all contracts via Copilot portal e-sign; no work begins until signed
5. **Schedule discovery call** (45 min) — complete `documents/dashboard-discovery.md` on the call
6. **Data intake after call** — client uploads files via Copilot portal or QBO API connection;
   refer to `documents/data-handling-policy.md` for approved transfer methods
7. **Proceed to build** — run `execution/dashboard_data_processor.py` then
   `execution/generate_dashboard.py` per `directives/dashboard_service.md`

### Bookkeeping / CFO Service
After Step 1, branch to:

1. **Higher sensitivity path** — DPA required before any conversation involving actual financial data
2. **Set up Copilot portal workspace** immediately
3. **QBO OAuth connection** (preferred over file transfer):
   - Client authorizes 5 Cypress read access in their QBO account
   - Populate `clients/{id}/client.json` → `api_access.qbo_company_id` on connection
   - See `directives/form_to_invoice_shipping_inventory.md` for QBO integration details
4. **All contracts signed first** — NDA + DPA + MSA before any data or system access
5. Follow standard kickoff flow (Steps 2–4)

## Outputs
- Architecture welcome email sent
- Copilot portal workspace created (all service types)
- Tailored calendar link generated
- Partner record initialized in global tracking
- Contracts sent for signature (as applicable to service type)
- Confirmation message

## Error Handling

### Invalid Contact Info
- Validate email and data integrity
- Return failure signal if initialization fails

### Calendar Conflict
- Alert if kickoff slots are restricted
- Suggest alternative contact methods

### Email Send Failure
- Retry up to 3 times with exponential backoff
- Log error details
- Notify admin if all retries fail

### Calendar Creation Failure
- Fall back to generic scheduling instructions
- Include admin contact info for manual scheduling

## Tools Used
1. `execution/send_email.py` - Send welcome email via SMTP/Resend
2. `execution/create_calendar_link.py` - Generate calendar scheduling link
3. `execution/log_activity.py` - Track onboarding events

## Edge Cases

### Duplicate Onboarding
- Check if client already onboarded
- Option to resend welcome email or skip

### Missing Contact Info
- Require at minimum a valid email address
- Gracefully handle missing name/company

### Timezone Handling
- Default to EST/UTC for calendar availability
- Include timezone selector in calendar link

## Success Criteria
- [ ] Email delivered successfully
- [ ] Calendar link is accessible and functional
- [ ] Client record logged
- [ ] No errors in execution

## Example Usage
```
Onboard client@example.com
Onboard john.smith@acme.com with company name "Acme Corp"
```

## Notes
- Always use professional, friendly tone
- Keep email concise but informative
- Ensure calendar link works before sending email
- Follow up if no response within 48 hours (separate directive)
