# SOP: Email Campaign Creation
# 5 Cypress Automation — Standard Operating Procedure

---

## Purpose
This SOP defines the process for producing client-ready email campaigns. 5 Cypress clients use email to nurture leads, re-engage prospects, and communicate with existing customers. Email for B2B is not about volume — it's about relevance, timing, and trust.

---

## When to Use This SOP
- Building a new nurture sequence (3-7 emails)
- One-off campaign email (announcement, event, launch)
- Re-engagement campaign for cold leads
- Onboarding sequence for new customers

---

## Inputs Required Before Starting
- [ ] Client context file loaded
- [ ] Campaign goal clearly defined (nurture? announce? re-engage?)
- [ ] Target audience segment identified
- [ ] Number of emails in sequence confirmed
- [ ] Any specific offers, CTAs, or dates to hit

---

## Output Format
Deliver a single Markdown document saved to:
`marketing-teammarketing-team/output/[client-name]/email-campaign-[campaign-name]-[YYYY-MM].md`

Each email in the document should be clearly separated with a header.

---

## B2B Email Principles (Always Apply)
1. **One email, one job.** Each email has a single purpose and a single CTA.
2. **Lead with value, not the ask.** Give the reader something useful before asking for anything.
3. **Short subject lines win.** 4-7 words. Curiosity or specificity beat cleverness.
4. **Respect the sales cycle.** Early emails educate. Later emails invite action.
5. **Sound like a person, not a newsletter.** Plain text often outperforms designed HTML for B2B.
6. **Always have a clear, single CTA.** One link. One action. No confusion.

---

## Process: Step by Step

### Phase 1 — Campaign Brief (5 min)
Define before writing:
- **Campaign Goal:** What outcome do we want? (Book a demo, download resource, reply to email, attend webinar)
- **Audience Segment:** Who is receiving this? (Cold leads, warm prospects, existing customers, lapsed clients)
- **Sequence Length:** How many emails?
- **Cadence:** How many days between each email?
- **Key Message:** What is the single most important thing to communicate?
- **Offer / CTA:** What specific action are we driving toward?

### Phase 2 — Sequence Architecture
Map out the sequence before writing any email:

| Email # | Day | Subject Theme | Primary Goal | CTA |
|---------|-----|---------------|--------------|-----|
| 1 | Day 0 | | | |
| 2 | Day 3 | | | |
| 3 | Day 7 | | | |
| ... | | | | |

**Standard Sequence Frameworks by Type:**

**Nurture Sequence (5-7 emails)**
1. Welcome / context-setting
2. Problem awareness (their pain point)
3. Education / insight (your POV)
4. Social proof / case study
5. Soft CTA (low-friction ask)
6. Objection handling
7. Direct ask (demo, call, proposal)

**Re-engagement Sequence (3 emails)**
1. "We noticed you've been quiet" — value reminder
2. New insight or resource — give before you ask
3. Final check-in — permission to close or reopen

**Announcement / Launch (1-2 emails)**
1. The news + why it matters to them
2. (Optional) Follow-up with social proof or FAQ

### Phase 3 — Write Each Email

For each email, produce:

```
---
EMAIL [#] OF [TOTAL]
Subject Line: [subject]
Preview Text: [40-90 characters shown in inbox]
Send Day: Day [X]
Goal: [what this email accomplishes]
---

[EMAIL BODY]

[SIGNATURE]
[CTA BUTTON TEXT / LINK PLACEHOLDER]
```

**Email Body Structure:**
- **Opening line:** Hook. Not "I hope this email finds you well." Start with the point.
- **Body (2-4 short paragraphs):** Build the case. One idea per paragraph. Short sentences.
- **CTA:** Clear, specific, low-friction. Tell them exactly what happens when they click.
- **Signature:** Keep it simple. Name, title, company, website.

### Phase 4 — Subject Line Variations
For each email, provide 3 subject line options:
- Option A: Curiosity-driven
- Option B: Specificity/benefit-driven
- Option C: Direct/plain

### Phase 5 — Campaign Notes
At the end of the document include:
- Recommended sending times (day of week, time of day for B2B)
- Segmentation notes (any emails that should be adjusted per audience)
- A/B test recommendations
- Follow-up actions if someone clicks vs. doesn't open

---

## Output Document Structure

```
# Email Campaign: [Campaign Name]
# Client: [Client Name] | Prepared by 5 Cypress Automation | [Date]

## Campaign Brief
- Goal:
- Audience:
- Sequence Length:
- Cadence:
- CTA:

## Sequence Architecture
[Table]

## Emails

### Email 1: [Subject Theme]
[Full email]

### Email 2: [Subject Theme]
[Full email]

...

## Campaign Notes & Recommendations
```

---

## Quality Checklist
- [ ] Every email has one clear CTA only
- [ ] Subject lines are under 7 words (at least one option)
- [ ] No filler openers ("Hope this finds you well", "Just checking in")
- [ ] Tone matches client voice from context file
- [ ] Sequence tells a logical story from email 1 to last
- [ ] Saved to correct output folder
