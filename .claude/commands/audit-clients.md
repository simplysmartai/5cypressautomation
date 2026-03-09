# /audit-clients

Validate all client data files against the canonical `ClientData` Pydantic schema.

## Purpose
Catch schema drift before it causes a production failure. Every client folder should have a `client.json` that matches `execution/shared/client_schema.py`. This command:
1. Loads every client folder in `clients/`
2. Validates it against the `ClientData` model
3. Reports validation errors, missing fields, and legacy format warnings
4. Optionally migrates legacy `info.json` / `client-config.json` to `client.json`

## Run it

```bash
# Validate only — print any schema errors
python scripts/audit_clients.py

# Validate + migrate legacy files to client.json
python scripts/audit_clients.py --migrate

# JSON output for server.js
python scripts/audit_clients.py --json
```

## What it checks per client
| Check | Severity |
|-------|----------|
| `client.json` exists | WARN if missing |
| All required fields present (slug, name, website, status, contact) | ERROR |
| `slug` format matches folder name | ERROR |
| `status` is valid enum (active, prospect, trial, churned, paused) | ERROR |
| Contact has at least one of email / phone | WARN |
| `api_access` keys present if status is `active` | WARN |
| ROI estimate populated for active clients | WARN |

## Manual audit steps (without the script)

For each folder in `clients/`:
1. Check what JSON files exist:
   ```bash
   ls clients/nexairi/
   ```
2. Load via the schema:
   ```python
   from execution.shared.client_schema import load_client
   client = load_client("nexairi")   # raises ValidationError on bad data
   print(client.model_dump())
   ```
3. Fix any validation errors, then save:
   ```python
   from execution.shared.client_schema import save_client
   save_client(client)   # writes canonical client.json
   ```

## Migrating legacy formats

| Old format | Location | Action |
|------------|----------|--------|
| `info.json` | nexairi, nexairi-mentis, simply-smart-consulting | `load_client()` merges automatically |
| `client-config.json` | remy-lasers | `load_client()` merges automatically |
| `.md` context files | marketing-team/context/ | Manual: copy relevant fields to `client.json` |

## Client schema reference

```python
class ClientData(BaseModel):
    slug:            str        # folder name, kebab-case
    name:            str
    website:         str
    status:          str        # active | prospect | trial | churned | paused
    contact:         ClientContact
    business:        BusinessInfo
    engagement_type: str        # retainer | one-time | trial
    trial_program:   TrialProgram | None
    roi_estimate:    ROIEstimate | None
    api_access:      ClientAPIAccess
    created_at:      str        # ISO 8601
    updated_at:      str
    notes:           str
```

Full schema: `execution/shared/client_schema.py`

## Related
- `/health-check` — lists clients with legacy format warnings
- `/post-mortem` — if a client operation failed due to bad data
- `execution/shared/client_schema.py` — Pydantic models
- `scripts/normalize_clients.py` — migration script (TODO 8)
