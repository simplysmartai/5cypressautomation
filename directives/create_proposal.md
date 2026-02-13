# Create Proposal Directive

> Generate professional proposals from discovery information.

## Purpose

Transform discovery notes into a polished, professional proposal document that clearly communicates value, scope, and pricing.

## Inputs Required

Before creating a proposal, ensure you have:
- [ ] Client name and contact info
- [ ] Pain points identified
- [ ] Proposed solution approach
- [ ] Recommended package or custom scope
- [ ] Timeline estimate
- [ ] Any special requirements

## Proposal Structure

### 1. Executive Summary
- Acknowledge their pain points (show you listened)
- State the solution in one sentence
- Highlight the key benefit/outcome

### 2. Understanding Your Needs
- Recap what they told you (validates understanding)
- Quantify the problem when possible
- Show the cost of inaction

### 3. Proposed Solution
- High-level approach
- Specific workflows/automations included
- Systems that will be integrated
- What they DON'T need to worry about

### 4. Deliverables
- Clear list of what they receive
- Documentation included
- Training provided
- Support period

### 5. Timeline
- Phase breakdown with milestones
- Key dates/deadlines
- What you need from them (and when)

### 6. Investment
- Package or custom pricing
- What's included at this price
- Payment terms (50% deposit, 50% on completion)
- Optional add-ons if relevant

### 7. Why 5 Cypress Labs
- Resilient systems narrative
- Scaling capability
- Technical excellence and reliability

### 8. Next Steps
- Start Your Audit CTA
- How to proceed
- Expiration date (creates urgency)

## Execution

### Generate Proposal

```bash
python execution/create_proposal.py \
  --client "client-slug" \
  --package "growth" \
  --custom-price 8500 \
  --output "google-doc"
```

**Parameters:**
- `--client`: Client slug (must exist in clients/ folder)
- `--package`: starter, growth, scale, or custom
- `--custom-price`: Override package price (optional)
- `--discount`: Percentage discount (optional)
- `--output`: google-doc, pdf, or markdown
- `--rush`: Add rush delivery premium

### Script Actions

1. Reads `clients/[slug]/discovery.md` for context
2. Loads pricing from `config/pricing.json`
3. Generates proposal document
4. Saves to `clients/[slug]/proposals/proposal-[date].md`
5. If google-doc: Creates in Google Drive, shares link
6. Logs activity

## Proposal Templates

### For Starter Package
Focus on:
- Single workflow clarity
- Quick win messaging
- Low-risk entry point

### For Growth Package
Focus on:
- Interconnected value
- Scaling benefits
- ROI over 90 days

### For Scale Package
Focus on:
- Transformation narrative
- Strategic partnership
- Long-term roadmap

## Pricing Guidelines

From `config/pricing.json`:
- Load base package prices
- Apply any custom adjustments
- Calculate deposit amount
- Include payment terms

**Discounting Rules:**
- Max 15% discount without approval
- Document reason for any discount
- Never discount more than 25%

## Follow-Up Sequence

After sending proposal:
- Day 0: Send proposal + brief email
- Day 2: "Any questions?" check-in
- Day 5: Value reinforcement (case study, testimonial)
- Day 7: Direct ask - ready to proceed?
- Day 14: Final follow-up, offer call

## Output

Proposal saved to:
```
clients/[slug]/proposals/
├── proposal-2026-01-21.md      # Source
├── proposal-2026-01-21.pdf     # If PDF requested
└── proposal-2026-01-21.gdoc    # Google Doc link file
```

## Related Directives
- `discovery_call.md` - Gather requirements first
- `send_contract.md` - After proposal accepted
- `manage_pipeline.md` - Track proposal status
