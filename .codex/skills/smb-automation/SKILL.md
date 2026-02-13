---
name: smb-automation
description: SMB business automation workflows for QuickBooks, ShipStation, and payment processing. Use when building client automation workflows, sales-to-invoice pipelines, or inventory management systems.
---

# SMB Automation Skill

## When to Use
- Creating sales form to QuickBooks invoice workflows
- Building inventory sync and alert systems
- Implementing shipping automation with ShipStation
- Setting up payment processing with Stripe/PayPal

## 3-Layer Architecture (from CLAUDE.md)

### Layer 1: Directives (What to do)
- SOPs in `directives/` folder
- Natural language instructions like for a mid-level employee
- Define goals, inputs, tools/scripts to use, outputs, edge cases

### Layer 2: Orchestration (You - Decision making)
- Read directives, call execution tools in the right order
- Handle errors, ask for clarification
- Update directives with learnings

### Layer 3: Execution (Doing the work)
- Deterministic scripts in `execution/`
- Handle API calls, data processing
- Reliable, testable, fast

## Available Directives
| Directive | Purpose |
|-----------|---------|
| `directives/sales-to-qbo.md` | Form submission → validate → inventory check → QBO invoice |
| `directives/onboard_client.md` | Welcome email + calendar scheduling |
| `directives/manage_clients.md` | Client lifecycle management |
| `directives/prevent_contact_form_spam.md` | Form validation and spam prevention |

## Execution Scripts
| Script | Purpose |
|--------|---------|
| `execution/create_client.py` | Create client folders with structure |
| `execution/onboard_client.py` | Complete onboarding workflow |
| `execution/send_email.py` | SMTP/Resend email delivery |
| `execution/list_clients.py` | List managed clients |
| `execution/log_activity.py` | Activity logging |
| `execution/create_calendar_link.py` | Generate scheduling links |

## Key Integrations
- **QuickBooks Online** - OAuth, invoices, inventory
- **ShipStation** - Shipping labels, order sync
- **Stripe/PayPal** - Payment processing, webhooks
- **Resend/SMTP** - Email delivery

## Safety Rules (from CLAUDE.md)
- QBO sandbox first, inventory check before invoice
- Zod/Pydantic validation on ALL inputs
- .env.example only, no stored credentials
- Log every API call, notify on failure
- Dry-run + 80% coverage before delivery

## Agent Plugins Available
The following plugins from `agents/plugins/` are relevant:
- `payment-processing` - Stripe integration, webhooks, PCI compliance
- `backend-development` - API design, microservices patterns
- `python-development` - FastAPI, async patterns, testing
- `data-validation-suite` - Input validation with Pydantic/Zod
- `api-scaffolding` - FastAPI/Django project templates
- `customer-sales-automation` - Sales outreach, CRM patterns
