# Writing Effective Skill Instructions

This guide covers how to structure and write the body of SKILL.md so the skill is clear, flexible, and maintainable.

## Core Principles

### 1. Explain the Why, Not Just the What

**Poor (rote rules):**
```markdown
## Step 2: Validate Data

ALWAYS validate all inputs using Pydantic. DO NOT skip validation.
Never trust external data sources. Use strict type checking.
```

**Better (explains reasoning):**
```markdown
## Step 2: Validate Data

Before passing data to paid APIs or critical systems, validate inputs with Pydantic. 
Bad data causes two problems: it wastes API credits on requests that will fail, and 
it can cause downstream errors that are expensive to debug. Validation is cheap insurance.
```

Why this works: The model (and future users) understand that validation protects expensive operations, not because you said ALWAYS in caps. They can apply this principle to new domains they'll encounter.

### 2. Avoid Rigid MUST/NEVER in All Caps

These usually signal that you haven't explained the reasoning well enough. Compare:

**Rigid (brittle):**
```
MUST include error messages in JSON format at all times.
NEVER write errors in plain text.
```

**Flexible (principle-based):**
```
Format errors as structured JSON (not plain text) so consuming systems can parse them programmatically. 
This matters when errors are piped to logs or monitoring systems—plain text is hard to search and aggregate.
```

Rigid rules fail when you encounter unexpected scenarios. Principle-based instructions let the model generalize.

### 3. Assume Competence

Write for someone who understands the domain. Don't over-explain basic concepts unless the skill is explicitly beginner-focused.

**Over-explaining:**
```
In Python, a list is like an array. It's a container that holds multiple items. You can add items with .append().
```
(Skip this unless the skill is "Intro to Python")

**Right level:**
```
Flatten nested lists and remove duplicates before passing to the API.
```

### 4. Use Imperative Form

**Passive:**
"It may be helpful to consider validating the input data."

**Imperative:**
"Validate the input data."

Imperative is clearer and more actionable.

## Skill Structure Template

Use this hierarchical structure for SKILL.md:

```markdown
# [Skill Name]

## Overview
1-2 sentences. What does the skill do and why does it matter?

## Core Workflow
Step-by-step procedure (numbered) for the main happy path.

## Decision Tree / Variants
If there are different input types or workflows, explain how to route between them.

## Output Format
Exact structure the skill should produce. Use templates, examples, or detailed descriptions.

## Examples
1-3 complete examples. For each:
- **Input:** What the user provides
- **Process:** Key steps the skill takes
- **Output:** What the skill produces

## Edge Cases & Error Handling
Common failure modes and how to handle them.

## References
Links to bundled files (scripts, templates, etc.). Say when to read them.
```

### Quick Notes on Each Section

#### Overview
1-2 sentences. The reader should understand what problem this skill solves.

**Example:**
"Generate and execute Python data analysis scripts. Handles data loading, exploration, cleaning, visualization, and export to standard formats—all from natural language descriptions of what the user wants."

#### Core Workflow
Numbered steps for the happy path. Be specific about inputs, outputs, and decision points.

**Example:**
```markdown
1. Parse the user's request to identify: data source, analysis type, output format
2. Load data from the specified source (CSV, JSON, database)
3. Perform exploratory analysis (shape, dtypes, null counts, basic stats)
4. Apply transformations based on the user's request
5. Generate visualization (if requested)
6. Save output to the specified format
7. Display a summary of what was done and where the output is saved
```

Don't be so granular that you're micromanaging (e.g., "open terminal," "type python") unless the skill is explicitly about those steps.

#### Decision Trees / Variants
If the skill has multiple workflows or input types, use a clear decision tree.

**Example (for a content skill):**
```markdown
## Routing by Content Type

**If the user wants to write new content:**
→ Follow the New Content workflow (see "Writing New Content" below)

**If the user wants to optimize existing content:**
→ Follow the Optimization workflow (see "Optimizing Existing Content" below)

**If the user wants to repurpose content (e.g., blog post → social posts):**
→ Follow the Repurposing workflow (see "Repurposing Content" below)
```

Then have a subsection for each variant.

#### Output Format
Be explicit about what the skill produces. Use templates if output is structured.

**If it's a file, show its structure:**
```markdown
## Output Format

The skill produces an HTML report with this structure:

```html
<html>
<head>
  <title>Analysis Report</title>
</head>
<body>
  <h1>Executive Summary</h1>
  <p>Key findings in 2-3 sentences</p>
  
  <h1>Findings</h1>
  <ul>
    <li>Finding 1</li>
    ...
  </ul>
  
  <h1>Recommendations</h1>
  <ul>
    <li>Rec 1</li>
    ...
  </ul>
</body>
</html>
```
```

**If it's structured data, show an example:**
```markdown
## Output Format

The skill returns a JSON object:

```json
{
  "status": "success",
  "data": [
    {"id": 1, "label": "...", "value": 100},
    ...
  ],
  "metadata": {
    "rows_processed": 150,
    "columns_extracted": 5,
    "duration_seconds": 2.3
  }
}
```
```

