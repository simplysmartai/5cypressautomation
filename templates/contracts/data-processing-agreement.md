# Data Processing Agreement

**Between:** 5 Cypress Automation ("Processor")
**And:** ___________________________ ("Controller / Client")
**Effective Date:** ___________________________
**Related MSA Date:** ___________________________

---

> **When to use this agreement:** Required before any data transfer when the Client's data includes:
> financial records, P&L, revenue figures, employee information, customer PII, patient/health data,
> or any other sensitive personal or business data. Sign BEFORE any files change hands.

---

## 1. Definitions

- **"Personal Data"** means any information relating to an identified or identifiable natural person.
- **"Processing"** means any operation performed on data, including collection, storage, analysis,
  modification, transmission, or deletion.
- **"Controller"** means the Client, who determines the purposes and means of data processing.
- **"Processor"** means 5 Cypress Automation, who processes data on behalf of the Controller.
- **"Business Data"** means non-personal financial, operational, or organizational data belonging
  to the Client.

---

## 2. Scope of Processing

**2.1 Purpose of Processing**
5 Cypress Automation will process Client data solely for the following purposes:
- Building and maintaining data visualization dashboards
- Generating analytics, reports, and insights
- Providing automation and workflow services as described in the applicable SOW
- Data cleaning, transformation, and modeling in support of the above

**2.2 Categories of Data**
The following categories of data may be processed under this Agreement:

| Category | Examples | Sensitivity |
|---|---|---|
| Financial data | Revenue, expenses, invoices, P&L | High |
| Operational data | Orders, inventory, workflows, KPIs | Standard |
| Employee data | Names, roles, performance metrics | High |
| Customer data | Names, purchase history, contacts | High |
| Health data | Patient records, visit counts (aggregated) | Very High (HIPAA) |

**2.3 Data Not Permitted**
Unless explicitly authorized in writing, 5 Cypress Automation will NOT process:
- Full Social Security Numbers or Tax ID numbers
- Credit card numbers or full account numbers
- Passwords or authentication credentials
- Identifiable patient medical records (PHI) unless a separate HIPAA BAA is in place

---

## 3. Processor Obligations

5 Cypress Automation agrees to:

**(a) Documented Instructions Only**
Process data only on documented instructions from the Client, as specified in the SOW or written
communications. If Processing is required by law, 5 Cypress Automation will notify Client before
processing unless prohibited.

**(b) Confidentiality**
Ensure all personnel with access to Client data are bound by confidentiality obligations at least
as stringent as this Agreement.

**(c) Security Measures**
Implement appropriate technical and organizational security measures including:
- Encrypted local storage for all Client data files
- Access limited to authorized personnel only (currently: Nick, owner)
- Secure data transfer methods only (Copilot portal, encrypted email, ShareFile, or QBO API)
- No storage of Client data on unencrypted portable drives or personal devices
- Screen lock and device encryption enabled on all work devices

**(d) Sub-Processors**
5 Cypress Automation will not engage sub-processors for Client data without prior written approval.
Currently authorized sub-processors: None (all processing performed by 5 Cypress Automation directly).

**(e) Data Subject Rights**
Assist Client in responding to requests from individuals exercising their data rights (access,
correction, deletion) as applicable under GDPR, CCPA, or other applicable law.

**(f) Security Incident Notification**
Notify Client within 72 hours of becoming aware of any breach, unauthorized access, or accidental
disclosure of Client data.

**(g) Data Deletion / Return**
Upon completion of services or written request:
- Return all Client data in a portable format (CSV, Excel)
- Delete all copies of raw source files within 10 business days
- Retain only anonymized/aggregated outputs unless Client requests full deletion
- Provide written certification of deletion upon request

---

## 4. Controller Obligations

The Client (Controller) agrees to:

(a) Only provide data that they have legal authority to share;
(b) Ensure data subjects have been appropriately notified of processing activities where required;
(c) Notify 5 Cypress Automation of any changes to data categories or processing requirements;
(d) Not provide data categories marked as "Not Permitted" above without express written agreement.

---

## 5. Data Retention

| Data Type | Retention Period | Deletion Method |
|---|---|---|
| Raw source files (sensitive) | Duration of project + 30 days | Secure delete (overwrite) |
| Cleaned/processed datasets | Duration of engagement + 6 months | Secure delete |
| Dashboard files (.pbix, .twbx, HTML) | Duration of engagement + 12 months | Secure delete |
| Communications about Client data | 2 years | Secure delete |

Retention periods may be extended by mutual written agreement.

---

## 6. Audit Rights

Client may request written confirmation of compliance with this Agreement no more than once per
year. Compliance documentation will be provided within 10 business days of the request.

---

## 7. HIPAA Provisions (Health Data Only)

_Complete this section only if Client data includes Protected Health Information (PHI)._

If Client data contains PHI as defined under HIPAA:
- The parties agree to execute a separate Business Associate Agreement (BAA) before any PHI transfer
- 5 Cypress Automation will not process PHI until a BAA is signed and in effect
- All HIPAA-covered PHI will be stored in HIPAA-compliant infrastructure (ShareFile with BAA,
  or equivalent) rather than standard local storage
- PHI will never be included in web-hosted dashboards accessible via public or semi-public URLs

PHI involved in this engagement: [ ] Yes — BAA required and signed  [ ] No

---

## 8. Governing Law

This Agreement shall be governed by the laws of the State of ___________________________.

---

## 9. Order of Precedence

In the event of a conflict, this Data Processing Agreement takes precedence over the Master Service
Agreement with respect to data handling obligations.

---

## 10. Term

This Agreement remains in effect for the duration of the services described in the related MSA and
for the applicable retention periods in Section 5 thereafter.

---

## Signatures

**5 Cypress Automation (Processor)**

Signature: ___________________________
Name: Nick ___________________________
Title: Owner / Principal
Date: ___________________________

---

**Client (Controller)**

Signature: ___________________________
Name: ___________________________
Title: ___________________________
Company: ___________________________
Date: ___________________________

---

*Deliver and collect signatures via the Copilot client portal BEFORE any data transfer.*
*File signed copy to `clients/{client-id}/documents/dpa-signed-{date}.pdf`*
