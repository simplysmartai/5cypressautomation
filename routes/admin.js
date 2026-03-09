/**
 * routes/admin.js
 * Admin page serves + all /admin/* and /admin/api/* endpoints.
 * adminAuth is applied at the /admin prefix in server.js.
 */
const express = require('express');
const path = require('path');
const fs = require('fs');
const { body, validationResult } = require('express-validator');

const router = express.Router();
const ROOT = path.join(__dirname, '..');

// ── Helper: resolve marketing team root ─────────────────────────────────────
function getMarketingBasePath() {
  return process.env.MARKETING_TEAM_PATH || path.join(ROOT, 'marketing-team');
}

function getClientsConfigPath() {
  const base = getMarketingBasePath();
  const mktgPath = path.join(base, 'config', 'clients.json');
  return fs.existsSync(mktgPath) ? mktgPath : path.join(ROOT, 'config', 'clients.json');
}

// ── Admin page routes ────────────────────────────────────────────────────────
// Note: adminAuth is applied at the /admin prefix in server.js
router.get('/', (_req, res) => res.sendFile(path.join(ROOT, 'public', 'admin', 'index.html')));
router.get('/clients', (_req, res) => res.sendFile(path.join(ROOT, 'public', 'admin', 'clients.html')));
router.get('/seo', (_req, res) => res.sendFile(path.join(ROOT, 'public', 'admin', 'seo.html')));
router.get('/marketing', (_req, res) => res.sendFile(path.join(ROOT, 'public', 'admin', 'marketing.html')));
router.get('/leads', (_req, res) => res.sendFile(path.join(ROOT, 'public', 'admin', 'leads.html')));
router.get('/newclient', (_req, res) =>
  res.sendFile(path.join(ROOT, 'public', 'admin', 'newclient-form.html'))
);

