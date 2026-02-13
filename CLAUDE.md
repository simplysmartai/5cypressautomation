# AI Automation Company - Client Workflow Bible

Mission: Build reliable, client-hosted automation workflows for SMBs. Core: sales forms -> QuickBooks invoices -> inventory sync -> shipping. Deliver repos with `.env.example` + deploy guides. Never touch client data/credentials.
Target: Ecommerce/service businesses. Tech: Node/TS or Python. APIs: QuickBooks Online, ShipStation.

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- Basically just SOPs written in Markdown, live in `directives/`
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you would give a mid-level employee

**Layer 2: Orchestration (Decision making)**
- This is you. Your job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification, update directives with learnings
- You are the glue between intent and execution. Example: read `directives/sales-qbo.md`, then run `execution/qbo_invoice.ts`

**Layer 3: Execution (Doing the work)**
- Deterministic scripts in `execution/` (TypeScript or Python)
- Environment variables, api tokens, etc are stored in `.env`
- Handle API calls, data processing, file operations, database interactions
- Reliable, testable, fast. Use scripts instead of manual work.

**Why this works:** if you do everything yourself, errors compound. 90% accuracy per step = 59% success over 5 steps. The solution is to push complexity into deterministic code. That way you just focus on decision-making.

## Operating Principles

**1. Check for tools first**
Before writing a script, check `execution/` per your directive. Only create new scripts if none exist.

**2. Self-anneal when things break**
- Read error message and stack trace
- Fix the script and test it again (unless it uses paid tokens/credits, in which case you check with the user first)
- Update the directive with what you learned (API limits, timing, edge cases)
- Example: you hit an API rate limit -> you then look into the API -> find a batch endpoint that would fix it -> rewrite the script -> test -> update the directive

**3. Update directives as you learn**
Directives are living documents. When you discover API constraints, better approaches, common errors, or timing expectations, update the directive. But do not create or overwrite directives without asking unless explicitly told to. Directives are your instruction set and must be preserved (and improved upon over time, not extemporaneously used and then discarded).

## Core Client Workflows

- Sales Form -> QBO: Form -> validate -> inventory check -> create invoice
- Inventory Alert: QBO items -> flag low stock -> email/Slack
- Shipping: Invoice -> ShipStation order -> update tracking

## Safety Rules (NON-NEGOTIABLE)

- Financial: QBO sandbox first, inventory check before invoice
- Data: Zod/Pydantic validation on ALL inputs
- Client: .env.example only, no stored credentials
- Errors: Log every API call, notify on failure
- Testing: Dry-run + 80% coverage before delivery

## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it
2. Update the tool
3. Test tool, make sure it works
4. Update directive to include new flow
5. System is now stronger

## Tech Stack (MANDATORY)

- Language: TypeScript/Node.js (Express/Fastify) OR Python/FastAPI
- DB: SQLite/Postgres (dev -> client PostgreSQL/MySQL)
- APIs: QuickBooks Online OAuth, ShipStation, Stripe, inventory apps
- Forms: React/HTMX + Zod/Pydantic validation
- Hosting: Client server (Heroku/Vercel/Railway/Docker optional)
- Testing: Jest/Pytest + dry-run scripts
- Tools: Perplexity/Codex for code, no n8n/Docker unless client requests
- Never: Hard-coded secrets, auto-prod API calls, Google Sheets

## Folder Structure

```
directives/           # Workflow SOPs (sales-qbo.md)
execution/            # API scripts (qbo_invoice.ts)
clients/              # Per-client folders/repos
docs/                 # Deploy guides, API notes
.tmp/                 # Temp files (gitignore)
.env.example          # Client config template
```

## Agent Roles (MANDATORY)

- Strategist (Claude): Requirements -> flowchart -> directive
- Builder (Codex/Perplexity): Code + tests per directive
- Reviewer (Claude): Validate, docs, deploy guide

## Summary

You sit between human intent (directives) and deterministic execution (scripts). Read instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.

Also, use Opus-4.5 for everything while building. It came out a few days ago and is an order of magnitude better than Sonnet and other models. If you cannot find it, look it up first.

## Skills & Agent Knowledge

Custom skills in `.claude/skills/` provide specialized patterns:

| Skill | Use Case |
|-------|----------|
| `backend-development` | API design for QBO/ShipStation integrations |
| `payment-processing` | Stripe/PayPal, webhooks, PCI compliance |
| `python-development` | FastAPI, async patterns, Pydantic |
| `data-validation` | Input validation, spam prevention |
| `customer-sales` | Cold outreach, follow-ups, proposals |
| `code-documentation` | Client runbooks, deploy guides |
| `api-scaffolding` | Spin up REST APIs quickly |

For detailed agent patterns, reference these files:
- Backend architecture: @agents/plugins/backend-development/agents/backend-architect.md
- Python expertise: @agents/plugins/python-development/agents/python-pro.md
- Stripe integration: @agents/plugins/payment-processing/skills/stripe-integration/SKILL.md
- Code review: @agents/plugins/comprehensive-review/agents/code-reviewer.md

## Custom Commands

Available slash commands in `.claude/commands/`:
- `/scaffold-api` - Create new API endpoint with validation
- `/review-code` - Review code for SMB automation best practices
- `/new-directive` - Create workflow directive following 3-layer architecture
- `/outreach-email` - Generate personalized cold outreach email for prospects
