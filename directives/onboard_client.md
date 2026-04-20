# Client Onboarding Directive

## Goal
Onboard a new partner by initiating the Root Audit and scheduling the Architecture Kickoff.

## Inputs
- `client_email`: Email address of the new client
- `client_name`: Full name of the client
- `company_name`: Client's company name

## Process

### Step 1: Validate Input & Initialize Profile
- Ensure client_email is valid
- Format names and company details for the CRM
- Prepare the internal "Root Audit" dossier template

### Step 2: Send Architecture Welcome
Use: `execution/send_email.py`

Email should include:
- **Subject**: "Welcome to 5 Cypress Labs | Initiating Your Architecture Audit"
- **Mission**: High-level focus on resilience and scale
- **The Journey**: The 5-stage Cypress implementation
- **Next Steps**: Link to the Architecture Kickoff session

Template structure:
```
Hi [Client Name],

Welcome to 5 Cypress Labs. We are ready to begin the process of architecting your resilient operations.

**Our Mission**
At 5 Cypress Labs, we don't just "automate"—we build the infrastructure that allows your business to endure and scale. Our focus is on creating deep-rooted reliability and branching logic that grows with you.

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
The 5 Cypress Labs Team
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

## Outputs
- Architecture welcome email sent
- Tailored calendar link generated
- Partner record initialized in global tracking
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
