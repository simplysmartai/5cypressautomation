# Evaluating Skills: Test Cases and Assertions

This guide covers how to design test prompts and assertions that measure skill quality effectively.

## Test Case Design

A good test case (eval) is:
- **Realistic** — What a real user would actually ask
- **Specific** — Contains concrete details (file names, values, URLs, context)
- **Substantive** — Complex enough that Claude benefits from the skill (simple queries may not trigger)
- **Independent** — Each test case covers a different aspect or workflow

### Structure

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "The exact user task, as they would phrase it",
      "expected_output": "What success looks like (narrative description, not a rigid spec)",
      "files": []
    }
  ]
}
```

### Example: Good vs. Poor

**Poor test case:**
- Prompt: "Format this data"
- Expected output: "Data formatted correctly"
- Problem: Too vague, no concrete details, won't trigger the skill

**Good test case:**
- Prompt: "My boss sent me a CSV from our Q4 sales tool (it's called 'q4_sales_final.csv'). The revenue is in column C and costs in column D. I need to add a column that shows profit margin as a percentage. Can you help me build that? Also show me the top 5 rows to spot-check."
- Expected output: "A Python script that reads the CSV, calculates profit margin, adds it as a new column, displays top 5 rows for verification, and saves the result to a new file"
- Why it's good: Specific file name, concrete columns, real-world context, includes edge case (verification step), enough detail that the skill is clearly useful

## How Many Test Cases?

- **Minimum: 2-3** for initial testing (captures happy case + 1-2 variants)
- **Expansion pass: 5-8** after iteration 1, to increase confidence
- **Comprehensive: 10-15** for release-quality skills

Start small and expand after the first iteration when you've gotten feedback on core functionality.

## Test Case Categories

### Happy Path
The normal, expected case where the skill should work smoothly.

Example: "Write a blog post about cloud migration for a technical audience targeting the keyword 'serverless architecture.'"

### Edge Case
Boundary conditions, unusual inputs, or tricky scenarios.

Examples:
- Very long input vs. very short input
- Missing or ambiguous information
- Conflicting requirements ("make it short and comprehensive")
- Invalid input that should be rejected gracefully

### Variant / Alternative Intent
The same skill used for a different purpose or in a different domain.

Example for a "blog writing" skill: "Rewrite this existing blog post to improve the SEO" (not new content, but optimization—still in scope but different workflow)

## Assertions: Measuring Quality

Assertions are objective checks that measure whether the skill's output meets standards. They're saved in `eval_metadata.json` alongside each test case.

### When to Use Assertions

- **Use assertions** for objectively verifiable outputs: file formats, code syntax, completeness, data validation
- **Skip assertions** for subjective qualities: writing style, creativity, tone, design aesthetics (use qualitative feedback instead)

### Anatomy of a Good Assertion

```json
{
  "name": "code_syntax_valid",
  "description": "Generated Python code has no syntax errors and can be imported without errors"
}
```

- **name**: Machine-readable identifier (snake_case)
- **description**: Human-readable what/why (reads clearly in benchmark viewer)

### Example Assertions by Domain

#### Data Analysis Skill
- `output_file_exists` — CSV/JSON file written with expected name
- `required_columns_present` — All expected columns exist in output
- `no_null_values` — No missing data in critical fields
- `numeric_values_valid` — Numbers are in expected range (dates are valid, percentages < 100, etc.)

#### Code Generation Skill
- `code_syntax_valid` — No Python/JS/etc. syntax errors
- `imports_available` — All imported modules are standard library or mentioned dependencies
- `functions_defined` — All required function signatures present
- `test_coverage` — If tests are generated, basic structure is present

#### Content Skill
- `markdown_structure_complete` — Has headers, body, conclusion sections
- `minimum_word_count` — Prose meets minimum length requirement
- `keyword_present` — Target keyword appears in title/introduction
- `cta_included` — Call-to-action present in conclusion

#### API/Automation Skill
- `endpoint_reachable` — API endpoint is available (can ping successfully)
- `response_format_correct` — JSON/XML structure matches spec
- `all_required_fields` — Response includes all documented fields
- `error_handling_present` — Script handles common error cases (timeouts, invalid input, etc.)

### Writing Effective Assertions

**Anti-pattern (too specific/brittle):**
```
"The JSON includes exactly these fields in this exact order: id, name, email"
```
This fails if fields are reordered or new fields are added (sometimes OK, sometimes not).

**Better:**
```
"Required fields (id, name, email) are present in the output; order and additional fields don't matter"
```

**Anti-pattern (too vague):**
```
"The output is good"
```
This can't be evaluated programmatically.

**Better:**
```
"The output CSV has at least 5 rows and all numeric columns contain numbers (no text or null values)"
```

### How Many Assertions?

- **2-4 per test case** is typical
- Focus on discriminator assertions that fail if the skill is broken (not assertions that pass regardless of skill quality)
- Combine related checks into one assertion rather than many simple ones

Example:
- ❌ Bad: `file_exists`, `file_readable`, `file_has_data`, `file_is_csv`
- ✓ Good: `output_csv_is_valid` (covers all above)

## Evaluating Test Results

Once tests run, use the benchmark viewer (or manual review) to assess:

### Quantitative Markers
- **Pass rate** — What % of assertions passed? (Aim for >90% for release)
- **Time overhead** — How much longer with the skill? (Usually wants to be <50% slower, ideally <20%)
- **Token usage** — How many tokens per run? (Use as a proxy for complexity)

### Qualitative Markers
In the results viewer, read the actual outputs and ask:
- Does the skill produce what the user asked for?
- Are there obvious gaps or errors?
- Would a user accept this without revision?
- Are there patterns in failure modes (e.g., all fails on test case 3)?

### Passing but Wrong Assertions

Sometimes an assertion passes but the output is clearly wrong. This signals:
- The assertion is too lenient
- The skill is doing something unexpected
- There's a mismatch between what you expected and what the skill delivers

Comb through the qualitative outputs carefully during human review.

## Expanding Test Cases

After iteration 1:

1. Identify weak points from feedback and benchmarks (e.g., "the skill struggles with variant phrasings")
2. Add 2-3 new test cases that specifically target those weak points
3. Combine with the original test cases for iteration 2
4. Re-baseline and re-evaluate

This expands coverage without abandoning early tests.

## Example Test Suite Evolution

**Iteration 1 (minimal):**
- eval-1: Happy path (main use case)
- eval-2: Edge case (missing input)
- eval-3: Variant (related but different intent)

**Iteration 2+ (expanded):**
- All above, plus:
- eval-4: Large input (stress test)
- eval-5: Ambiguous input (requires clarification)
- eval-6: Integration scenario (skill works with other tools)
- eval-7: Error recovery (graceful handling of failure)

---

## Checklist for Test Case Readiness

Before running tests:

- ✓ At least 2-3 test cases written
- ✓ Each prompt is realistic (real user would ask this)
- ✓ Prompts include specific context (file names, values, URLs)
- ✓ Each test case covers a different aspect or workflow
- ✓ Assertions are objective and discriminating (not always passing)
- ✓ Assertions have clear, readable descriptions
- ✓ Expected outputs are narrative descriptions, not rigid specs
- ✓ You can explain why each test case matters

