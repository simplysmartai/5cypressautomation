# Universal Workflow Builder System

## Overview
This system enables SSA to handle **any use case thrown at us** with confidence. Instead of saying "let me see if we can do that," we have a systematic approach to analyze, design, and implement workflows for any business process.

**Core Principle:** Every business workflow follows patterns. Once you understand the patterns, you can solve anything.

---

## The 5 Universal Workflow Patterns

### Pattern 1: Trigger → Action (Simple Automation)
**When X happens, do Y**

**Examples:**
- New lead submitted → Send welcome email
- Invoice paid → Update accounting system
- Deal closed → Create project folder

**Components:**
- Trigger (event that starts the workflow)
- Action (single task to perform)
- Error handling (what if it fails?)

**Template:** `trigger_action.json`

---

### Pattern 2: Trigger → Conditional Logic → Actions (Decision Tree)
**When X happens, if Y is true, do Z, else do A**

**Examples:**
- New lead → If high-value, assign to senior rep, else auto-nurture
- Proposal sent → If opened within 24hrs, send follow-up, else wait 3 days
- Invoice overdue → If <30 days, gentle reminder, else escalate

**Components:**
- Trigger
- Conditional branches (if/else logic)
- Multiple action paths
- Error handling

**Template:** `conditional_logic.json`

---

### Pattern 3: Sequential Process (Multi-Step Workflow)
**Do A, then B, then C, in order**

**Examples:**
- Client onboarding: Welcome email → Intake form → Kickoff call → Project setup
- Invoice process: Generate → Send → Track → Follow-up → Mark paid
- Content creation: Draft → Review → Approve → Publish → Promote

**Components:**
- Ordered steps (must happen in sequence)
- Delay/wait states (pause between steps)
- Progress tracking (where are we in the process?)
- Rollback logic (if step fails, undo previous steps)

**Template:** `sequential_process.json`

---

### Pattern 4: Parallel Execution (Do Multiple Things at Once)
**When X happens, do A, B, and C simultaneously**

**Examples:**
- New client → Create Slack channel + Google Drive folder + Asana project + Send welcome email (all at once)
- Lead qualified → Add to CRM + Add to email sequence + Notify sales rep + Update dashboard
- Document signed → Store in Dropbox + Update database + Send confirmation + Trigger billing

**Components:**
- Single trigger
- Multiple parallel actions
- Synchronization point (wait for all to complete)
- Partial failure handling (what if 1 of 4 actions fails?)

**Template:** `parallel_execution.json`

---

### Pattern 5: Looping/Iteration (Repeat for Multiple Items)
**For each item in list, do X**

**Examples:**
- For each lead in list → Send personalized outreach email
- For each invoice → Check payment status → Send reminder if unpaid
- For each project milestone → Generate report → Email to stakeholder

**Components:**
- Collection/list of items
- Loop logic (iterate through each)
- Action performed on each item
- Batch processing (do in groups if list is large)
- Aggregation (collect results at the end)

**Template:** `loop_iteration.json`

---

## The Confidence Framework

### Step 1: Client Describes Use Case (Discovery)
**Ask these questions:**

1. **What triggers this workflow?**
   - Manual action? (user clicks button, fills form)
   - System event? (new record created, time-based, status change)
   - External signal? (email received, webhook fired, API call)

2. **What needs to happen?**
   - Single action or multiple steps?
   - Need to make decisions (if/else)?
   - Parallel or sequential?
   - Repeated for multiple items?

3. **What are the exceptions?**
   - What could go wrong?
   - What if data is missing?
   - What if external system is down?
   - What's the fallback plan?

4. **How do we know it worked?**
   - Success criteria (what does "done" look like?)
   - Monitoring/alerts needed?
   - Reporting requirements?

### Step 2: Map to Pattern (Classification)
Based on answers, identify which of the 5 patterns (or combination) fits:

| If client says... | Pattern | Complexity |
|-------------------|---------|------------|
| "When X happens, do Y" | Trigger → Action | Simple |
| "Do different things based on..." | Conditional Logic | Medium |
| "Steps that must happen in order" | Sequential Process | Medium |
| "Do several things at the same time" | Parallel Execution | Medium-High |
| "Do this for every item in..." | Loop/Iteration | High |
| "Combination of above" | Composite Pattern | High |