// ── Admin: New client scaffold (POST) ────────────────────────────────────────
router.post(
  '/newclient',
  [
    body('company_name').trim().notEmpty().isLength({ max: 100 }).escape(),
    body('website').optional({ checkFalsy: true }).trim().isURL({ require_protocol: false }),
    body('industry').trim().notEmpty().isLength({ max: 100 }).escape(),
    body('contact_name').trim().notEmpty().isLength({ max: 150 }).escape(),
    body('contact_email').optional({ checkFalsy: true }).isEmail().normalizeEmail(),
    body('what_they_sell').trim().notEmpty().isLength({ max: 1000 }),
    body('who_they_sell_to').trim().notEmpty().isLength({ max: 300 }),
    body('main_goal').trim().notEmpty().isLength({ max: 300 }),
    body('services').optional({ checkFalsy: true }).trim().isLength({ max: 500 }),
    body('automations').optional({ checkFalsy: true }).trim().isLength({ max: 500 }),
    body('contract_start').optional({ checkFalsy: true }).isISO8601(),
    body('bio').optional({ checkFalsy: true }).trim().isLength({ max: 3000 }),
  ],
  (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

    const {
      company_name, website, industry, contact_name, contact_email,
      what_they_sell, who_they_sell_to, main_goal, services, automations,
      contract_start, bio
    } = req.body;

    const todayStr = new Date().toISOString().split('T')[0];
    const clientId = company_name
      .toLowerCase()
      .replace(/[^a-z0-9\s-]/g, '')
      .trim()
      .replace(/\s+/g, '-');

    const marketingBase = getMarketingBasePath();
    const configDir   = path.join(marketingBase, 'config');
    const contextDir  = path.join(marketingBase, 'context');
    const clientsDir  = path.join(marketingBase, 'clients', clientId);
    const outputDir   = path.join(marketingBase, 'output', clientId);
    const meetingsDir = path.join(clientsDir, 'meetings');
    const assetsDir   = path.join(clientsDir, 'assets');

    // Path-traversal guard
    for (const d of [configDir, contextDir, clientsDir, outputDir, meetingsDir, assetsDir]) {
      if (!d.startsWith(marketingBase)) {
        return res.status(400).json({ error: 'Invalid client ID — path traversal detected' });
      }
    }

    const serviceList = (services || '').split(',').map(s => s.trim()).filter(Boolean);
    const autoList    = (automations || '').split(',').map(s => s.trim()).filter(Boolean);

    const jsonEntry = {
      id: clientId, name: company_name, status: 'active', industry,
      contact_name, contact_email: contact_email || '(TBD)',
      website: website || '(TBD)', onboarded: todayStr,
      contract_start: contract_start || todayStr, billing_cycle: 'monthly',
      services: serviceList,
      automations: { count: autoList.length, active: [], proposed: autoList },
      files: {
        context: `context/${clientId}.md`,
        history: `clients/${clientId}/history.md`,
        automations: `clients/${clientId}/automations.md`,
        output_folder: `output/${clientId}/`
      },
      notes: (bio || '').substring(0, 200)
    };

    const contextMd = `# Client Context: ${company_name}
**ID:** ${clientId}
**Status:** active
**Last Updated:** ${todayStr}

---

## Company Overview
- **Company name:** ${company_name}
- **Website:** ${website || '(TBD)'}
- **Industry:** ${industry}
- **Primary contact:** ${contact_name}
- **Contact email:** ${contact_email || '(TBD)'}
- **Company size:** (TBD)
- **Revenue / ARR:** (TBD)

## What They Sell
${what_they_sell}

## Target Audience
- **Ideal customer:** ${who_they_sell_to}
- **Key pain points:** (TBD)
- **Top objections:** (TBD)

## Marketing Goals
- **#1 goal:** ${main_goal}
- **90-day success:** (TBD)
- **KPIs:** (TBD)

## Services We're Providing
${serviceList.length ? serviceList.map(s => `- ${s}`).join('\n') : '- (TBD)'}

## Current Marketing Status
- **Active channels:** (TBD)
- **Email list size:** (TBD)
- **Monthly website traffic:** (TBD)

## Tools & Integrations
- **CRM:** (TBD)
- **Email platform:** (TBD)

## Competitors
- (TBD)

## Brand Voice & Preferences
- **Tone:** (TBD)

## Notes & Background
${bio || '(TBD)'}
`;

    const historyMd = `# Client History: ${company_name}
**ID:** ${clientId}
**Onboarded:** ${todayStr}

---

## Work Log

| Date | Deliverable | Skill/Workflow Used | File Location | Notes |
|------|------------|-------------------|--------------|-------|
| ${todayStr} | Client onboarded | /newclient | context/${clientId}.md | Initial setup |
`;

    const automationsMd = `# Automation Tracker: ${company_name}
**ID:** ${clientId}
**Last Updated:** ${todayStr}

---

## Active Automations

| ID | Automation Name | Type | Status | Created | Tools | Notes |
|----|----------------|------|--------|---------|-------|-------|
| — | None yet | — | — | — | — | — |

## Proposed Automations
${autoList.length ? autoList.map(a => `- ${a}`).join('\n') : '- None yet'}
`;

    try {
      [configDir, contextDir, clientsDir, outputDir, meetingsDir, assetsDir].forEach(d =>
        fs.mkdirSync(d, { recursive: true })
      );

      const clientsJsonPath = path.join(configDir, 'clients.json');
      let clientsList = { agency: '5 Cypress Automation', last_updated: todayStr, clients: [] };
      if (fs.existsSync(clientsJsonPath)) {
        try { clientsList = JSON.parse(fs.readFileSync(clientsJsonPath, 'utf8')); } catch (_) {}
      }
      clientsList.clients = clientsList.clients.filter(c => c.id !== clientId);
      clientsList.clients.push(jsonEntry);
      clientsList.last_updated = todayStr;
      fs.writeFileSync(clientsJsonPath, JSON.stringify(clientsList, null, 2), 'utf8');

      fs.writeFileSync(path.join(contextDir, `${clientId}.md`), contextMd, 'utf8');
      fs.writeFileSync(path.join(clientsDir, 'history.md'), historyMd, 'utf8');
      fs.writeFileSync(path.join(clientsDir, 'automations.md'), automationsMd, 'utf8');

      console.log(`[ADMIN] New client scaffolded: ${clientId} (${company_name})`);
      res.json({
        success: true, clientId,
        files: {
          context: `context/${clientId}.md`,
          history: `clients/${clientId}/history.md`,
          automations: `clients/${clientId}/automations.md`,
          config: 'config/clients.json (updated)',
          output: `output/${clientId}/ (folder created)`
        }
      });
    } catch (err) {
      console.error('[ADMIN] Failed to scaffold client files:', err);
      res.status(500).json({ error: 'Failed to write client files', detail: err.message });
    }
  }
);

