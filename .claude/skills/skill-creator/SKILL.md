---
name: skill-creator
description: Create, test, evaluate, and iteratively improve skills from scratch. Use this skill whenever you need to build a new skill—whether the user has a rough idea of what they want, a specific workflow they want to automate, or an existing pattern they want to encode. Also use when improving an existing skill based on test results. This skill guides you through intent capture, drafting, systematic testing with benchmarking, quantitative and qualitative evaluation via an interactive viewer, and iteration loops until the skill meets quality standards. If a user mentions "create a skill", "build a skill", "I want a skill that does X", or "my workflow should be a skill", jump straight into skill creator mode.
compatibility: Requires Claude Code or Cowork environment with filesystem access and subagent capability for parallel test execution. Claude.ai users can use a serial workflow (no baselines, no parallel runs). No external API dependencies.
---

# Skill Creator

## Overview

The Skill Creator guides you through building production-quality reusable skills. The process has five main phases:

1. **Capture Intent** — Understand exactly what the skill should do, when it should trigger, and what success looks like
2. **Draft & Design** — Write the SKILL.md with clear instructions, examples, and required outputs
3. **Test & Evaluate** — Create realistic test prompts, run them, and assess quality via quantitative metrics and human review
4. **Iterate** — Refine based on feedback, maintain test suite in new iteration directories
5. **Optimize & Package** — Fine-tune the skill description for better triggering, then prepare for release

You don't always follow these phases linearly. Meet the user where they are—they might arrive with a fully drafted skill and only need evaluation/iteration, or they might have a vague idea and need heavy guidance on intent capture. Be flexible, but always follow this loop once you start testing: **Draft → Test → Review → Improve → Retest** until the user is satisfied.

---

## Phase 1: Capture Intent

Your job here is to deeply understand what the skill should do and when to use it.

### Key Questions to Answer

Start with these—don't skip over them even if they seem obvious:

- **What should this skill enable Claude to do?** (the core capability)
- **When should this skill trigger?** (what user phrases, contexts, workflows?)
- **What's the output format?** (files, structured data, prose?)
- **Are there objective success criteria?** Or is quality subjective?
- **What are the edge cases?** (Common failure modes, ambiguous inputs, dependencies)

### Information Gathering

If the user describes an existing workflow, extract:
- Tools they currently use (APIs, scripts, services)
- Step-by-step sequence
- Input/output formats at each step
- Corrections or workarounds they've discovered
- Pain points where automation would help most

Check if they need test cases:
- **Objectively verifiable outputs** (file transforms, data extraction, code generation, deterministic workflows) → **Yes, use test cases**
- **Subjective outputs** (writing style, design quality, creative choices) → **Usually no; rely on qualitative feedback**

### Sign-Off

Before moving to drafting, confirm:
- _You_ understand the scope clearly
- The user agrees with your understanding
- You've identified 3-5 realistic test prompts that cover the happy case + edge cases

---

## Phase 2: Draft & Design

Write the SKILL.md with these components:

### Frontmatter

```yaml
---
name: [skill-identifier, lowercase-with-hyphens]
description: [Detailed description of what skill does and WHEN to use it. Be "pushy"—include specific trigger phrases like "when the user mentions X, Y, or Z". Include both capability and context for when to invoke.]
compatibility: [Optional. Required tools or dependencies.]
---
```

**Key point on description:** Skills are underused if descriptions are too passive. Instead of "A helper for running tests," write "Use this skill ANY TIME the user mentions tests, testing, QA, validation, pytest, or wants to verify code works. Use it even if they don't explicitly ask for 'testing.'"

### Body Structure

1. **Overview** — 1-2 sentences explaining what the skill does and why it matters
2. **Core Workflow** — Step-by-step procedure, numbered
3. **Decision Trees** (if applicable) — Branch logic for different input types
4. **Output Format** — Exact structure the skill should produce (templates, examples)
5. **Examples** — 1-3 realistic examples with input → output
6. **Edge Cases** — Common pitfalls and how to handle them
7. **References** — Links to bundled files (scripts, templates, docs) if any

### Writing Principles

- **Imperative form** — "Do X," not "You might consider X"
- **Explain the why** — Don't just say "Always validate inputs." Say "Validating inputs prevents bad data from reaching paid APIs and external systems, which saves time and prevents costly errors."
- **Use theory of mind** — Assume the model (and future users) are smart and can go beyond rote rules if you explain the reasoning
- **Keep it lean** — Remove instructions that aren't pulling their weight
- **No MUST in all caps** — Use narrative explanation instead of rigid rules
- **Stay under 500 lines** — If you're exceeding this, split into domains and reference files clearly

### Example Frontmatter (Bad → Good)

**Bad:**
```yaml
description: Creates a blog post for a client website.
```