### Step 3: Design Workflow (Blueprint)
**Create flowchart/diagram:**

```
[Trigger] 
   ↓
[Condition?] 
   ├─ Yes → [Action A] → [Action B] → [Done]
   └─ No  → [Action C] → [Done]
```

**Document:**
- Each node (step in workflow)
- Connections (how steps link together)
- Data passed between steps
- Error handling at each point

**Tools:**
- Pen & paper (fastest for discovery calls)
- Miro/Figma (for client presentations)
- n8n visual editor (for implementation)

### Step 4: Validate Feasibility (Confidence Check)
**Questions to answer before committing:**

1. **Do we have access to required systems?**
   - API available? (check documentation)
   - Authentication method? (OAuth, API key, etc.)
   - Rate limits? (can we handle the volume?)

2. **Are there timing constraints?**
   - Real-time execution required?
   - Batch processing acceptable?
   - Time-sensitive dependencies?

3. **What's the data quality?**
   - Clean and structured?
   - Need validation/cleanup?
   - Missing data scenarios?

4. **What's the failure mode?**
   - Can we retry automatically?
   - Need human intervention?
   - Data consistency risks?

**Confidence Levels:**
- 🟢 **High Confidence (95%+):** Standard pattern, systems we know, low risk
- 🟡 **Medium Confidence (75-95%):** New system integration, some unknowns, manageable risk
- 🔴 **Low Confidence (<75%):** Complex logic, untested integrations, need proof-of-concept first

**Never say "we can't do that" unless truly impossible. Say:** 
- High confidence: "Yes, we can deliver that in [timeline]"
- Medium confidence: "Yes, we'll need 2-3 days to validate the integration, then [timeline]"
- Low confidence: "Great question. Let me research the API and get back to you within 24 hours with a concrete plan"

### Step 5: Implement Workflow (Execution)
**Use our 3-layer architecture:**

1. **Directive (What to do)**
   - Create/update directive document
   - Define inputs, process, outputs, edge cases

2. **Orchestration (Decision making)**
   - Route to appropriate execution script
   - Handle errors and exceptions
   - Log activity

3. **Execution (Doing the work)**
   - Write Python script (deterministic logic)
   - Connect APIs, process data, handle errors
   - Test thoroughly

**Quality Checklist:**
- ✅ Happy path works (normal scenario)
- ✅ Error handling works (API down, bad data, etc.)
- ✅ Logging/monitoring in place
- ✅ Documentation written
- ✅ Client trained on usage

---

## Integration Playbook (Common Systems)

