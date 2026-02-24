# Directive: Email Sequence Builder
# 5 Cypress Automation

---

## Purpose
Build and deliver client-ready B2B email sequences — nurture campaigns, re-engagement series, drip flows, onboarding emails, and cold outreach sequences. Sequences are personalized, strategically structured, and timed for the client's sales cycle.

**Pricing:** Included in Marketing Services retainer or $500–$1,500 per standalone sequence.

---

## When to Use This Directive
- Client needs an email nurture sequence for a new lead segment
- Launching a new product or service and need an announcement + follow-up email set
- Re-engaging a cold or inactive list
- Building onboarding emails for new customers
- Client has a sales sequence that needs a professional copywriting overhaul

---

## Inputs Required

Collect before starting:
- [ ] Client name and industry
- [ ] Target audience for this sequence (cold leads / warm prospects / existing customers)
- [ ] Sequence goal (book a demo, download resource, reply, attend webinar, convert to paid)
- [ ] Number of emails and cadence (e.g., "5 emails, Day 0 / 3 / 7 / 14 / 21")
- [ ] Primary offer or CTA
- [ ] Key messaging or proof points to include
- [ ] Any specific dates, offers, or constraints
- [ ] Client context file loaded from `clients/[client-name]/`

---

## Process

### Step 1 — Brief Alignment
Confirm sequence parameters with user:
- Campaign type (nurture / re-engagement / announcement / onboarding)
- Audience segment
- Sequence length and cadence
- Primary goal and CTA

### Step 2 — Sequence Architecture
Map all emails before writing. Produce a table:

| Email | Send Day | Subject Theme | Goal | CTA |
|-------|----------|---------------|------|-----|

Standard frameworks:
- **Nurture (5–7 emails):** Problem awareness → Education → Social proof → Soft ask → Objection handling → Direct ask
- **Re-engagement (3 emails):** Value reminder → New insight → Final check-in
- **Announcement (1–2 emails):** News + why it matters → Follow-up with proof

Present architecture to user before writing. Adjust if needed.

### Step 3 — Write All Emails

For each email:
```
EMAIL [#] OF [TOTAL]
Subject Line: [subject] (provide 3 options: curiosity / specificity / direct)
Preview Text: [40–90 characters]
Send Day: Day [X]
Goal: [what this email accomplishes]

[EMAIL BODY]
```

B2B Email Principles (always apply):
- One email, one goal. One CTA. No confusion.
- Lead with value before the ask.
- Short subject lines (4–7 words).
- Early emails educate. Later emails invite action.
- Plain text tone — writing for a person, not a newsletter.
- Clear, single CTA.

### Step 4 — Campaign Notes
Append to the end of the document:
- Recommended send timing and days of week
- A/B test suggestions (subject line or CTA variants)
- Segmentation recommendations (opened vs. not opened branches)
- Follow-up logic notes

### Step 5 — Save Output
Save to: `marketing-team/output/[client-name]/email-campaign-[campaign-name]-[YYYY-MM].md`

---

## Integration Points
- Use **email_sequence_builder.py** in `execution/` to scaffold email metadata templates
- Sequences can be imported into client's email platform (Mailchimp, HubSpot, Klaviyo, etc.)
- Coordinate with `directives/deliver_monthly_insights.md` for performance tracking

---

## Quality Standards
- Every email has a single, clear purpose
- No email over 250 words (unless explicitly "long-form educational")
- Subject lines tested against curiosity, specificity, and directness dimensions
- Document is deliverable as-is to the client
