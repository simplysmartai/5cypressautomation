# 5 Cypress Automation — Data Handling Policy

**Effective Date:** March 2, 2026
**Owner:** Nick (Owner / Principal)
**Review cycle:** Annually or upon any material change in tools or services

---

## Purpose

This policy defines how 5 Cypress Automation receives, stores, processes, and disposes of client
data across all services — including dashboard analytics, automation workflows, bookkeeping/CFO
support, SEO, and marketing. Every client engagement that involves client-provided data is governed
by this policy.

---

## 1. Data We Accept

| Data Type | Examples | Classification |
|---|---|---|
| Business operational data | Orders, inventory, KPIs, workflows | Standard |
| Financial data | Revenue, expenses, P&L, invoices, bank statements | Sensitive |
| Employee data | Names, roles, compensation, performance | Sensitive |
| Customer / prospect data | Names, contacts, purchase history, pipeline | Sensitive |
| Health / patient data | Patient counts (aggregated), visit data | Very Sensitive (HIPAA) |
| System credentials | API keys, OAuth tokens, login credentials | Restricted |

**We do not accept (without explicit written authorization):**
- Full Social Security Numbers or Tax IDs
- Full credit card / bank account numbers
- Identifiable patient PHI without a signed HIPAA BAA
- Government-issued ID numbers

---

## 2. Approved Data Transfer Methods

**In order of preference:**

| Method | Use Case | Notes |
|---|---|---|
| **Copilot client portal** (portal.io) | All clients — standard default | Encrypted upload, client has own login. Start here. |
| **QBO API (OAuth)** | Bookkeeping / CFO clients | Direct connection — no file transfer at all. Best for financial data. |
| **Password-protected ZIP via encrypted email** | When Copilot not yet set up | Password shared via separate channel (text, not same email) |
| **OneDrive / SharePoint shared link** | Microsoft 365 clients | Use expiring links only (set 7-day expiration max) |
| **ShareFile** | 3+ clients with financial or HIPAA data | SOC 2 Type II; industry standard for accounting |

**Never use:**
- Unprotected email attachments
- Public Google Drive / Dropbox links
- Slack file shares
- USB drives / physical media
- Personal cloud storage accounts

---

## 3. Data Storage

### Local Storage (Active Projects)
```
clients/{client-id}/
├── data/
│   ├── raw/        ← Original files from client (delete sensitive files after processing)
│   └── processed/  ← Cleaned datasets (retain for project duration)
└── deliverables/   ← Final dashboard files, reports, exports
```

**Rules:**
- All work machines must have full-disk encryption enabled (BitLocker on Windows)
- Screen lock required when stepping away (timeout: 5 minutes max)
- No client data on personal devices or unencrypted portable drives
- No client data synced to personal cloud accounts (personal Dropbox, Google Drive, etc.)

### Copilot Portal
- Client files stored in Copilot's encrypted infrastructure per their security policies
- Each client has a separate workspace — no cross-client data access
- 5 Cypress admin account protected by a strong, unique password + MFA

### After Project Completion
- Raw sensitive files: deleted within 30 days of project completion
- Processed/cleaned datasets: retained up to 6 months post-project (in case of revisions)
- Dashboard files (.pbix, .twbx, .html): retained up to 12 months
- If client requests immediate deletion: completed within 10 business days, written confirmation provided

---

## 4. Who Has Access

Currently: **Nick (Owner/Principal) only.**

If contractors or additional personnel are engaged in the future:
- Must sign an NDA before any client data access
- Access limited to specific client data relevant to their assigned task
- Never given credentials or raw files — only processed outputs unless absolutely necessary
- Access revoked immediately upon completion of their assignment

---

## 5. Third-Party AI Tools

**Policy: Client data is never uploaded to third-party AI platforms.**

This includes: ChatGPT, Claude.ai (consumer), Gemini, Perplexity, or any other AI service where
data would be stored or used for model training.

AI assistance in this business uses:
- AI accessed within controlled development environments (VS Code Copilot, local context) where
  data is not retained or used for training
- Generated code and frameworks that run locally against client data
- Synthetic/anonymized data for testing and demonstration purposes

If a workflow requires AI processing of client data, it must be:
1. Approved in writing by the client
2. Disclosed in the Data Processing Agreement
3. Limited to AI providers with enterprise/zero-retention agreements

---

## 6. Contracts Required Before Data Transfer

| Data Classification | Contracts Required |
|---|---|
| Standard (operational/KPI) | NDA |
| Sensitive (financial, customer PII, employee) | NDA + DPA |
| Very Sensitive (HIPAA/health) | NDA + DPA + HIPAA BAA |
| System credentials / API keys | NDA + DPA (credentials section) |

**All contracts signed via Copilot client portal before any data changes hands. No exceptions.**

Templates:
- `templates/contracts/nda.md`
- `templates/contracts/master-service-agreement.md`
- `templates/contracts/data-processing-agreement.md`

---

## 7. Incident Response (Data Breach)

If a breach, unauthorized access, or accidental disclosure is suspected:

1. **Immediately** disconnect affected system from network if compromise is ongoing
2. Identify what data was exposed and to whom
3. **Within 72 hours:** Notify affected client(s) in writing via Copilot portal message + email
4. Notification must include:
   - What happened (to the best of our knowledge)
   - What data was involved
   - What we're doing to address it
   - What the client should do (if anything)
5. Document the incident in `logs/security-incidents.log`
6. Conduct root cause analysis and update this policy / security practices accordingly

---

## 8. Service-Specific Notes

### Dashboard Analytics Service
- Client sends data via Copilot portal or QBO API
- Raw files (if sensitive) deleted after `dashboard_data_processor.py` completes
- Final dashboard files retained in `clients/{id}/deliverables/`
- DPA required for financial or customer data

### Bookkeeping / CFO Support (Remy Lasers + future clients)
- Connect to QuickBooks Online via OAuth API — no raw file transfer needed for QBO data
- Bank statements / receipts accepted via Copilot portal (password-protected)
- Financial data is the most sensitive category — DPA always required
- Aggregated/summary data in dashboards is fine; line-item transaction data is Sensitive

### Automation Workflows (QBO, ShipStation, etc.)
- API credentials stored in `.env` on secure local machine — never in plaintext in code
- `.env` is gitignored — never committed to any repository
- Credentials documented in `clients/{id}/client.json` remain on local machine only

### SEO Services
- Usually involves public website URLs — low sensitivity
- If client provides internal analytics data (GA4, Search Console), treat as Standard
- No DPA required unless analytics includes PII-level data

---

## 9. Client Rights

Clients may request at any time:
- A copy of all data we hold about them or provided by them
- Deletion of their data (completed within 10 business days)
- A description of how their data is being used
- Written confirmation that data has been deleted

To submit a request: Contact nick@5cypress.com or via the Copilot client portal.

---

## 10. Policy Updates

This policy will be reviewed:
- Annually (each January)
- When adding a new service category
- When adding new tools or technology to the stack
- After any security incident

Clients will be notified of material changes via the Copilot portal.

---

*Last reviewed: March 2, 2026 | Next review: January 2027*