### CRM Systems
| Platform | Difficulty | API Docs | Notes |
|----------|-----------|----------|-------|
| HubSpot | Easy | [Link](https://developers.hubspot.com/) | Excellent API, OAuth2 |
| Salesforce | Medium | [Link](https://developer.salesforce.com/) | Powerful but complex |
| Pipedrive | Easy | [Link](https://developers.pipedrive.com/) | Simple REST API |
| Close | Easy | [Link](https://developer.close.com/) | API key auth |

### Accounting
| Platform | Difficulty | API Docs | Notes |
|----------|-----------|----------|-------|
| QuickBooks Online | Medium | [Link](https://developer.intuit.com/) | OAuth2, sandbox available |
| Xero | Medium | [Link](https://developer.xero.com/) | OAuth2, good docs |
| FreshBooks | Easy | [Link](https://www.freshbooks.com/api) | Simple REST API |

### Email/Marketing
| Platform | Difficulty | API Docs | Notes |
|----------|-----------|----------|-------|
| Gmail API | Easy | [Link](https://developers.google.com/gmail/api) | OAuth2, powerful |
| Mailchimp | Easy | [Link](https://mailchimp.com/developer/) | API key auth |
| SendGrid | Easy | [Link](https://docs.sendgrid.com/) | API key auth |
| ActiveCampaign | Medium | [Link](https://developers.activecampaign.com/) | REST API |

### Project Management
| Platform | Difficulty | API Docs | Notes |
|----------|-----------|----------|-------|
| Asana | Easy | [Link](https://developers.asana.com/) | Excellent docs |
| Trello | Easy | [Link](https://developer.atlassian.com/cloud/trello/) | API key + token |
| Monday.com | Medium | [Link](https://developer.monday.com/) | GraphQL API |
| ClickUp | Easy | [Link](https://clickup.com/api) | REST API |

### Document/Storage
| Platform | Difficulty | API Docs | Notes |
|----------|-----------|----------|-------|
| Google Drive | Easy | [Link](https://developers.google.com/drive) | OAuth2 |
| Dropbox | Easy | [Link](https://www.dropbox.com/developers) | OAuth2 |
| DocuSign | Medium | [Link](https://developers.docusign.com/) | OAuth2, e-signature |

**Pro Tip:** If a system isn't listed, check:
1. Does it have a Zapier integration? (if yes, likely has API)
2. Does it have webhook support? (easier than polling)
3. Is there an n8n node available? (pre-built integration)

---

## Standard Response Times

When client asks "Can you automate X?"

| Scenario | Response | Timeline |
|----------|----------|----------|
| **Standard pattern + known system** | "Yes, we can deliver that in 3-5 days" | Immediate (on call) |
| **New system, standard pattern** | "Yes, I need 24 hours to validate the API, then 5-7 days" | Within 24 hrs |
| **Complex logic, known systems** | "Yes, 1-2 weeks with testing" | Immediate (on call) |
| **New system + complex logic** | "Let me research and send you a detailed plan by [date]" | Within 48 hrs |
| **Truly impossible** | "That specific approach won't work, but here's what we can do instead..." | Immediate (offer alternative) |

---

## Edge Case Handling

### "What if the API doesn't support what we need?"
**Options (in order of preference):**
1. **Workaround:** Use alternate API endpoint or creative logic
2. **Batch processing:** If real-time not possible, run on schedule
3. **Hybrid approach:** Automate 80%, manual for 20%
4. **Build custom integration:** More work, but possible
5. **Alternative tool:** Suggest different system that supports it

### "What if data quality is poor?"
**Options:**
1. **Data validation layer:** Clean/validate before processing
2. **Manual review step:** Flag suspicious data for human check
3. **Baseline cleanup project:** One-time data cleanup, then automate
4. **Training:** Teach client team data hygiene best practices

### "What if client's systems are too locked down?"
**Options:**
1. **Middleware:** Build intermediate system that bridges gap
2. **Export/import:** Batch file processing instead of live API
3. **Screen scraping:** Last resort, but possible (less reliable)
4. **Request access:** Help client get API access from IT team

---

## Workflow Templates Library

### Ready-to-Use Templates
Located in `directives/workflow_templates/`:

1. `lead_capture_to_crm.json` — Webform → CRM
2. `invoice_generation_payment.json` — Generate → Send → Track
3. `proposal_followup.json` — Send proposal → Track opens → Follow-up
4. `client_onboarding_sequence.json` — Welcome → Intake → Kickoff
5. `email_sequence_automation.json` — Drip campaigns
6. `document_generation_signature.json` — Create doc → Send for signature
7. `deal_won_celebration.json` — Close deal → Notify team → Create project
8. `pipeline_stage_progression.json` — Move deals through stages automatically
9. `lead_scoring_routing.json` — Score leads → Route to right rep
10. `abandoned_cart_recovery.json` — Detect abandonment → Send reminder

**How to use:**
1. Copy template JSON
2. Replace placeholders with client-specific values
3. Test in n8n/Zapier
4. Deploy to production

---

## Launch Checklist (for any new workflow)

### Pre-Launch
- [ ] Flowchart/diagram reviewed with client
- [ ] All integrations tested (auth working, API calls successful)
- [ ] Error handling implemented
- [ ] Logging/monitoring configured
- [ ] Documentation written
- [ ] Client trained

### Launch Day
- [ ] Deploy to production
- [ ] Monitor first 24 hours closely
- [ ] Fix any edge cases discovered
- [ ] Confirm success metrics met

### Post-Launch
- [ ] Week 1 check-in (any issues?)
- [ ] Month 1 review (performance data)
- [ ] Add to monthly insights reporting
- [ ] Document lessons learned

---

## Key Takeaway

**You don't need to know every API or system upfront. You need:**
1. **Pattern recognition** — Map use case to one of 5 patterns
2. **Research skills** — Find API docs, read them fast, validate feasibility
3. **Systematic approach** — Follow this framework every time
4. **Confidence** — Trust the process, communicate clearly, deliver reliably

**With this system, you can confidently say "yes" to 95%+ of use cases and deliver 99.9% of the time.**
