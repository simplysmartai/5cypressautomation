# 5 Cypress Automation

Resilient AI automation and scalable operations architecture. Rooted in reliability, built for limitless growth.

**Live on GitHub:** [github.com/simplysmartai/5cypressautomation](https://github.com/simplysmartai/5cypressautomation)

---

## 🚀 Deploy Now

**Ready to go live?** See [DEPLOYMENT.md](DEPLOYMENT.md) for:
- Railway deployment (5 minutes)
- Modal webhooks setup (10 minutes)
- Environment variables guide
- Custom domain setup

**Quick deploy:**
```bash
# Railway (Node.js + site hosting)
# → Sign up at railway.app, connect GitHub, deploy

# Modal (automation workflows)
pip install modal
modal token new
modal deploy execution/modal_webhook.py
```

---

## 🚀 Quick Start (New? Start Here)

**Goal:** Close your first client in 7 days

1. **Read:** [QUICK_START.md](QUICK_START.md) - Complete 7-day sprint guide
2. **Test:** `python execution/live_demo_automation.py` - See the automation work
3. **Deploy:** `modal deploy execution/modal_production.py` - Go live
4. **Sell:** Use [clients/remy-lasers/pitch-deck-trial-program.md](clients/remy-lasers/pitch-deck-trial-program.md)

**Key Resources:**
- 📊 [BATTLE_PLAN.md](BATTLE_PLAN.md) - Strategic roadmap to first revenue
- 🏗️ [HOSTING_ARCHITECTURE.md](HOSTING_ARCHITECTURE.md) - Why you don't need a VPS
- 📦 [SERVICES_ROADMAP.md](SERVICES_ROADMAP.md) - All service packages & pricing
- 🎯 [LAUNCH_READINESS.md](LAUNCH_READINESS.md) - What's ready, what's not

**Current Status:**
✅ Website rebranded to "5 Cypress Automation"  
✅ Server running at http://localhost:3000  
✅ Live demo tested and working  
✅ Modal deployment ready  
❌ First paying client (work in progress)

---

## Architecture Overview

We operate on a 3-layer architecture designed for maximum endurance and scale:

1. **Directives** (`directives/`) - The root system. Natural language SOPs that define deterministic goals.
2. **Orchestration** (AI logic) - The branching layer. Intelligent routing and decision-making via agents.
3. **Execution** (`execution/`) - The endurance layer. Deterministic Python scripts that perform the work.

See [CLAUDE.md](CLAUDE.md), [AGENTS.md](AGENTS.md), or [GEMINI.md](GEMINI.md) for complete agent instructions.

## Directory Structure

```
├── directives/          # Markdown SOPs defining workflows
├── execution/           # Python scripts for deterministic operations
├── .tmp/               # Temporary intermediate files (git-ignored)
├── .env                # Environment variables and API keys (git-ignored)
├── credentials.json    # Google OAuth credentials (git-ignored)
└── token.json         # Google OAuth token (git-ignored)
```

## Getting Started

### 1. Environment Setup

Copy [.env](.env) and fill in your API keys:

```bash
# Required API keys
ANTHROPIC_API_KEY=your_key_here
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Google Workspace Setup

1. Create a project at [Google Cloud Console](https://console.cloud.google.com)
2. Enable Google Sheets and Google Slides APIs
3. Create OAuth 2.0 credentials
4. Download `credentials.json` to the project root

### 4. Modal Setup (for webhooks)

```bash
pip install modal
modal token new
modal deploy execution/modal_webhook.py
```

## Key Principles

**Deliverables vs Intermediates:**
- Deliverables live in cloud services (Google Sheets, Slides, etc.)
- Local files in `.tmp/` are temporary and can be regenerated

**Self-Annealing:**
- When errors occur, fix the script, test it, and update the directive
- The system improves over time through learning

**Tool-First Approach:**
- Always check `execution/` for existing scripts before creating new ones
- Push complexity into deterministic code, not AI decision-making

## Usage

Work with AI agents by referencing directives:

```
"Follow the directive in directives/scrape_website.md to scrape example.com"
```

Agents will:
1. Read the directive
2. Call execution scripts in the correct order
3. Handle errors and edge cases
4. Update directives with learnings

## Webhooks

Event-driven execution via Modal. See [directives/add_webhook.md](directives/add_webhook.md) for setup.

Available endpoints:
- List webhooks: `https://nick-90891--claude-orchestrator-list-webhooks.modal.run`
- Execute directive: `https://nick-90891--claude-orchestrator-directive.modal.run?slug={slug}`

All webhook activity streams to Slack in real-time.

## Contributing

When adding new workflows:
1. Create a directive in `directives/`
2. Build execution scripts in `execution/`
3. Test thoroughly
4. Update this README if needed

## License

Proprietary - Simply Smart Automation
