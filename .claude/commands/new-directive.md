---
description: Create a new workflow directive following the 3-layer architecture
---

Create a new directive for: $ARGUMENTS

## Directive Template

Create file at `directives/[name].md`:

```markdown
# [Workflow Name]

> Brief description of what this workflow accomplishes

## Purpose
Why this workflow exists and what problem it solves.

## Trigger
What initiates this workflow:
- Manual: User requests it
- Scheduled: Runs on a cron schedule
- Event: Triggered by webhook or external event

## Inputs
| Input | Type | Required | Description |
|-------|------|----------|-------------|
| ... | ... | ... | ... |

## Steps

1. **Validate inputs**
   - Check required fields
   - Validate formats
   - Use: `execution/validators.py`

2. **[Main action]**
   - Description
   - Use: `execution/[script].py`
   - Expected output: ...

3. **[Follow-up action]**
   - Description
   - Handle edge cases: ...

## Outputs
- What gets created/updated
- Where results are stored
- Who gets notified

## Error Handling
| Error | Cause | Resolution |
|-------|-------|------------|
| ... | ... | ... |

## Edge Cases
- Case 1: How to handle
- Case 2: How to handle

## Related
- `directives/[related].md`
- `execution/[script].py`
```

## Checklist

After creating:
- [ ] Directive saved to `directives/`
- [ ] Referenced execution scripts exist (or created)
- [ ] Related directives linked
- [ ] Tested with dry-run if applicable
