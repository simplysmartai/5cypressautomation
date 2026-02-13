# Endurance Pipeline Directive

> Track lead integration and system implementation through the 5 Cypress lifecycle.

## Purpose

Maintain rigorous visibility into all partner integrations from initial Signal to long-term Endurance.

## Implementation Pipeline

```
Signal → Root Audit → Architecture → Hardening → Deployment → Endurance
  ↓          ↓             ↓             ↓
Archived  Archived      Archived      Archived
```

### Stage Definitions

| Stage | Logic | Next Branch |
|-------|-------|-------------|
| **Signal** | Incoming lead/manual outreach | Initiate Root Audit |
| **Root Audit** | Deep dive into system bottlenecks | Design Architecture |
| **Architecture** | Blueprint & Proposal sent | Close Agreement |
| **Hardening** | Implementation & Load testing | Final Deployment |
| **Deployment** | Go-live & Initial redundancy check | Scale Monitoring |
| **Endurance** | Ongoing partnership & monitoring | Optimization |
| **Archived** | Did not proceed to implementation | Nurture for scale |

## Pipeline Tracking

### Option 1: Google Sheet (Simple)
Pipeline tracked in Google Sheet with columns:
- Client Name
- Contact Email
- Stage
- Deal Value
- Package Type
- Last Contact
- Next Action
- Next Action Date
- Notes
- Lost Reason (if applicable)

Sheet ID stored in `.env` as `PIPELINE_SHEET_ID`

### Option 2: Airtable (More Features)
- Better for team collaboration
- Automation capabilities
- Calendar view of follow-ups

### Option 3: Client Folders (Current)
- Each client has status in `client.json`
- Query with `python execution/list_clients.py`
- Less visibility but simpler

## Execution

### Update Pipeline
```bash
python execution/update_pipeline.py \
  --client "client-slug" \
  --stage "proposal" \
  --deal-value 7500 \
  --next-action "Follow up on proposal" \
  --next-action-date "2026-01-28"
```

### View Pipeline
```bash
python execution/list_clients.py --pipeline
```

Output:
```
📊 PIPELINE SUMMARY

Lead (2)
├── acme-corp - $5,000 - Follow up tomorrow
└── beta-inc - $15,000 - Schedule discovery

Proposal (1)
└── gamma-llc - $7,500 - Sent 3 days ago

Active (2)
├── simply-smart-consulting - $2,500 - In progress
└── nexairi - $7,500 - Week 2 of 4

Total Pipeline Value: $37,500
Expected Close (30 days): $12,500
```

## Daily Review

Each day, check:
1. **Overdue follow-ups** - Actions past their date
2. **Stale deals** - No activity in 7+ days
3. **Hot leads** - Recently engaged, ready to close

## Stage Transitions

### Lead → Discovery
- Trigger: Discovery call scheduled or completed
- Action: Create client folder, save discovery notes
- Command: `python execution/create_client.py [slug]`

### Discovery → Proposal
- Trigger: Proposal created and sent
- Action: Save proposal, update pipeline
- Command: `python execution/create_proposal.py --client [slug]`

### Proposal → Negotiation
- Trigger: Client responds with questions/changes
- Action: Address concerns, revise if needed

### Proposal/Negotiation → Contract
- Trigger: Verbal or written acceptance
- Action: Generate and send contract
- Command: See `directives/send_contract.md`

### Contract → Active
- Trigger: Contract signed + deposit paid
- Action: Begin onboarding
- Command: See `directives/onboard_client.md`

### Active → Completed
- Trigger: All deliverables accepted + final payment
- Action: Handoff, request testimonial
- Command: `python execution/update_client.py [slug] --status completed`

### Any → Lost
- Trigger: Client declines or goes silent
- Action: Log reason, add to nurture list
- Reasons: Budget, Timing, Went with competitor, No response, Not a fit

## Follow-Up Automation

### Proposal Follow-Up Sequence
| Day | Action |
|-----|--------|
| 0 | Send proposal |
| 2 | "Any questions?" email |
| 5 | Share relevant case study |
| 7 | Direct ask: "Ready to proceed?" |
| 14 | Final check-in, offer call |
| 21 | Move to nurture or mark lost |

### Stale Lead Revival
- 30 days: "Still interested?" check-in
- 60 days: Value email (tip, resource)
- 90 days: Re-engagement offer

## Metrics to Track

- **Conversion Rates:** Lead → Discovery → Proposal → Close
- **Average Deal Size:** By package type
- **Sales Cycle Length:** Days from lead to close
- **Win Rate:** Closed won / (Closed won + Lost)
- **Pipeline Velocity:** Deals moving per week

## Output

Pipeline data stored in:
- Google Sheet (if configured)
- Individual `clients/[slug]/client.json` files
- Query via `list_clients.py --pipeline`

## Related Directives
- `discovery_call.md` - Move lead to discovery
- `create_proposal.md` - Move to proposal stage
- `send_contract.md` - Move to contract stage
- `onboard_client.md` - Move to active