**Good:**
```yaml
description: Write SEO-optimized blog posts for your client. Use this skill whenever the user mentions writing a blog post, article, newsletter content, or long-form content for their website. Also use if they mention improving blog strategy, targeting keywords, or competing on search. Include this skill even if they don't explicitly ask for "a blog post"—watch for phrases like "what should I write about" or "we need content on X topic."
```

---

## Phase 3: Test & Evaluate

This is where the skill proves itself. You'll create realistic test prompts, run them, and measure quality.

### Step 1: Create Test Prompts

Generate 2-3 realistic test cases—the kind of task a real user would ask for. Format them as:

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "Realistic user task as they'd actually phrase it",
      "expected_output": "What success looks like (narrative, not a rigid template)",
      "files": []
    }
  ]
}
```

Save this as `evals/evals.json` in your workspace. Don't write assertions yet—just the prompts and expected_output descriptions.

### Step 2: Run All Test Cases in Parallel

For each test case, spawn **two** subagent tasks in the same function call:

**With Skill:**
- Skill path: `[path-to-skill]`
- Task: `[eval prompt]`
- Save outputs to: `[workspace]/iteration-1/eval-[ID]/with_skill/outputs/`

**Baseline** (depends on context):
- Creating a new skill: no skill at all (same prompt, no skill path)
- Improving: the previous version (snapshot it first)
- Save to: `[workspace]/iteration-1/eval-[ID]/without_skill/outputs/` or `old_skill/outputs/`

Critical: Spawn all runs together, don't batch them sequentially.

### Step 3: Draft Assertions While Runs Complete

While subagents work, draft quantitative assertions for each test case. These should be:
- **Objectively verifiable** — can be scored as pass/fail
- **Descriptively named** — read clearly in the benchmark viewer
- **Not forced** — skip for subjective skills; use qualitative feedback instead

Examples of good assertions:
- `output_file_exists` — "The skill produces a file with the expected name"
- `markdown_structure_complete` — "Markdown has headers, body, and conclusion sections"
- `code_syntax_valid` — "Generated Python code has no syntax errors"
- `all_required_fields` — "JSON output contains name, email, and phone fields"

Save these to `eval_metadata.json` in each eval directory:

```json
{
  "eval_id": 0,
  "eval_name": "descriptive-name-for-this-test",
  "prompt": "The user's task prompt",
  "assertions": [
    {
      "name": "output_file_exists",
      "description": "The skill produces a file with the expected name and format"
    }
  ]
}
```

### Step 4: Capture Timing Data

When each subagent task completes, it returns `total_tokens` and `duration_ms`. Save immediately to `timing.json` in the run directory:

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3
}
```

This data only comes through task notifications and is lost otherwise.

### Step 5: Generate the Evaluation Viewer

Once all runs complete:

1. **Grade each run** — Use agents/grader.md to evaluate assertions. Save results to `grading.json` with exact field names: `text`, `passed`, `evidence` (not name/met/details).

2. **Aggregate benchmark** — Run the aggregation script:
   ```bash
   python -m scripts.aggregate_benchmark <workspace>/iteration-1 --skill-name my-skill
   ```
   This produces `benchmark.json` and `benchmark.md` with pass rates, timing, and token usage for each configuration.

3. **Launch the reviewer** — Show results to the user:
   ```bash
   python eval-viewer/generate_review.py <workspace>/iteration-1 \
     --skill-name "my-skill" \
     --benchmark <workspace>/iteration-1/benchmark.json
   ```
   For iteration 2+, add: `--previous-workspace <workspace>/iteration-1`

   **In Claude Code:** This opens a browser with interactive results.
   
   **In Cowork:** Use `--static <output_path>` to generate standalone HTML instead of starting a server.

The viewer has two tabs:
- **Outputs** — Click through each test case, see the prompt and what the skill produced
- **Benchmark** — Quantitative stats: pass rates, timing, token usage, analyst observations

Tell the user: _"I've generated the results. The 'Outputs' tab shows what the skill produced for each test case. The 'Benchmark' tab shows the quantitative comparison. Review them both, then come back with feedback."_

---

## Phase 4: Iterate

Once the user reviews the results and tells you what to improve:

### Read the Feedback

When the user submits reviews, parse `feedback.json`:

```json
{
  "reviews": [
    {"run_id": "eval-0-with_skill", "feedback": "the chart is missing axis labels", "timestamp": "..."},
    {"run_id": "eval-1-with_skill", "feedback": "", "timestamp": "..."}
  ],
  "status": "complete"
}
```

Empty feedback = they thought it was fine. Focus improvements on evals with specific feedback.

### Improve the Skill

When revising, think about:

- **Generalization** — The feedback is from a few examples, but the skill will be used a million times across different prompts. Don't overfit to edge cases. Instead, find underlying patterns and use better metaphors or instructions.
  