// ── Admin API: Clients list ──────────────────────────────────────────────────
router.get('/api/clients', (req, res) => {
  try {
    const clientsPath = getClientsConfigPath();
    if (!fs.existsSync(clientsPath)) return res.status(404).json({ error: 'clients.json not found' });
    const raw = fs.readFileSync(clientsPath, 'utf8');
    const parsed = JSON.parse(raw);
    const data = Array.isArray(parsed?.clients) ? parsed.clients : [];
    res.json({ source: clientsPath, count: data.length, clients: data });
  } catch (error) {
    console.error('[ADMIN] Failed to load clients list:', error);
    res.status(500).json({ error: 'Failed to load clients', detail: error.message });
  }
});

// ── Admin API: SEO audit (PageSpeed) ────────────────────────────────────────
router.get('/api/seo-audit', async (req, res) => {
  try {
    const target   = String(req.query.url || '').trim();
    const strategy = String(req.query.strategy || 'mobile').trim().toLowerCase();
    const apiKey   = process.env.GOOGLE_PAGESPEED_API_KEY;

    if (!apiKey) return res.status(503).json({ error: 'GOOGLE_PAGESPEED_API_KEY is not configured' });
    if (!target)  return res.status(400).json({ error: 'Missing required query param: url' });

    const normalizedStrategy = strategy === 'desktop' ? 'desktop' : 'mobile';
    const normalizedUrl = /^https?:\/\//i.test(target) ? target : `https://${target}`;

    let validated;
    try { validated = new URL(normalizedUrl); }
    catch (_) { return res.status(400).json({ error: 'Invalid URL provided' }); }

    const endpoint = new URL('https://www.googleapis.com/pagespeedonline/v5/runPagespeed');
    endpoint.searchParams.set('url',      validated.toString());
    endpoint.searchParams.set('strategy', normalizedStrategy);
    endpoint.searchParams.set('key',      apiKey);
    ['performance', 'accessibility', 'best-practices', 'seo'].forEach(cat =>
      endpoint.searchParams.append('category', cat)
    );

    const response = await fetch(endpoint.toString(), { headers: { Accept: 'application/json' } });
    const payload  = await response.json();

    if (!response.ok) {
      return res.status(response.status).json({
        error: 'PageSpeed request failed',
        detail: payload?.error?.message || 'Unknown API error',
        raw: payload
      });
    }

    const categories        = payload?.lighthouseResult?.categories || {};
    const audits            = payload?.lighthouseResult?.audits     || {};
    const loadingExperience = payload?.loadingExperience?.metrics   || {};

    res.json({
      fetchedAt: new Date().toISOString(),
      requested: { url: validated.toString(), strategy: normalizedStrategy },
      scores: {
        performance:   categories.performance?.score          ?? null,
        accessibility: categories.accessibility?.score        ?? null,
        bestPractices: categories['best-practices']?.score    ?? null,
        seo:           categories.seo?.score                  ?? null
      },
      vitals: {
        lcp:  audits['largest-contentful-paint']?.displayValue  || null,
        cls:  audits['cumulative-layout-shift']?.displayValue   || null,
        inp:  audits['interaction-to-next-paint']?.displayValue || null,
        fcp:  audits['first-contentful-paint']?.displayValue    || null,
        ttfb: audits['server-response-time']?.displayValue      || null
      },
      fieldData: {
        lcp: loadingExperience.LARGEST_CONTENTFUL_PAINT_MS?.percentile   || null,
        cls: loadingExperience.CUMULATIVE_LAYOUT_SHIFT_SCORE?.percentile || null,
        inp: loadingExperience.INTERACTION_TO_NEXT_PAINT?.percentile     || null,
        fcp: loadingExperience.FIRST_CONTENTFUL_PAINT_MS?.percentile     || null
      },
      lighthouseLink: payload?.lighthouseResult?.finalDisplayedUrl || validated.toString()
    });
  } catch (error) {
    console.error('[ADMIN] SEO audit endpoint failed:', error);
    res.status(500).json({ error: 'Failed to run SEO audit', detail: error.message });
  }
});

