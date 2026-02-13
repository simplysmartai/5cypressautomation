---
name: customer-sales
description: Automate cold outreach, follow-ups, and lead nurturing for SMB client acquisition. Use when generating sales emails, proposals, or follow-up sequences.
---

# Customer Sales Automation

Automate your sales outreach to land more SMB clients without manual effort.

## When to Use This Skill

- Writing cold emails to potential SMB clients
- Creating follow-up sequences (3-5 touchpoints)
- Drafting proposals and quotes
- Building case studies from completed projects
- Handling common objections

## Cold Email Framework

### Structure (Keep Under 150 Words)
```
Subject: [Specific pain point] for [Company Name]

Hi [First Name],

[1 sentence showing you researched them]

[1-2 sentences about their specific problem]

[1 sentence about how you solve it - with proof]

[Clear CTA - calendar link or reply request]

[Your name]
```

### Example: QuickBooks Automation Pitch
```
Subject: Manual invoicing eating 5+ hours/week at [Company]?

Hi Sarah,

I noticed your Etsy shop is growing fast - congrats on the 500+ reviews!

Most shops your size spend 5-10 hours weekly on manual invoicing
and inventory updates. That's time you could spend on product design.

We automate the sales→QuickBooks→shipping flow for ecommerce sellers.
One client cut their admin time from 8 hours to 30 minutes weekly.

Worth a 15-min call to see if this fits? [Calendar Link]

Best,
[Your name]
Simply Smart Automation
```

## Follow-Up Sequence

| Day | Email Focus | Subject Line |
|-----|-------------|--------------|
| 0 | Initial outreach | [Pain point] for [Company] |
| 3 | Quick bump | Re: [Original subject] |
| 7 | Add value | Quick tip for [their situation] |
| 14 | Social proof | How [similar company] saved X hours |
| 21 | Break-up | Closing the loop |

### Day 3: Quick Bump
```
Subject: Re: Manual invoicing eating 5+ hours/week at [Company]?

Hi Sarah,

Just floating this back up - I know things get busy.

Would a quick 15-minute call be worth exploring? Happy to show
you exactly how the automation works for shops like yours.

[Calendar Link]
```

### Day 7: Value Add
```
Subject: Quick tip for Etsy sellers with inventory headaches

Hi Sarah,

Whether we chat or not, thought you'd find this useful:

Most Etsy sellers don't realize QuickBooks can auto-flag
low inventory items. Takes 5 minutes to set up.

Here's how: [Brief tip or link]

Let me know if you'd like help setting up the full automation.

[Calendar Link]
```

### Day 21: Break-Up
```
Subject: Closing the loop

Hi Sarah,

I've reached out a few times about automating your invoicing
workflow but haven't heard back.

Totally understand if the timing isn't right or it's not a priority.

I'll close this out, but feel free to reach out anytime
if automation makes sense down the road.

Cheers,
[Your name]
```

## Proposal Template

```markdown
# Automation Proposal for [Client Name]

## The Problem
[1-2 sentences about their specific pain - use their words from discovery]

## The Solution
We'll automate your [specific workflow]:
- Sales form → QuickBooks invoice (automatic)
- Inventory sync (real-time)
- Shipping labels (one-click)

## What You Get
- [ ] Custom automation workflow
- [ ] Admin dashboard
- [ ] Deploy guide + training
- [ ] 30-day support

## Investment
**One-time setup**: $X,XXX
**Monthly maintenance** (optional): $XXX/month

## Timeline
- Week 1: Discovery + build
- Week 2: Testing + deploy
- Week 3: Training + handoff

## Next Steps
1. Reply to confirm scope
2. 50% deposit to start
3. Kickoff call [suggest date]

---
Questions? Reply to this email or book a call: [Calendar Link]
```

## Objection Handling

| Objection | Response |
|-----------|----------|
| "Too expensive" | "What's the cost of 5 hours/week for the next year? That's 260 hours - at $50/hr that's $13K in time. This pays for itself in 2 months." |
| "We're too small" | "Actually, small teams benefit most - you don't have an ops person to handle this manually. Automation IS your ops team." |
| "We tried automation before" | "What broke? Usually it's bad implementation, not bad automation. We build with your specific workflow in mind." |
| "Let me think about it" | "Totally fair. What questions would help you decide? Happy to send more details or hop on a quick call." |

## Personalization Variables

Use these in your emails:
- `{company_name}` - Their business name
- `{first_name}` - Contact's first name
- `{pain_point}` - Specific problem (research this!)
- `{social_proof}` - Relevant case study
- `{calendar_link}` - Your scheduling link

## Metrics to Track

- **Open rate**: Target 40%+ (improve subject lines if lower)
- **Reply rate**: Target 10%+ (improve body if lower)
- **Meeting booked rate**: Target 3-5% of sent
- **Close rate**: Target 25%+ of meetings

## Integration with Your Workflow

1. Research prospect (5 min)
2. Draft email using templates above
3. Use `execution/send_email.py` for delivery
4. Log activity with `execution/log_activity.py`
5. Track in your CRM or spreadsheet