- **Keep it lean** — Read the transcripts from test runs. If subagents wasted time on unproductive steps, remove the skill instructions causing that.
  
- **Explain the why** — Avoid MUST and NEVER in all caps. Instead, explain reasoning so the model understands the deeper principles.

- **Look for repeated work** — If all 3 test case subagents independently wrote a helper script (e.g., `create_docx.py`), that's a signal to bundle it in `scripts/` so future invocations don't reinvent.

### Rerun in New Iteration

After improving:

1. Apply your changes to SKILL.md
2. Rerun all test cases into `iteration-2/` with new, clean baseline runs
3. Launch the viewer with `--previous-workspace iteration-1` so user can compare
4. Repeat until feedback is empty or user says they're satisfied

---

## Phase 5: Optimize & Package

Once the skill is solid:

### Description Optimization (Optional but Recommended)

The description field is the primary mechanism for skill triggering. You can optimize it for better accuracy:

1. **Generate 20 trigger eval queries** — Mix of should-trigger and should-not-trigger, kept realistic:
   ```json
   [
     {"query": "ok so my boss sent me this big CSV file...", "should_trigger": true},
     {"query": "i need to write a fibonacci function", "should_trigger": false}
   ]
   ```
   For should-not-trigger, focus on near-misses—queries that share keywords but need something different.

2. **Review with user** — Use the template at `assets/eval_review.html` to let them refine queries

3. **Run optimization loop** (Claude Code / Cowork only):
   ```bash
   python -m scripts.run_loop \
     --eval-set <path-to-trigger-eval.json> \
     --skill-path <path-to-skill> \
     --model <current-model> \
     --max-iterations 5 \
     --verbose
   ```
   This iterates on the description, testing triggering accuracy and returning `best_description` selected by held-out test performance.

4. **Apply result** — Update SKILL.md frontmatter with the optimized description

### Package the Skill

Once you and the user agree the skill is done:

```bash
python -m scripts.package_skill <path/to/skill-folder>
```

This bundles everything into a `.skill` file ready for distribution.

---

## Communication Patterns

Adjust your technical language based on user familiarity:

- **If they use terms like "evaluation," "benchmark,"** — they're technical; you can use formal language
- **If they ask "what's JSON?" or avoid jargon** — explain briefly: "JSON is a standard text format for storing structured data, like a table but more flexible"
- **When in doubt, show, don't tell** — "This is an assertion—basically a test that checks if the output has X property" (with example) is clearer than abstract definitions

Frame async work clearly: _"I'll run all the tests in parallel and check back periodically to report what I find."_

---

## Edge Cases

### Working in Claude.ai (No Subagents)

Claude.ai doesn't have subagents, so adapt like this:

- **Run test cases serially** — You read the skill's SKILL.md, then you follow its instructions to accomplish each test prompt yourself. Do them one at a time.
- **Skip baseline runs** — Just use the skill to complete the task. Human review compensates for lack of A/B comparison.
- **No browser viewer** — Present results directly in conversation: show prompt, show output, ask for feedback inline
- **No benchmarking** — Skip quantitative stats (they're less meaningful without baselines). Focus on qualitative feedback.
- **No description optimization** — Requires `claude` CLI tool, which is Claude Code only

### Updating an Existing Skill

If the user asks you to improve a skill they already have:

- **Preserve the original name** — Use the existing skill identifier, don't create "skill-v2"
- **Copy to writeable location** — The installed skill may be read-only. Copy to `/tmp/skill-name/`, edit there, package from the copy
- **Snapshot for baseline** — Before editing, copy the original skill to `<workspace>/skill-snapshot/` so baseline runs compare against the old version
- **Initialize evals.json** — If it doesn't exist, create it with test cases to drive iteration

---

## Checklist for a Finished Skill

Before packaging, confirm:

- ✓ SKILL.md has clear frontmatter (name, description, compatibility)
- ✓ Description is "pushy"—includes multiple trigger phrases and contexts
- ✓ Body has overview, workflow, output format, examples, edge cases
- ✓ Written in imperative form with explanation of reasoning (no rote rules)
- ✓ Under 500 lines (or properly split into references)
- ✓ Tested with realistic prompts covering happy case + edge cases
- ✓ Quantitative + qualitative evaluation completed
- ✓ Iterated (at least once) based on feedback
- ✓ Benchmark shows meaningful improvement (or unchanged if already good)
- ✓ User is satisfied with quality

---

## References

- **agents/grader.md** — How to evaluate assertions against outputs
- **agents/analyzer.md** — How to analyze why one version beat another
- **agents/comparator.md** — Blind comparison for rigorous A/B testing (advanced)
- **references/schemas.md** — JSON structures for evals.json, grading.json, benchmark.json
- **eval-viewer/generate_review.py** — The script to generate interactive results viewer

