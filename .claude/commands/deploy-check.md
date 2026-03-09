# /deploy-check

Full pre-deployment gate. Runs every check before pushing to production.

## Purpose
`/deploy-check` is the final safeguard before any code reaches a client's server.
It chains health checks, test runs, placeholder verification, and server validation
into a single pass/fail decision.

**Do not deploy if this fails.**

## Full checklist

### 1. Environment
```bash
python scripts/check_health.py --fail-fast
```
Must exit 0. If not, fix errors before continuing.

### 2. Placeholder scripts
```bash
python scripts/check_readiness.py --fail-on-placeholder
```
No PLACEHOLDER scripts should be called by any active workflow.
Cross-reference `directives/` to confirm placeholders aren't referenced in active flows.

### 3. Tests
```bash
pytest --cov=execution --cov-fail-under=80
```
Coverage must be ≥ 80%. All tests must pass.

### 4. No bare except: regressions
```bash
grep -rn "^\s*except:\s*$" execution/*.py
```
Must return empty (zero matches).

### 5. Env vars on target server
SSH into the target and run:
```bash
python scripts/check_health.py --no-colour --json | python -c "
import json, sys
results = json.load(sys.stdin)
errors = [r for r in results if r['level'] in ('ERROR', 'CRITICAL')]
for e in errors: print(e['message'])
sys.exit(len(errors))
"
```

### 6. Node.js server build
```bash
node -e "require('./server.js')" 2>&1 | head -5
```
Server must start without errors.

### 7. Database connectivity
```bash
node -e "
const db = require('./db.js');
const row = db.prepare('SELECT 1 AS ok').get();
console.log(row.ok === 1 ? 'DB OK' : 'DB FAIL');
"
```

### 8. Git status (clean deploy)
```bash
git status --short
```
No uncommitted changes should be on the branch being deployed.

## One-liner (for CI / hook)

```bash
python scripts/check_health.py --fail-fast && \
python scripts/check_readiness.py --fail-on-placeholder && \
pytest --cov=execution --cov-fail-under=80 -q && \
echo "✓ Deploy check passed"
```

## Add to package.json

```json
"scripts": {
  "predeploy": "python scripts/check_health.py --fail-fast && python scripts/check_readiness.py --fail-on-placeholder"
}
```

## Deploy flow (after check passes)

```bash
# 1. Run the check
npm run predeploy

# 2. Deploy to server (Heroku / Railway / VPS)
git push heroku main
# or
railway up
# or
rsync -avz --exclude node_modules ./ user@server:/app/

# 3. Verify on server
ssh user@server "cd /app && python scripts/check_health.py --no-colour"
```

## If the check fails

| Failure | Action |
|---------|--------|
| ERROR: QBO creds missing | Add to server .env, re-run |
| WARN: placeholder scripts | Tag them, confirm not in active directive |
| Test failures | Fix tests or the underlying script |
| DB connectivity issue | Check SQLite file path / permissions |
| Server won't start | Check server.js for syntax errors |

## Related
- `/health-check` — system-level pre-flight
- `/test` — run tests independently
- `/post-mortem` — if deploy causes a production failure
- `execution/shared/errors.py` — error codes and types
