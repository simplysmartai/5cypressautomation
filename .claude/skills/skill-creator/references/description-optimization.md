# Skill Description Optimization Guide

This guide explains how to write skill descriptions that trigger reliably without over-triggering.

## What Skill Descriptions Do

In Claude's skill system, the name and description appear in the `available_skills` list. Claude reads these and decides whether a skill is relevant to the user's prompt. A well-written description:

- Clearly states what the skill does (capability)
- Lists specific contexts and trigger phrases (when to use)
- Includes edge cases and variant phrasings
- Reaches toward the user's intent even when they don't explicitly name the skill

## The Pushing Principle

Skills are underused if descriptions are too passive or narrow. Compare:

**Passive (underutilized):**
> "Helps with data analysis and reporting."

**Pushy (properly triggered):**
> "Create marketing dashboards and reports from any data source. Use this skill ANY TIME the user mentions analytics, metrics, reporting, KPIs, dashboards, campaign performance, ROI, conversions, or data visualization. Also use when they provide raw numbers and want insights extracted. Use even if they don't explicitly ask for a 'dashboard'—watch for phrases like 'show me what happened' or 'analyze this data.'"

The second description is aggressively inclusive because:
1. It names multiple trigger phrases
2. It explicitly tells Claude to use it for variants (dashboard, analysis, insights)
3. It identifies anti-patterns ("don't wait for them to say X explicitly")

## Structure

A good description combines three elements:

### 1. Capability Statement (1-2 sentences)
What the skill fundamentally enables.

Example: "Analyze data and create client-ready performance reports."

### 2. Primary Trigger Phrases (bulleted or inline)
Specific words/phrases that indicate the skill is needed.

Example: "Use when the user mentions reporting, dashboard, metrics, KPIs, performance analysis, campaign results, or ROI."

### 3. Pattern Recognition (anti-pattern + inclusion rules)
Help Claude identify intent even when the user doesn't use the exact terms.

Example: "Also use when the user provides raw numbers/data and wants insights extracted. Use even if they don't explicitly ask for a 'dashboard'—watch for vague phrases like 'show me what happened' or 'make sense of this data.'"

## Examples by Domain

### Business Intelligence Skill

```
Analyze business metrics and create executive dashboards. Use this skill whenever the user 
mentions KPIs, metrics, performance tracking, ROI, conversion rates, pipeline analysis, 
or data visualization. Also use when they provide raw numbers and want insights. Even if 
they say things like "I have this data and want to understand it" or "make me a report," 
this is a good fit. Don't restrict to just "create a dashboard"—this skill also helps with 
ad-hoc analysis, trend spotting, and explaining what the data means.
```

### Code Review Skill

```
Systematically review code for bugs, performance, security, and maintainability. Use when 
the user asks for code review, mentions a pull request, wants feedback on code, or has 
concerns about performance or security. Also use if they ask "is this code good?" or "does 
this look right?" even if they don't explicitly say "review." Consider using this skill for 
refactoring guidance, legacy code cleanup, and best practices advice—these often benefit 
from structured review patterns.
```

### SEO Content Skill

```
Write and optimize long-form content (blog posts, guides, landing pages) for search rankings 
and conversions. Use whenever the user mentions blog posts, articles, landing pages, content 
marketing, SEO, keyword targeting, or organic traffic. Also use if they ask "what should we 
write about?" or "how do we rank for X?" even if they don't ask for prose directly. This skill 
is appropriate for strategy (what to write), content (the prose itself), and optimization 
(improving existing content).
```

## Anti-Patterns

**Too narrow:**
> "Write a blog post with 2,000 words that targets a specific keyword."
- Over-specifies the output format
- Misses variants (300-word article, update existing post, competitor comparison)
- Doesn't help with strategy

**Too vague:**
> "Content for marketing purposes."
- Could apply to email, ads, landing pages, social media (which need different approaches)
- Doesn't guide Claude on when to reach for this skill vs. a more general writing skill
- No user phrases to match against

**Just right:**
> "Write SEO-optimized content for search visibility. Use whenever the user mentions blog, article, landing page, keyword ranking, organic traffic, or content marketing. Also use if they ask 'what should we write about' even if they haven't decided on format yet. This skill helps with strategy, first draft, and optimization of existing content for search."

## Testing Your Description

Ask yourself:

1. **Coverage** — If I use this skill, will it catch most of the legitimate cases where it's useful?
2. **False positives** — Will it over-trigger on things it's not good at? (If yes, add a "don't use" clause)
3. **Variant phrasings** — Does it account for how real users actually phrase requests?
4. **Anti-patterns** — Does it help Claude identify intent when the user doesn't name the skill explicitly?

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Only lists one trigger phrase | Add 5-8 phrases; include variants and anti-patterns |
| Assumes user will be explicit | Add clause: "even if they don't explicitly ask for X" |
| No examples of intent patterns | Show what user phrasing looks like ("watch for...") |
| Includes out-of-scope domains | Split into separate skills or clearly delineate boundaries |
| Too long (>150 words) | Condense; prioritize high-value trigger phrases |
| Passive voice ("can be used for...") | Rewrite as imperative: "Use when..." |

---

## The Full Loop

Descriptions are optimized via the description-optimizer script in the skill creator. The loop:

1. Generate 20 trigger eval queries (mix of should-trigger and should-not-trigger)
2. Test the current description (each query evaluated 3 times for reliability)
3. Claude proposes improvements based on what failed in step 2
4. Evaluate the new description; iterate up to 5 times
5. Select best version by held-out test performance (not training performance, to avoid overfitting)

You can run this manually once the skill core is solid:

```bash
python -m scripts.run_loop \
  --eval-set <trigger-evals.json> \
  --skill-path <path-to-skill> \
  --model <current-model> \
  --max-iterations 5
```

