# /post-mortem

Structured failure capture process that feeds the self-annealing loop.

## Purpose
When a script fails in production (or a client delivery breaks), run this command to:
1. Capture what happened and why
2. Record it in `logs/anneal.log` via `AnnealLogger`
3. Annotate the relevant directive with a `## Known Issues` entry
4. Produce a resolution plan and record it when fixed

The anneal log is the **memory of the system** — it grows smarter after every failure.

## Trigger
Run `/post-mortem` any time after:
- A script throws an unhandled exception
- A client reports something didn't work
- An API integration stops responding
- A deployment breaks something

## Inputs needed
Provide the following when running this command:

```
Script name:    e.g. create_qbo_invoice.py
Error message:  e.g. 401 Unauthorized — token expired
Directive:      e.g. directives/sales-to-qbo.md
Context:        e.g. Ran for client nexairi, order #142 at 14:32 UTC
```

## Process

### Step 1 — Record the failure
```python
from execution.shared.anneal import AnnealLogger

AnnealLogger.record_failure(
    script="create_qbo_invoice.py",
    error="401 Unauthorized — QBO token expired after 3600s",
    directive="directives/sales-to-qbo.md",
    context="Client nexairi, order #142, 2026-02-27 14:32 UTC"
)
```
This appends a JSON entry to `logs/anneal.log` and adds a row to the `## Known Issues` table in the directive.

### Step 2 — Diagnose

Ask: **Why did this fail?** Use context clues:
- Missing env var? → `python scripts/check_health.py`
- Expired token? → check token refresh logic in the script
- API rate limit? → check `execution/shared/retry.py` config
- Bad input data? → check Pydantic validation
- Placeholder script was called in production? → check `SCRIPT_STATUS` header

### Step 3 — Fix it
Edit the failing script. If the fix changes API behaviour or timing, update the directive:
- Add a `## Known Issues` row (already done by Step 1)
- Update the `## Flow` section if the process changes
- Update `## Edge Cases` if it's a new class of problem

### Step 4 — Record the resolution
```python
AnnealLogger.record_resolution(
    script="create_qbo_invoice.py",
    resolution="Added token refresh ahead of every API call. Tokens now refreshed if age > 3000s.",
    learning="QBO access tokens expire after 3600s but the expiry can come early under load. Always refresh proactively, not reactively."
)
```

### Step 5 — Verify
```bash
python scripts/check_health.py
```
Confirm anneal.log shows 0 unresolved failures.

## Output
- `logs/anneal.log` — failure + resolution JSON entries
- Directive file — `## Known Issues` table updated
- Future AI sessions — `AnnealLogger.get_learnings()` surfaces recent resolutions

## When the system self-anneals
At the start of complex execution sessions, load learnings so they inform the current session:

```python
from execution.shared.anneal import AnnealLogger

recent = AnnealLogger.get_learnings(limit=10)
for entry in recent:
    print(f"[LEARNING] {entry['script']}: {entry['learning']}")
```

## Related
- `/health-check` — surface all problems first
- `execution/shared/anneal.py` — the implementation
- `execution/shared/errors.py` — @safe_execute decorator (auto-records to anneal on failure)