**If it's prose, describe the structure:**
```markdown
## Output Format

The skill produces a 2,000-3,000 word blog post structured as:
- **Title** (50 characters max, target keyword included)
- **Introduction** (150 words, hook + problem statement + what reader will learn)
- **3-5 Main Sections** (400-600 words each, each with clear subheading)
- **Conclusion** (200 words, summary + call-to-action)
```

#### Examples
1-3 complete examples. Show realistic input → output chains.

**Template:**
```markdown
### Example 1: [Descriptive Title]

**Input:**
[User's request as they'd actually phrase it]

**Process:**
[Key steps the skill takes, 1-2 sentences]

**Output:**
[What the skill produces]
```

**Real example (for a report generation skill):**
```markdown
### Example 1: Sales Performance Dashboard

**Input:**
"I have a spreadsheet with monthly sales data (sales.csv) with columns: Date, Rep, Total, Commission. 
Create a dashboard showing total sales by rep and month-over-month trend."

**Process:**
1. Load the CSV; parse dates and convert amounts to numeric
2. Group by rep and month; calculate totals
3. Create bar chart (sales by rep) and line chart (monthly trend)
4. Generate dashboard with both charts + summary table

**Output:**
An interactive HTML dashboard showing:
- Bar chart: Total sales by rep (sorted highest to lowest)
- Line chart: Month-over-month trend with seasonality flagged
- Summary table: Totals by rep with % change from previous month
```

#### Edge Cases & Error Handling
Common failure modes and how to gracefully handle them.

**Format:**
```markdown
### Missing or Invalid Data

**Problem:** User provides a file path that doesn't exist or a CSV with mismatched columns.

**Solution:** 
- Check file existence before attempting load
- If columns don't match expected schema, list what was found vs. expected
- Ask user to verify the file path or provide a corrected file

### Empty Dataset

**Problem:** User uploads a file with headers but no data rows.

**Solution:**
- Detect empty datasets after load
- Return a clear message ("The file has headers but 0 data rows")
- Suggest next steps
```

#### References
Link to bundled files. Say when to read them.

**Example:**
```markdown
## References

- **scripts/generate_report.py** — Automated report generation. Read this if the skill needs to produce detailed formatted reports programmatically.
- **references/seo-strategies.md** — SEO best practices for content. Consult this if the user's request mentions search visibility or keyword targeting.
- **templates/blog-structure.md** — Blog outline templates. Use as reference when structuring long-form content.
```

---

## Writing for Different Audiences

### Technical Users
- Use domain terminology (Pydantic, async, JWT)
- Reference libraries and tools by name
- Assume familiarity with APIs, databases, deployment patterns
- Can abbreviate explanations ("Zod validation" vs. "use Zod, which is a TypeScript library for...")

### Non-Technical Users
- Explain jargon with brief, clear definitions
- Use analogies ("a database is like a spreadsheet, but more powerful")
- Reference general concepts rather than specific tools
- Avoid assuming they know what APIs are

### Mixed Audience (Default)
- Define terms the first time you use them
- Provide tool/library names but don't assume familiarity
- Use analogies when introducing new concepts
- Example: "Validate inputs with Pydantic (a Python library for checking data types and structure)"

---

## Length and Organization

### Sweet Spot
- **Main SKILL.md:** 300-500 lines
- **If approaching 500:** Split into main file + referenced files
- **Key principle:** A single read-through should take 5-10 minutes for the full body

### When to Split into References
If any section exceeds 100 lines and is:
- A complete sub-workflow (new file like `workflow-foo.md`)
- Reference material not needed on every invocation (e.g., detailed API docs)
- Reusable patterns the user might reference separately (e.g., templates)

**Example:**
```
SKILL.md: (400 lines) Main workflow + decision tree + short examples
references/
  ├── detailed-api-spec.md (200 lines)
  ├── templates.md (150 lines)
  └── troubleshooting.md (100 lines)
```

In SKILL.md, link clearly: "For detailed API documentation, see `references/detailed-api-spec.md`."

---

## Progressive Disclosure

Not everything needs to be in SKILL.md upfront. Use this hierarchy:

1. **In frontmatter description** (always loaded) — Trigger phrases, core capability
2. **In SKILL.md overview** (loaded when skill triggered) — What it does, why it matters
3. **In SKILL.md body** (important context) — Core workflow, main decisions
4. **In references/** (on-demand) — Deep dives, templates, troubleshooting

This keeps the main file focused while making detailed info available when needed.

---

## Checklist: Effective Skill Instructions

Before finalizing:

- ✓ Overview is 1-2 sentences and explains the problem the skill solves
- ✓ Core workflow is numbered, specific, and covers happy path only
- ✓ Decision trees clearly route between variants
- ✓ Output format has examples or structure diagrams
- ✓ Examples include realistic input → output chains (not abstract)
- ✓ Edge cases detail problems and solutions (not just warnings)
- ✓ Explanations focus on why, not just what (principles > rules)
- ✓ No MUST/NEVER in all caps; reasoning is explained
- ✓ Language is imperative ("Do X" not "You might consider X")
- ✓ Tech level matches audience (or mixed audience friendly)
- ✓ Under 500 lines (or split with clear references)
- ✓ References are linked clearly with "when to read" notes

