# 5 Cypress Automation — AI Marketing Team
## Quick Start Guide

---

### What's In This Folder

This is your complete AI Marketing Team setup for Claude Code. It contains:

- **CLAUDE.md** — Master instructions that tell Claude how to navigate this project
- **context/** — Agency profile + client context templates
- **sops/** — Standard operating procedures for each deliverable type
- **skills/** — 5 skill definitions that Claude uses as its "playbook"
- **references/** — Knowledge base: frameworks, email patterns, dashboard templates
- **output/** — Where all client deliverables get saved automatically

---

### First-Time Setup (Do This Once)

**Step 1: Prerequisites**
Make sure you have these installed:
- Claude Code (CLI) — https://docs.anthropic.com/claude-code
- (Optional but recommended) Perplexity MCP — for research skills
- (Optional) Nano Banana MCP — for image/creative generation

**Step 2: Open in VS Code**
1. Open VS Code
2. Open this folder (`5cypress-marketing-team`) as your project
3. Open the integrated terminal

**Step 3: Launch Claude Code**
In the terminal, run:
```
claude
```

**Step 4: Paste the Setup Prompt**
Open `SETUP-PROMPT.md`, copy the prompt inside it, and paste it into Claude Code.
Claude will read all the files and confirm it's ready.

**Step 5: Create Your First Client**
When Claude asks for client details, provide what you have. Claude will create a context file at `context/[client-name].md`. The more you fill in, the better the output.

---

### Daily Use — How to Get Deliverables

Once set up, just talk to Claude naturally or use slash commands:

| What You Want | What to Type |
|---------------|--------------|
| Strategy brief for a client | `/research [client name]` |
| Email campaign | `/email [client name] — [campaign type]` |
| Performance report or dashboard | `/report [client name] — [period]` |
| Social media posts | `/content [client name] — [topic]` |
| Turn materials into a presentation | `/present [client name] — [source file]` |
| Onboard a new client | `/newclient` |

---

### Adding a New Client

1. Type `/newclient` in Claude Code
2. Tell Claude the client name and whatever details you have
3. Claude creates `context/[client-name].md` from the template
4. Fill in any gaps directly in that file
5. You're ready to run any skill against that client

---

### Where Deliverables Are Saved

Everything goes to `/output/[client-name]/` automatically.

Examples:
- `output/acme-tech/strategy-brief-2025-11.md`
- `output/acme-tech/email-campaign-nurture-2025-11.md`
- `output/acme-tech/dashboard-october-2025.html`

HTML files (dashboards, presentations) can be opened directly in a browser.

---

### The 5 Skills

| Skill | What It Does |
|-------|--------------|
| `marketing-research-strategy` | Market research + 90-day strategy brief |
| `email-campaign` | Full email sequences and campaigns |
| `data-analysis-reporting` | Performance reports and interactive dashboards |
| `social-media-content` | LinkedIn and social posts |
| `campaign-presenter` | Turns deliverables into client presentations |

---

### Tips for Best Results

- **Fill out client context files thoroughly.** The more Claude knows about a client, the more specific and useful the output.
- **Run `/research` first for new clients.** The strategy brief informs everything else.
- **Chain skills together for big projects.** Ask Claude to run research + email + report in one go for a full campaign project.
- **Save your client context files carefully.** They're the memory of your client relationships.
- **Review and refine output before sending to clients.** Claude does the heavy lifting; you add the final human judgment.

---

*Built for 5 Cypress Automation | www.5cypress.com*
