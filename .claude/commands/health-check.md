# /health-check

Run a full system health audit and print a colour-coded status report.

## Purpose
Quickly determine whether the system is safe to run before executing scripts, making a client delivery, or diagnosing a production issue.

## What it checks
1. **Python version** — must be ≥ 3.9, recommend 3.12+
2. **Required directories** — `logs/`, `execution/shared/`, `directives/` exist
3. **Shared module files** — all 8 files in `execution/shared/` are present
4. **Environment variables** — CRITICAL (QBO, Stripe) and optional (Resend, Telegram, DataForSEO, Anthropic, Zoho) vars are set
5. **Placeholder scripts** — lists any script with SCRIPT_STATUS: PLACEHOLDER / NEEDS_CONFIG / PARTIAL
6. **Bare except: regression** — confirms zero bare `except:` clauses remain
7. **Anneal log** — surfaces any unresolved failures from `logs/anneal.log`
8. **Recent log errors** — scans today's structured log for ERROR/CRITICAL entries
9. **Client data files** — checks that each client folder has at least one JSON file
10. **Config JSON** — validates `config/clients.json` and `config/pricing.json` are parseable
11. **Server in-memory stores** — warns if `server.js` still holds `orders[]`, `clients[]`, or `workItems[]`

## Commands to run

```bash
# Standard — full colour report
python scripts/check_health.py

# Machine-readable — for CI or server.js subprocess call
python scripts/check_health.py --json

# Auto-fix safe items (creates missing directories)
python scripts/check_health.py --fix

# Fail fast — exit 1 on first ERROR/CRITICAL (good for pre-commit hook)
python scripts/check_health.py --fail-fast
```

## Exit codes
| Code | Meaning |
|------|---------|
| 0    | All checks passed |
| 1    | At least one ERROR or CRITICAL |

## When to run
- **Before any deployment** — `python scripts/check_health.py --fail-fast`
- **First run on a new machine** — `python scripts/check_health.py --fix`
- **After a production failure** — to quickly find the root cause before running `/post-mortem`
- **Before a client delivery** — confirm placeholder scripts aren't being called

## Related
- `/post-mortem` — deep-dive on a specific failure and update anneal log
- `/audit-clients` — validate client data specifically
- `/deploy-check` — final gate before deploy (superset of health-check)
- `scripts/check_readiness.py` — script-status-only view