// ── Admin API: Pipeline action ───────────────────────────────────────────────
router.post('/api/pipeline-action', (req, res) => {
  const { action, id } = req.body;
  console.log(`[ADMIN] Pipeline action: ${action} for ${id}`);
  res.json({ success: true, message: `Action ${action} processed for ${id}`, timestamp: new Date().toISOString() });
});

// ── Admin API: Leads (from DB) ───────────────────────────────────────────────
router.get('/api/leads', (req, res) => {
  const db = req.app.get('db');
  try {
    const limit = Math.min(parseInt(req.query.limit) || 50, 200);
    const leads = db.prepare('SELECT * FROM leads ORDER BY createdAt DESC LIMIT ?').all(limit);
    const total = db.prepare('SELECT COUNT(*) as count FROM leads').get().count;
    res.json({ total, leads });
  } catch (err) {
    console.error('[ADMIN] Leads query failed:', err.message);
    res.status(500).json({ error: 'Failed to load leads', detail: err.message });
  }
});

// ── Admin API: Stats ─────────────────────────────────────────────────────────
router.get('/api/stats', (req, res) => {
  const db = req.app.get('db');
  try {
    const leadCount   = db.prepare('SELECT COUNT(*) as c FROM leads').get().c;
    const clientCount = db.prepare('SELECT COUNT(*) as c FROM clients').get().c;
    const auditCount  = db.prepare('SELECT COUNT(*) as c FROM seo_audits').get().c;
    const newLeads    = db
      .prepare("SELECT COUNT(*) as c FROM leads WHERE createdAt >= datetime('now','-7 days')")
      .get().c;
    res.json({ leadCount, clientCount, auditCount, newLeads, serverTime: new Date().toISOString() });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── Admin API: Marketing team file listing ───────────────────────────────────
router.get('/api/marketing', (req, res) => {
  try {
    const mktgPath  = process.env.MARKETING_TEAM_PATH || path.join(ROOT, 'marketing-team');
    const contextDir = path.join(mktgPath, 'context');
    const outputDir  = path.join(mktgPath, 'output');

    const clients = [];
    if (fs.existsSync(contextDir)) {
      fs.readdirSync(contextDir)
        .filter(f => f.endsWith('.md') && f !== 'agency.md' && f !== 'client-template.md')
        .forEach(file => {
          const slug = file.replace('.md', '');
          const outputs = [];
          const clientOutputDir = path.join(outputDir, slug);
          if (fs.existsSync(clientOutputDir)) {
            fs.readdirSync(clientOutputDir).forEach(outFile => {
              const stat = fs.statSync(path.join(clientOutputDir, outFile));
              outputs.push({ name: outFile, size: stat.size, modified: stat.mtime.toISOString() });
            });
          }
          clients.push({ slug, contextFile: file, outputCount: outputs.length, outputs });
        });
    }
    res.json({ mktgPath, clientCount: clients.length, clients });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── Admin API: Serve marketing output file ───────────────────────────────────
router.get('/api/marketing/file', (req, res) => {
  try {
    const mktgPath = process.env.MARKETING_TEAM_PATH || path.join(ROOT, 'marketing-team');
    const { client, file } = req.query;
    if (!client || !file) return res.status(400).json({ error: 'client and file params required' });
    const filePath = path.join(mktgPath, 'output', path.basename(client), path.basename(file));
    if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'File not found' });
    res.sendFile(filePath);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── PATCH /admin/api/leads/:id — update lead status ─────────────────────────
router.patch('/api/leads/:id', (req, res) => {
  const db = req.app.get('db');
  const { status } = req.body;
  const allowed = ['new', 'contacted', 'closed', 'booked', 'canceled'];
  if (!allowed.includes(status)) {
    return res.status(400).json({ error: `Invalid status. Allowed: ${allowed.join(', ')}` });
  }
  try {
    const info = db.prepare('UPDATE leads SET status = ? WHERE id = ?').run(status, Number(req.params.id));
    if (info.changes === 0) return res.status(404).json({ error: 'Lead not found' });
    res.json({ success: true, status });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// ── DELETE /admin/api/leads/:id — remove a lead ───────────────────────────────
router.delete('/api/leads/:id', (req, res) => {
  const db = req.app.get('db');
  try {
    const info = db.prepare('DELETE FROM leads WHERE id = ?').run(Number(req.params.id));
    if (info.changes === 0) return res.status(404).json({ error: 'Lead not found' });
    res.json({ success: true });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
