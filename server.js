const express = require('express');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');
require('dotenv').config();
const { exec } = require('child_process');
const helmet = require('helmet');
const morgan = require('morgan');
const rateLimit = require('express-rate-limit');
const xss = require('xss-clean');
const hpp = require('hpp');
const { body, validationResult } = require('express-validator');
const db = require('./db');

// Initialize Stripe gracefully
let stripe;
if (process.env.STRIPE_SECRET_KEY) {
  stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
} else {
  console.warn('WARNING: STRIPE_SECRET_KEY is missing. Payment features will be disabled.');
}

const app = express();

// Rate Limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per window
  message: 'Too many requests from this IP, please try again after 15 minutes'
});

// Apply rate limiting to all requests
app.use('/api/', limiter);

// Security Middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://unpkg.com", "https://assets.calendly.com", "https://*.cloudflare.com", "https://cdnjs.cloudflare.com"],
      styleSrc: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://assets.calendly.com", "https://fonts.googleapis.com", "https://cdnjs.cloudflare.com"],
      styleSrcElem: ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "https://fonts.googleapis.com", "https://assets.calendly.com"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https://unpkg.com", "https://cdn.jsdelivr.net", "https://*.cloudflare.com", "https://cdnjs.cloudflare.com", "https://assets.calendly.com"],
      fontSrc: ["'self'", "https://fonts.gstatic.com", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com"],
      scriptSrcAttr: ["'unsafe-inline'"],
      objectSrc: ["'none'"],
      frameSrc: ["https://calendly.com"],
      upgradeInsecureRequests: [],
    }
  },
}));

// Data sanitization against XSS
app.use(xss());

// Prevent HTTP parameter pollution
app.use(hpp());

// Middleware
// rawBody is stored so Calendly webhook signatures can be verified
app.use(express.json({
  limit: '10kb',
  verify: (req, _res, buf) => { req.rawBody = buf; }
})); // Body limit to prevent DOS
app.use(express.urlencoded({ extended: true, limit: '10kb' }));
app.use('/admin', adminAuth);
app.use(express.static('public'));

// Admin basic-auth middleware (protect admin pages)
function adminAuth(req, res, next) {
  // Require environment vars ADMIN_USER and ADMIN_PASS to be set
  const adminUser = process.env.ADMIN_USER;
  const adminPass = process.env.ADMIN_PASS;

  if (!adminUser || !adminPass) {
    // If not configured, deny access to admin routes
    return res.status(503).send('Admin authentication not configured');
  }

  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Basic ')) {
    res.set('WWW-Authenticate', 'Basic realm="5Cypress Admin"');
    return res.status(401).send('Authentication required');
  }

  const base64 = authHeader.split(' ')[1];
  const creds = Buffer.from(base64, 'base64').toString('utf8');
  const [user, pass] = creds.split(':');

  if (user === adminUser && pass === adminPass) {
    return next();
  }

  res.set('WWW-Authenticate', 'Basic realm="5Cypress Admin"');
  return res.status(401).send('Invalid credentials');
}

// Structured Logging (Morgan)
app.use(morgan(':remote-addr - :remote-user [:date[clf]] ":method :url HTTP/:http-version" :status :res[content-length] ":referrer" ":user-agent" - :response-time ms'));


// In-memory storage for demo
let orders = [];
let clients = [];

// Work items storage (for operations dashboard)
let workItems = [];
let workItemCounter = 0;

function getMarketingBasePath() {
  return process.env.MARKETING_TEAM_PATH || path.join(__dirname, 'marketing-team');
}

function getClientsConfigPath() {
  const marketingBase = getMarketingBasePath();
  const marketingConfigPath = path.join(marketingBase, 'config', 'clients.json');

  if (fs.existsSync(marketingConfigPath)) {
    return marketingConfigPath;
  }

  return path.join(__dirname, 'config', 'clients.json');
}

// Routes - Pages
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/dashboard', (req, res) => {
  res.redirect('/skills-dashboard.html');
});

app.get('/form', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'form.html'));
});

app.get('/operations', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'operations.html'));
});

app.get('/seo-dashboard', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'seo-dashboard.html'));
});

app.get('/marketing', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'marketing-dashboard.html'));
});

// SEO Config Endpoint - tells frontend what features are enabled
app.get('/api/seo/config', (req, res) => {
  const adminUser = process.env.ADMIN_USER;
  const adminPass = process.env.ADMIN_PASS;
  let isAdmin = false;

  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Basic ') && adminUser && adminPass) {
    const base64 = authHeader.split(' ')[1];
    const creds = Buffer.from(base64, 'base64').toString('utf8');
    const [user, pass] = creds.split(':');
    if (user === adminUser && pass === adminPass) isAdmin = true;
  }

  res.json({
    stripe_enabled: !!(stripe && process.env.STRIPE_SECRET_KEY),
    is_admin: isAdmin,
    dataforseo_enabled: !!(process.env.DATAFORSEO_USERNAME && process.env.DATAFORSEO_PASSWORD),
    pagespeed_enabled: !!process.env.GOOGLE_PAGESPEED_API_KEY,
    calendly_url: process.env.CALENDLY_URL || 'https://calendly.com/jimmy-5cypress/30min',
    brand: '5 Cypress Automation'
  });
});

app.get('/preview-work-item', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'preview-work-item.html'));
});

app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'ok',
    service: '5cypress-admin-api',
    timestamp: new Date().toISOString()
  });
});

app.get('/admin', adminAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin', 'index.html'));
});

app.get('/admin/clients', adminAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin', 'clients.html'));
});

app.get('/admin/seo', adminAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin', 'seo.html'));
});

app.get('/admin/marketing', adminAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin', 'marketing.html'));
});

app.get('/admin/leads', adminAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin', 'leads.html'));
});

// Admin-only: New client intake form (GET)
app.get('/admin/newclient', adminAuth, (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin', 'newclient-form.html'));
});

// Admin-only: Create client scaffold files (POST)
app.post('/admin/newclient', adminAuth, [
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
], (req, res) => {
  const fs = require('fs');

  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const {
    company_name, website, industry, contact_name, contact_email,
    what_they_sell, who_they_sell_to, main_goal,
    services, automations, contract_start, bio
  } = req.body;

  const todayStr = new Date().toISOString().split('T')[0];
  const clientId = company_name.toLowerCase().replace(/[^a-z0-9\s-]/g, '').trim().replace(/\s+/g, '-');

  // Resolve marketing team path (override with MARKETING_TEAM_PATH env var if needed)
  const marketingBase = getMarketingBasePath();

  const configDir   = path.join(marketingBase, 'config');
  const contextDir  = path.join(marketingBase, 'context');
  const clientsDir  = path.join(marketingBase, 'clients', clientId);
  const outputDir   = path.join(marketingBase, 'output', clientId);
  const meetingsDir = path.join(clientsDir, 'meetings');
  const assetsDir   = path.join(clientsDir, 'assets');

  // Reject path traversal attempts
  const safeDirs = [configDir, contextDir, clientsDir, outputDir, meetingsDir, assetsDir];
  for (const d of safeDirs) {
    if (!d.startsWith(marketingBase)) {
      return res.status(400).json({ error: 'Invalid client ID — path traversal detected' });
    }
  }

  const serviceList = (services || '').split(',').map(s => s.trim()).filter(Boolean);
  const autoList    = (automations || '').split(',').map(s => s.trim()).filter(Boolean);

  // ----- Build file contents -----

  const jsonEntry = {
    id: clientId,
    name: company_name,
    status: 'active',
    industry,
    contact_name,
    contact_email: contact_email || '(TBD)',
    website: website || '(TBD)',
    onboarded: todayStr,
    contract_start: contract_start || todayStr,
    billing_cycle: 'monthly',
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
**Status:** active
**Primary Contact:** ${contact_name}

---

## Work Log

| Date | Deliverable | Skill/Workflow Used | File Location | Notes |
|------|------------|-------------------|--------------|-------|
| ${todayStr} | Client onboarded | /newclient | context/${clientId}.md | Initial setup |

---

## Meeting Notes

*(Add meeting notes here)*

---

## Client Preferences & Standing Instructions

*(Fill in as learned)*

---

## Campaign Performance

| Campaign | Launch Date | Type | Primary Metric | Result | Notes |
|----------|------------|------|---------------|--------|-------|
| | | | | | |
`;

  const automationsMd = `# Automation Tracker: ${company_name}
**ID:** ${clientId}
**Last Updated:** ${todayStr}

---

## Active Automations

| ID | Automation Name | Type | Status | Created | Tools | Notes |
|----|----------------|------|--------|---------|-------|-------|
| — | None yet | — | — | — | — | — |

### Status Key
- 🟢 **Live** — Running in production
- 🟡 **In Progress** — Being built or tested
- 🔵 **Proposed** — Scoped, not started
- 🔴 **Paused** — Built but not running
- ⚫ **Retired** — No longer in use

---

## Proposed Automations
${autoList.length ? autoList.map(a => `- ${a}`).join('\n') : '- None yet'}

---

## Integration Map

| Tool / API | Purpose | Auth Method | Status | Notes |
|------------|---------|------------|--------|-------|
| | | | | |

---

## Monthly Health Check

| Month | Automations Running | Errors | Fixes Applied | Notes |
|-------|-------------------|--------|--------------|-------|
| | | | | |
`;

  // ----- Write files -----
  try {
    // Ensure all directories exist
    [configDir, contextDir, clientsDir, outputDir, meetingsDir, assetsDir].forEach(d => {
      fs.mkdirSync(d, { recursive: true });
    });

    // Update (or create) config/clients.json
    const clientsJsonPath = path.join(configDir, 'clients.json');
    let clientsList = { agency: '5 Cypress Automation', last_updated: todayStr, clients: [] };
    if (fs.existsSync(clientsJsonPath)) {
      try { clientsList = JSON.parse(fs.readFileSync(clientsJsonPath, 'utf8')); } catch (_) {}
    }
    // Remove existing entry with same id then push updated
    clientsList.clients = clientsList.clients.filter(c => c.id !== clientId);
    clientsList.clients.push(jsonEntry);
    clientsList.last_updated = todayStr;
    fs.writeFileSync(clientsJsonPath, JSON.stringify(clientsList, null, 2), 'utf8');

    // Write context file
    fs.writeFileSync(path.join(contextDir, `${clientId}.md`), contextMd, 'utf8');

    // Write history + automations
    fs.writeFileSync(path.join(clientsDir, 'history.md'), historyMd, 'utf8');
    fs.writeFileSync(path.join(clientsDir, 'automations.md'), automationsMd, 'utf8');

    console.log(`[ADMIN] New client scaffolded: ${clientId} (${company_name})`);

    res.json({
      success: true,
      clientId,
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
});

// Client Dashboard Routes
app.get('/clients/remy-lasers', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'client-remy-lasers.html'));
});

app.get('/clients/remy-lasers/prototypes/roi-calculator', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'client-remy-lasers-roi.html'));
});

app.get('/clients/remy-lasers/prototypes/qbo-invoice', (req, res) => {
  res.sendFile(path.join(__dirname, 'clients', 'remy-lasers', 'prototypes', 'qbo-invoice-preview.html'));
});

app.get('/clients/remy-lasers/prototypes/shipping-label', (req, res) => {
  res.sendFile(path.join(__dirname, 'clients', 'remy-lasers', 'prototypes', 'shipping-label-preview.html'));
});

app.get('/clients/remy-lasers/prototypes/calendar-dashboard', (req, res) => {
  res.sendFile(path.join(__dirname, 'clients', 'remy-lasers', 'prototypes', 'calendar-dashboard-preview.html'));
});

// Specific document routes must come before wildcard route
app.get('/clients/remy-lasers/documents/presentation', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'client-remy-lasers-presentation.html'));
});

// Wildcard route for other documents (comes last)
app.get('/clients/remy-lasers/documents/:docType', (req, res) => {
  const docType = req.params.docType;
  res.send(`Document viewer for: ${docType} - Coming soon! (Working on proposal and technical plan viewers)`);
});

app.get('/clients/:clientSlug', (req, res) => {
  const clientSlug = req.params.clientSlug;
  const clientFile = path.join(__dirname, 'public', `client-${clientSlug}.html`);
  
  // Check if client dashboard exists
  const fs = require('fs');
  if (fs.existsSync(clientFile)) {
    res.sendFile(clientFile);
  } else {
    res.status(404).send(`Client dashboard not found for: ${clientSlug}`);
  }
});

// API Routes
app.get('/api/dashboard', (req, res) => {
  const clients = db.prepare('SELECT * FROM clients').all();
  const orders = db.prepare('SELECT * FROM orders').all();

  const activeCount = clients.filter(c => c.status === 'active').length;
  const proposalCount = clients.filter(c => c.status === 'proposal').length;
  const totalPipeline = clients.reduce((sum, c) => sum + c.dealValue, 0);
  
  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  const oneWeekAgoStr = oneWeekAgo.toISOString().split('T')[0];

  const thisWeekOrders = orders.filter(o => o.date >= oneWeekAgoStr).length;
  const todayStr = new Date().toISOString().split('T')[0];

  res.json({
    summary: {
      activeClients: activeCount,
      proposals: proposalCount,
      pipelineValue: totalPipeline,
      thisWeekOrders: thisWeekOrders,
      todayOrders: orders.filter(o => o.date === todayStr).length
    },
    recentOrders: orders.slice(-5).reverse(),
    clients: clients
  });
});

app.get('/api/orders', (req, res) => {
  const orders = db.prepare('SELECT * FROM orders ORDER BY createdAt DESC').all();
  res.json(orders);
});

app.post('/api/orders', [
  body('customerName').trim().notEmpty().withMessage('Name is required').isLength({ max: 100 }),
  body('customerEmail').isEmail().withMessage('Valid email is required').normalizeEmail(),
  body('productName').trim().notEmpty().withMessage('Product is required'),
  body('quantity').isInt({ min: 1 }).withMessage('Quantity must be at least 1'),
  body('utm_source').optional().trim().escape(),
  body('utm_medium').optional().trim().escape(),
  body('utm_campaign').optional().trim().escape()
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { customerName, customerEmail, date, salesRep, orderType, productName, quantity, utm_source, utm_medium, utm_campaign } = req.body;

  const stmt = db.prepare(`
    INSERT INTO orders (customerName, customerEmail, date, salesRep, orderType, productName, quantity, status, utm_source, utm_medium, utm_campaign)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `);
  
  const info = stmt.run(customerName, customerEmail, date, salesRep, orderType, productName, parseInt(quantity), 'pending', utm_source || null, utm_medium || null, utm_campaign || null);
  const invoiceId = `INV-${info.lastInsertRowid}`;
  const shipmentId = `SHIP-${info.lastInsertRowid}`;

  const newOrder = {
    id: info.lastInsertRowid,
    customerName,
    customerEmail,
    date,
    salesRep,
    orderType,
    productName,
    quantity: parseInt(quantity),
    status: 'pending',
    createdAt: new Date(),
    invoiceId,
    shipmentId
  };

  res.json({
    success: true,
    message: 'Order submitted successfully',
    order: newOrder,
    automation: {
      qboInvoice: `Created invoice ${invoiceId}`,
      shipstationOrder: `Created shipment ${shipmentId}`,
      emailSent: `Confirmation sent to ${customerEmail}`
    }
  });
});

// Work Items API
app.get('/api/work-items', (req, res) => {
  const { status, client, type } = req.query;
  let filtered = [...workItems];

  if (status) filtered = filtered.filter(w => w.status === status);
  if (client) filtered = filtered.filter(w => w.client_slug === client);
  if (type) filtered = filtered.filter(w => w.type === type);

  // Sort by due_date and priority
  filtered.sort((a, b) => {
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    if (a.priority !== b.priority) {
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    }
    return new Date(a.due_date) - new Date(b.due_date);
  });

  res.json(filtered);
});

app.post('/api/work-items', (req, res) => {
  const { type, client_slug, description } = req.body;

  if (!type || !client_slug || !description) {
    return res.status(400).json({ error: 'Missing required fields: type, client_slug, description' });
  }

  // Calculate due date based on type
  const dueDateMap = {
    new_lead: 2,
    schedule_discovery_call: 1,
    create_proposal: 5,
    send_contract: 7,
    onboard_client: 1,
    modify_workflow: 3,
    create_invoice: 0,
    send_payment_reminder: 0,
    log_payment_received: 0,
    send_email: 0,
    add_workflow: 0,
    generate_sow: 7,
    resolve_integration_issue: 0,
    handle_alert: 0
  };

  const daysToAdd = dueDateMap[type] || 0;
  const dueDate = new Date();
  dueDate.setDate(dueDate.getDate() + daysToAdd);

  workItemCounter++;
  const workItemId = `WI-${String(workItemCounter).padStart(3, '0')}`;

  const newWorkItem = {
    id: workItemId,
    type,
    client_slug,
    description,
    status: 'pending',
    created_at: new Date().toISOString(),
    due_date: dueDate.toISOString().split('T')[0],
    priority: 'medium',
    context: {},
    preview_generated: false,
    execution: {
      script: null,
      status: 'pending',
      result: null
    }
  };

  workItems.push(newWorkItem);

  res.json({
    success: true,
    workItem: newWorkItem
  });
});

app.get('/api/work-items/:id', (req, res) => {
  const workItem = workItems.find(w => w.id === req.params.id);

  if (!workItem) {
    return res.status(404).json({ error: 'Work item not found' });
  }

  // Get client info for preview
  const client = clients.find(c => c.slug === workItem.client_slug);

  res.json({
    workItem,
    client,
    preview: generatePreview(workItem, client)
  });
});

app.post('/api/work-items/:id/execute', (req, res) => {
  const workItem = workItems.find(w => w.id === req.params.id);

  if (!workItem) {
    return res.status(404).json({ error: 'Work item not found' });
  }

  // Mark as executing
  workItem.status = 'executing';
  workItem.execution.status = 'running';

  // Route to correct script (simulated for now, will call Python scripts later)
  const scriptMap = {
    new_lead: 'create_client.py',
    schedule_discovery_call: 'create_calendar_link.py',
    create_proposal: 'create_proposal.py',
    send_contract: 'send_contract.py',
    onboard_client: 'onboard_client.py',
    modify_workflow: 'log_activity.py',
    create_invoice: 'create_invoice.py',
    send_payment_reminder: 'send_email.py',
    log_payment_received: 'update_client.py',
    send_email: 'send_email.py',
    add_workflow: 'add_workflow.py',
    generate_sow: 'create_document.py',
    resolve_integration_issue: 'debug_integration.py',
    handle_alert: 'monitor_recovery.py'
  };

  workItem.execution.script = scriptMap[workItem.type] || 'unknown.py';
  workItem.execution.status = 'completed';

  // Simulate artifacts based on type
  const artifacts = {};
  if (workItem.type === 'create_proposal') {
    artifacts.google_doc_url = 'https://docs.google.com/document/d/example';
    artifacts.pdf_path = `/clients/${workItem.client_slug}/proposals/proposal-${Date.now()}.pdf`;
  } else if (workItem.type === 'create_invoice') {
    artifacts.invoice_number = `INV-${new Date().toISOString().split('T')[0].replace(/-/g, '')}-001`;
    artifacts.invoice_path = `/clients/${workItem.client_slug}/invoices/invoice-${Date.now()}.pdf`;
  } else if (workItem.type === 'send_email') {
    artifacts.email_sent_to = clients.find(c => c.slug === workItem.client_slug)?.name || 'client';
    artifacts.timestamp = new Date().toISOString();
  }

  workItem.status = 'completed';
  workItem.execution.result = {
    success: true,
    artifacts,
    completed_at: new Date().toISOString()
  };

  res.json({
    success: true,
    workItem
  });
});

app.get('/admin/api/clients', adminAuth, (req, res) => {
  try {
    const clientsPath = getClientsConfigPath();

    if (!fs.existsSync(clientsPath)) {
      return res.status(404).json({ error: 'clients.json not found' });
    }

    const raw = fs.readFileSync(clientsPath, 'utf8');
    const parsed = JSON.parse(raw);
    const data = Array.isArray(parsed?.clients) ? parsed.clients : [];

    return res.json({
      source: clientsPath,
      count: data.length,
      clients: data
    });
  } catch (error) {
    console.error('[ADMIN] Failed to load clients list:', error);
    return res.status(500).json({ error: 'Failed to load clients', detail: error.message });
  }
});

app.get('/admin/api/seo-audit', adminAuth, async (req, res) => {
  try {
    const target = String(req.query.url || '').trim();
    const strategy = String(req.query.strategy || 'mobile').trim().toLowerCase();
    const apiKey = process.env.GOOGLE_PAGESPEED_API_KEY;

    if (!apiKey) {
      return res.status(503).json({ error: 'GOOGLE_PAGESPEED_API_KEY is not configured' });
    }

    if (!target) {
      return res.status(400).json({ error: 'Missing required query param: url' });
    }

    const normalizedStrategy = strategy === 'desktop' ? 'desktop' : 'mobile';
    const normalizedUrl = /^https?:\/\//i.test(target) ? target : `https://${target}`;

    let validated;
    try {
      validated = new URL(normalizedUrl);
    } catch (_) {
      return res.status(400).json({ error: 'Invalid URL provided' });
    }

    const endpoint = new URL('https://www.googleapis.com/pagespeedonline/v5/runPagespeed');
    endpoint.searchParams.set('url', validated.toString());
    endpoint.searchParams.set('strategy', normalizedStrategy);
    endpoint.searchParams.set('key', apiKey);
    endpoint.searchParams.set('category', 'performance');
    endpoint.searchParams.set('category', 'accessibility');
    endpoint.searchParams.set('category', 'best-practices');
    endpoint.searchParams.set('category', 'seo');

    const response = await fetch(endpoint.toString(), {
      method: 'GET',
      headers: { Accept: 'application/json' }
    });

    const payload = await response.json();

    if (!response.ok) {
      return res.status(response.status).json({
        error: 'PageSpeed request failed',
        detail: payload?.error?.message || 'Unknown API error',
        raw: payload
      });
    }

    const categories = payload?.lighthouseResult?.categories || {};
    const audits = payload?.lighthouseResult?.audits || {};
    const loadingExperience = payload?.loadingExperience?.metrics || {};

    return res.json({
      fetchedAt: new Date().toISOString(),
      requested: {
        url: validated.toString(),
        strategy: normalizedStrategy
      },
      scores: {
        performance: categories.performance?.score ?? null,
        accessibility: categories.accessibility?.score ?? null,
        bestPractices: categories['best-practices']?.score ?? null,
        seo: categories.seo?.score ?? null
      },
      vitals: {
        lcp: audits['largest-contentful-paint']?.displayValue || null,
        cls: audits['cumulative-layout-shift']?.displayValue || null,
        inp: audits['interaction-to-next-paint']?.displayValue || null,
        fcp: audits['first-contentful-paint']?.displayValue || null,
        ttfb: audits['server-response-time']?.displayValue || null
      },
      fieldData: {
        lcp: loadingExperience.LARGEST_CONTENTFUL_PAINT_MS?.percentile || null,
        cls: loadingExperience.CUMULATIVE_LAYOUT_SHIFT_SCORE?.percentile || null,
        inp: loadingExperience.INTERACTION_TO_NEXT_PAINT?.percentile || null,
        fcp: loadingExperience.FIRST_CONTENTFUL_PAINT_MS?.percentile || null
      },
      lighthouseLink: payload?.lighthouseResult?.finalDisplayedUrl || validated.toString()
    });
  } catch (error) {
    console.error('[ADMIN] SEO audit endpoint failed:', error);
    return res.status(500).json({ error: 'Failed to run SEO audit', detail: error.message });
  }
});

// Admin Pipeline Action API
app.post('/admin/api/pipeline-action', adminAuth, (req, res) => {
  const { action, id, data } = req.body;
  console.log(`Received pipeline action: ${action} for ${id}`);
  res.json({
    success: true,
    message: `Action ${action} processed successfully for ${id}`,
    timestamp: new Date().toISOString()
  });
});

// Admin: Recent leads from DB
app.get('/admin/api/leads', adminAuth, (req, res) => {
  try {
    const limit = Math.min(parseInt(req.query.limit) || 50, 200);
    const leads = db.prepare(`SELECT * FROM leads ORDER BY createdAt DESC LIMIT ?`).all(limit);
    const total = db.prepare(`SELECT COUNT(*) as count FROM leads`).get().count;
    res.json({ total, leads });
  } catch (err) {
    console.error('[ADMIN] Leads query failed:', err.message);
    res.status(500).json({ error: 'Failed to load leads', detail: err.message });
  }
});

// Admin: Dashboard summary stats
app.get('/admin/api/stats', adminAuth, (req, res) => {
  try {
    const leadCount  = db.prepare(`SELECT COUNT(*) as c FROM leads`).get().c;
    const clientCount = db.prepare(`SELECT COUNT(*) as c FROM clients`).get().c;
    const auditCount = db.prepare(`SELECT COUNT(*) as c FROM seo_audits`).get().c;
    const newLeads   = db.prepare(`SELECT COUNT(*) as c FROM leads WHERE createdAt >= datetime('now','-7 days')`).get().c;
    res.json({ leadCount, clientCount, auditCount, newLeads, serverTime: new Date().toISOString() });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Admin: Marketing team clients + output listing
app.get('/admin/api/marketing', adminAuth, (req, res) => {
  try {
    const mktgPath = process.env.MARKETING_TEAM_PATH || path.join(__dirname, 'marketing-team');
    const contextDir  = path.join(mktgPath, 'context');
    const outputDir   = path.join(mktgPath, 'output');

    const clients = [];
    if (fs.existsSync(contextDir)) {
      fs.readdirSync(contextDir).filter(f => f.endsWith('.md') && f !== 'agency.md' && f !== 'client-template.md').forEach(file => {
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

// Admin: Serve a marketing output file (HTML preview)
app.get('/admin/api/marketing/file', adminAuth, (req, res) => {
  try {
    const mktgPath = process.env.MARKETING_TEAM_PATH || path.join(__dirname, 'marketing-team');
    const { client, file } = req.query;
    if (!client || !file) return res.status(400).json({ error: 'client and file params required' });
    // Sanitize to prevent path traversal
    const safeClient = path.basename(client);
    const safeFile   = path.basename(file);
    const filePath   = path.join(mktgPath, 'output', safeClient, safeFile);
    if (!fs.existsSync(filePath)) return res.status(404).json({ error: 'File not found' });
    res.sendFile(filePath);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Helper function to generate preview data
function generatePreview(workItem, client) {
  const previews = {
    new_lead: {
      directive: 'Capture prospect information and schedule initial discovery call',
      template: 'Discovery call scheduling email',
      execution: 'Creates client folder + sends calendar link'
    },
    schedule_discovery_call: {
      directive: 'Schedule systematic discovery call with prospect',
      template: 'Calendar link + reminder email',
      execution: 'Generates scheduling link + sends email'
    },
    create_proposal: {
      directive: 'Generate professional proposal from discovery notes',
      template: 'Proposal template with pricing',
      execution: 'Loads discovery data + creates Google Doc + exports PDF + sends email'
    },
    send_contract: {
      directive: 'Route MSA/SOW/NDA to e-signature',
      template: 'Choose MSA, SOW, or NDA',
      execution: 'Generates contract document + sends to DocuSign'
    },
    onboard_client: {
      directive: 'Send welcome email and schedule kickoff call',
      template: 'Kickoff call scheduling email',
      execution: 'Sends welcome email + generates calendar link'
    },
    modify_workflow: {
      directive: 'Document new feature/modification request',
      template: 'Follow-up discovery questions',
      execution: 'Captures scope + schedules follow-up call'
    },
    create_invoice: {
      directive: 'Generate invoice with payment links',
      template: 'Invoice template with Stripe/PayPal links',
      execution: 'Creates invoice + generates PDF + sends email'
    },
    send_payment_reminder: {
      directive: 'Send payment reminder for overdue invoice',
      template: 'Payment reminder email',
      execution: 'Sends reminder + updates invoice status'
    },
    send_email: {
      directive: 'Send templated email to client',
      template: 'Template picker (8 available)',
      execution: 'Loads template + sends to client email'
    },
    add_workflow: {
      directive: 'Document new automation/workflow',
      template: 'Workflow README template',
      execution: 'Creates workflow folder + documents process'
    },
    generate_sow: {
      directive: 'Create custom statement of work',
      template: 'SOW with deliverables + timeline',
      execution: 'Generates SOW document + stores in client folder'
    },
    resolve_integration_issue: {
      directive: 'Handle integration failures (QB, ShipStation, webhook)',
      template: 'Debug playbook',
      execution: 'Runs auto-recovery script or escalates'
    },
    handle_alert: {
      directive: 'Respond to monitoring alerts',
      template: 'Alert context + recovery steps',
      execution: 'Auto-retry or routes to manual investigation'
    }
  };

  return previews[workItem.type] || { directive: 'Unknown', template: 'None', execution: 'Custom' };
}

// Lead capture from Calendly
let leads = [];

app.post('/api/lead-capture', (req, res) => {
  const { email, name, source, service } = req.body;

  // Validate required fields
  if (!email || !name) {
    return res.status(400).json({ error: 'Missing required fields: email, name' });
  }

  // Create lead object
  const lead = {
    id: leads.length + 1,
    email: email.toLowerCase(),
    name: name,
    source: source || 'calendly',
    service: service || 'general',
    status: 'new',
    createdAt: new Date().toISOString(),
    followUpDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString() // 24 hours from now
  };

  // Store lead
  leads.push(lead);

  // Log for demo purposes
  console.log(`
╔════════════════════════════════════════════╗
║   🎯 NEW LEAD CAPTURED                     ║
╠════════════════════════════════════════════╣
║  Name: ${lead.name.padEnd(34)}║
║  Email: ${lead.email.padEnd(33)}║
║  Service: ${(lead.service || 'General').padEnd(30)}║
║  Source: ${(lead.source || 'Direct').padEnd(31)}║
║  Time: ${new Date().toLocaleString().padEnd(28)}║
╚════════════════════════════════════════════╝
  `);

  // TODO: Send email notification
  // TODO: Add to CRM (Pipedrive, HubSpot, etc)
  // TODO: Create follow-up task
  
  res.status(201).json({
    success: true,
    message: 'Lead captured successfully',
    lead: lead
  });
});

// Get all leads (admin — requires auth)
app.get('/api/leads', adminAuth, (req, res) => {
  res.json(leads);
});

// ─── Calendly Webhook ────────────────────────────────────────────────────────
/**
 * Verify Calendly webhook signature.
 * Header format: "t=<timestamp>,v1=<hex_hmac>"
 * Signed payload:  "<timestamp>.<raw_body_string>"
 */
function verifyCalendlySignature(req) {
  const signingKey = process.env.CALENDLY_WEBHOOK_SIGNING_KEY;
  if (!signingKey) {
    console.warn('[Calendly] CALENDLY_WEBHOOK_SIGNING_KEY not set — skipping signature check (dev mode)');
    return true;
  }
  const header = req.headers['calendly-webhook-signature'];
  if (!header) return false;

  // Parse "t=<ts>,v1=<sig>" into { t, v1 }
  const parts = {};
  header.split(',').forEach(part => {
    const idx = part.indexOf('=');
    if (idx > -1) parts[part.substring(0, idx)] = part.substring(idx + 1);
  });

  if (!parts.t || !parts.v1) return false;

  const rawBody = req.rawBody ? req.rawBody.toString('utf8') : '{}';
  const signed = `${parts.t}.${rawBody}`;
  const expected = crypto.createHmac('sha256', signingKey).update(signed).digest('hex');

  try {
    return crypto.timingSafeEqual(Buffer.from(parts.v1, 'hex'), Buffer.from(expected, 'hex'));
  } catch {
    return false; // Buffers of different length
  }
}

app.post('/api/webhooks/calendly', async (req, res) => {
  // 1. Verify signature
  if (!verifyCalendlySignature(req)) {
    console.warn('[Calendly] Invalid webhook signature – request rejected');
    return res.status(403).json({ error: 'Invalid signature' });
  }

  const event = req.body;
  const eventType = event?.event;
  const invitee = event?.payload?.invitee;
  const eventDetails = event?.payload?.event;

  if (!eventType) {
    return res.status(400).json({ error: 'Missing event type' });
  }

  console.log(`[Calendly] Webhook received: ${eventType}`);

  // ── invitee.created → new booking ──────────────────────────────────────
  if (eventType === 'invitee.created' && invitee) {
    const lead = {
      id: leads.length + 1,
      name: invitee.name || 'Unknown',
      email: (invitee.email || '').toLowerCase(),
      source: 'calendly_webhook',
      service: 'discovery_call',
      status: 'booked',
      calendlyEventUri: eventDetails?.uri || null,
      startTime: eventDetails?.start_time || null,
      timezone: invitee.timezone || null,
      createdAt: new Date().toISOString(),
      followUpDate: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
    };

    leads.push(lead);

    const startFormatted = lead.startTime
      ? new Date(lead.startTime).toLocaleString('en-US', {
          timeZone: 'America/Chicago',
          dateStyle: 'full',
          timeStyle: 'short'
        })
      : 'See Calendly';

    console.log(`
╔════════════════════════════════════════════╗
║   📅 CALENDLY BOOKING RECEIVED             ║
╠════════════════════════════════════════════╣
║  Name:  ${lead.name.substring(0, 34).padEnd(34)}║
║  Email: ${lead.email.substring(0, 33).padEnd(33)}║
║  Time:  ${startFormatted.substring(0, 33).padEnd(33)}║
╚════════════════════════════════════════════╝`);

    // Send internal notification email via Resend
    if (process.env.RESEND_API_KEY) {
      try {
        const { Resend } = require('resend');
        const resend = new Resend(process.env.RESEND_API_KEY);
        await resend.emails.send({
          from: `5 Cypress <${process.env.DEFAULT_FROM || 'nick@5cypress.com'}>`,
          to: 'nick@5cypress.com',
          subject: `📅 New Discovery Call: ${lead.name}`,
          html: `
            <div style="font-family:sans-serif;max-width:560px;margin:auto">
              <h2 style="color:#5d8c5d">New Discovery Call Booked</h2>
              <table style="width:100%;border-collapse:collapse">
                <tr><td style="padding:8px;color:#666"><strong>Name</strong></td><td style="padding:8px">${lead.name}</td></tr>
                <tr><td style="padding:8px;color:#666"><strong>Email</strong></td><td style="padding:8px"><a href="mailto:${lead.email}">${lead.email}</a></td></tr>
                <tr><td style="padding:8px;color:#666"><strong>Meeting time</strong></td><td style="padding:8px">${startFormatted} (CT)</td></tr>
                ${lead.calendlyEventUri ? `<tr><td style="padding:8px;color:#666"><strong>Calendly link</strong></td><td style="padding:8px"><a href="${lead.calendlyEventUri}">${lead.calendlyEventUri}</a></td></tr>` : ''}
              </table>
              <hr/>
              <p style="color:#999;font-size:0.8em">Sent automatically by the 5 Cypress booking system.</p>
            </div>
          `
        });
        console.log('[Calendly] Notification email sent → nick@5cypress.com');
      } catch (emailErr) {
        console.error('[Calendly] Failed to send notification email:', emailErr.message);
      }
    }
  }

  // ── invitee.canceled → mark lead canceled ──────────────────────────────
  if (eventType === 'invitee.canceled' && invitee) {
    const existing = leads.find(
      l => l.email === (invitee.email || '').toLowerCase() && l.status === 'booked'
    );
    if (existing) {
      existing.status = 'canceled';
      console.log(`[Calendly] Lead ${existing.email} marked as canceled`);
    }
  }

  res.status(200).json({ received: true, event: eventType });
});
// ─────────────────────────────────────────────────────────────────────────────

// SEO Analysis API
app.post('/api/seo/analyze', async (req, res) => {
  const { website_url, keywords, modules, competitors } = req.body;
  
  if (!website_url) {
    return res.status(400).json({ error: 'Missing website_url parameter' });
  }
  
  // Validate URL format
  try {
    new URL(website_url.startsWith('http') ? website_url : 'https://' + website_url);
  } catch (e) {
    return res.status(400).json({ error: 'Invalid URL format' });
  }
  
  const { spawn } = require('child_process');
  const fs = require('fs');
  const path = require('path');
  
  // Create output path
  const outputDir = path.join(__dirname, '.tmp', 'seo_reports');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  const domain = new URL(website_url.startsWith('http') ? website_url : 'https://' + website_url).hostname.replace(/[^a-z0-9]/gi, '-');
  const outputPath = path.join(outputDir, `${domain}.json`);
  
  console.log(`Starting SEO analysis for ${website_url} with modules: ${modules}`);
  
  // Spawn Python process - upgraded to DataForSEO runner
  const pythonArgs = [
    path.join(__dirname, 'execution', 'seo_audit_runner.py'),
    '--website-url', website_url,
    '--keywords', keywords ? (Array.isArray(keywords) ? keywords.join(',') : keywords) : '',
    '--modules', modules ? (Array.isArray(modules) ? modules.join(',') : modules) : 'on_page',
    '--competitors', competitors ? (Array.isArray(competitors) ? competitors.join(',') : competitors) : '',
    '--output', outputPath
  ];

  const pythonProcess = spawn('python', pythonArgs);
  
  let stdout = '';
  let stderr = '';
  
  pythonProcess.stdout.on('data', (data) => {
    stdout += data.toString();
    console.log(`SEO: ${data.toString().trim()}`);
  });
  
  pythonProcess.stderr.on('data', (data) => {
    stderr += data.toString();
    console.error(`SEO Error: ${data.toString().trim()}`);
  });
  
  pythonProcess.on('close', (code) => {
    if (code !== 0) {
      console.error(`SEO analysis failed with code ${code}`);
      return res.status(500).json({
        error: 'SEO analysis failed',
        details: stderr || 'Unknown error'
      });
    }
    
    // Read and return results
    try {
      const reportData = fs.readFileSync(outputPath, 'utf8');
      const report = JSON.parse(reportData);
      
      // Cache in database
      try {
        const checkExists = db.prepare('SELECT id FROM seo_audits WHERE domain = ? AND status = "pending"').get(domain);
        if (checkExists) {
          db.prepare('UPDATE seo_audits SET report_data = ? WHERE id = ?').run(reportData, checkExists.id);
        } else {
          db.prepare('INSERT INTO seo_audits (domain, report_data, status) VALUES (?, ?, "pending")').run(domain, reportData);
        }
      } catch (dbErr) {
        console.error('Database logging failed:', dbErr);
      }

      res.json(report);
    } catch (e) {
      console.error('Failed to read SEO report:', e);
      res.status(500).json({ error: 'Failed to read analysis results' });
    }
  });
  
  // Set timeout to prevent hanging (2 minutes)
  setTimeout(() => {
    pythonProcess.kill();
    res.status(504).json({ error: 'Analysis timeout - website may be too large or slow' });
  }, 120000);
});

// Admin: Free premium SEO report (no payment required)
app.get('/api/seo/admin/report/:domain', adminAuth, (req, res) => {
  const { domain } = req.params;
  const safeDomain = domain.replace(/[^a-z0-9-]/gi, '-');
  const reportPath = path.join(__dirname, '.tmp', 'seo_reports', `${safeDomain}.json`);

  if (!fs.existsSync(reportPath)) {
    return res.status(404).json({ error: 'No cached report found. Run /api/seo/analyze first.' });
  }

  try {
    const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
    res.json({ ...report, admin_access: true, payment_bypassed: true });
  } catch (e) {
    res.status(500).json({ error: 'Failed to read report' });
  }
});

// Stripe Checkout Session
app.post('/api/seo/create-checkout-session', async (req, res) => {
  const { domain, email } = req.body;

  if (!domain) {
    return res.status(400).json({ error: 'Domain is required' });
  }

  if (!stripe) {
    // Graceful fallback: return Calendly URL instead of error
    const calendlyUrl = process.env.CALENDLY_URL || 'https://calendly.com/jimmy-5cypress/30min';
    return res.status(402).json({
      error: 'stripe_not_configured',
      message: 'Premium report available via consultation. Book a free call instead.',
      fallback: 'calendly',
      calendly_url: calendlyUrl
    });
  }

  try {
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      customer_email: email,
      line_items: [
        {
          price_data: {
            currency: 'usd',
            product_data: {
              name: 'SEO Intelligence Audit - Premium Dossier',
              description: `Deep structural audit and vulnerability report for ${domain}`,
            },
            unit_amount: 5000, // $50.00
          },
          quantity: 1,
        },
      ],
      mode: 'payment',
      success_url: `${process.env.STRIPE_SUCCESS_URL || 'http://localhost:3000/seo-report.html'}?domain=${domain}&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${process.env.STRIPE_CANCEL_URL || 'http://localhost:3000/seo-dashboard.html'}`,
      metadata: {
        domain: domain,
        audit_type: 'premium_dossier'
      }
    });

    // Update the record with the session ID
    db.prepare('UPDATE seo_audits SET session_id = ?, email = ? WHERE domain = ? AND status = "pending"')
      .run(session.id, email, domain);

    res.json({ id: session.id, url: session.url });
  } catch (error) {
    console.error('Stripe error:', error);
    res.status(500).json({ error: 'Failed to create checkout session' });
  }
});

// Verify Payment and Retrieve Report
app.get('/api/seo/report/:sessionId', async (req, res) => {
  const { sessionId } = req.params;
  const { domain } = req.query;

  try {
    // Check if session is paid in Stripe
    const audit = db.prepare('SELECT * FROM seo_audits WHERE session_id = ?').get(sessionId);
    
    if (!audit) {
      return res.status(404).json({ error: 'Audit not found' });
    }

    if (audit.status !== 'paid') {
      if (!stripe) {
        return res.status(503).json({ error: 'Payment verification unavailable (Stripe not configured).' });
      }
      const session = await stripe.checkout.sessions.retrieve(sessionId);
      if (session.payment_status === 'paid') {
        db.prepare('UPDATE seo_audits SET status = "paid" WHERE session_id = ?').run(sessionId);
        audit.status = 'paid';
      }
    }

    if (audit.status === 'paid') {
      res.json(JSON.parse(audit.report_data));
    } else {
      res.status(402).json({ error: 'Payment required', status: audit.status });
    }
  } catch (error) {
    console.error('Verification error:', error);
    res.status(500).json({ error: 'Failed to verify payment or retrieve report' });
  }
});

// General Contact / Lead Capture API
app.post('/api/contact', [
  body('name').trim().notEmpty().isLength({ max: 150 }).escape(),
  body('email').isEmail().normalizeEmail(),
  body('website').optional({ checkFalsy: true }).trim().isLength({ max: 200 }),
  body('source').optional().trim().escape(),
  body('scanned_domain').optional().trim().isLength({ max: 200 }),
  body('challenge').optional().trim().isLength({ max: 2000 }),
  body('details').optional().trim().isLength({ max: 2000 }),
  body('company').optional().trim().isLength({ max: 200 }).escape(),
  body('timeline').optional().trim().escape(),
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { name, email, website, source, scanned_domain, challenge, details, company, timeline } = req.body;
  const timestamp = new Date().toISOString();

  // Log lead to database
  try {
    db.prepare(`
      INSERT INTO leads (name, email, company, website, source, scanned_domain, challenge, timeline)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      name,
      email,
      company || null,
      website || null,
      source || null,
      scanned_domain || null,
      (challenge || details) || null,
      timeline || null
    );
  } catch (dbErr) {
    console.error('Lead DB log failed (non-fatal):', dbErr.message);
  }

  console.log(`[LEAD] ${name} <${email}> from ${source || 'website'} @ ${timestamp}`);

  res.json({ success: true, message: 'Received. We\'ll be in touch within one business day.' });
});

// ─── Public Vetting / Inquiry Form ────────────────────────────────────────────
// Receives the modal contact form submitted from all public pages (dynamics.js → /submit-inquiry)
app.post('/submit-inquiry', [
  body('name').trim().notEmpty().isLength({ max: 150 }).escape(),
  body('email').isEmail().normalizeEmail(),
  body('company').optional({ checkFalsy: true }).trim().isLength({ max: 200 }).escape(),
  body('details').optional({ checkFalsy: true }).trim().isLength({ max: 2000 }),
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }

  const { name, email, company, details } = req.body;
  const timestamp = new Date().toISOString();

  try {
    db.prepare(`
      INSERT INTO leads (name, email, company, source, challenge)
      VALUES (?, ?, ?, ?, ?)
    `).run(name, email, company || null, 'website-inquiry', details || null);
  } catch (dbErr) {
    console.error('[INQUIRY] DB log failed (non-fatal):', dbErr.message);
  }

  console.log(`[INQUIRY] New inquiry from ${name} <${email}> @ ${timestamp}`);

  res.json({ success: true, message: "Application received. We'll be in touch within one business day." });
});

// Get cached SEO report
app.get('/api/seo/:domain', (req, res) => {
  const { domain } = req.params;
  const fs = require('fs');
  
  const reportPath = path.join(__dirname, '.tmp', 'seo_reports', `${domain}.json`);
  
  if (!fs.existsSync(reportPath)) {
    return res.status(404).json({ error: 'No analysis found for this domain' });
  }
  
  try {
    const reportData = fs.readFileSync(reportPath, 'utf8');
    const report = JSON.parse(reportData);
    res.json(report);
  } catch (e) {
    res.status(500).json({ error: 'Failed to read analysis report' });
  }
});

// Start server
const PORT = process.env.PORT || 3000;
const server = app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════════╗
║                                            ║
║       🌲  5 Cypress Automation  🌲         ║
║                                            ║
║   Agentic Automation for SMBs              ║
║                                            ║
║   🌐  http://localhost:${PORT}                ║
║   📊  http://localhost:${PORT}/dashboard      ║
║   🛠️   Loaded skills: Check /api/skills   ║
║                                            ║
║  Use Ctrl+C to stop the server             ║
║                                            ║
╚════════════════════════════════════════════╝
  `);
});


// === Skills API for Skills Dashboard ===
const skillsPath = path.join(__dirname, 'skills', 'skills.json');

app.get('/api/skills', (req, res) => {
  const fs = require('fs');
  if (!fs.existsSync(skillsPath)) {
    return res.status(404).json({ error: 'Skills config not found' });
  }
  const skills = JSON.parse(fs.readFileSync(skillsPath, 'utf8'));
  res.json(skills);
});

app.post('/api/skills/:id/run', adminAuth, (req, res) => {
  const fs = require('fs');
  if (!fs.existsSync(skillsPath)) {
    return res.status(404).json({ error: 'Skills config not found' });
  }
  const skills = JSON.parse(fs.readFileSync(skillsPath, 'utf8'));
  const skill = skills.find(s => s.id === req.params.id);
  if (!skill) return res.status(404).json({ error: 'Skill not found' });

  // Build command to run the script with arguments
  let cmd = `python execution/${skill.id}.py`;
  for (const input of (skill.inputs || [])) {
    const val = req.body[input.name] || '';
    if (val) {
      cmd += ` --${input.name} "${val.replace(/"/g, '\\"')}"`;
    }
  }

  console.log(`[SKILL RUN] ${skill.name}: ${cmd}`);

  exec(cmd, { timeout: 60000 }, (err, stdout, stderr) => {
    if (err) {
      console.error(`[SKILL ERROR] ${skill.name}:`, stderr);
      return res.status(500).json({ 
        error: stderr || err.message,
        skill: skill.name,
        tip: 'Check that the execution script exists and dependencies are installed.'
      });
    }
    console.log(`[SKILL OK] ${skill.name}`);
    res.json({ output: stdout, skill: skill.name });
  });
});

// ─── Catch-all: serve .html for clean/extensionless page URLs ───────────────
// Handles requests like /services, /about, /process, /case-studies, /booking
app.get('*', (req, res, next) => {
  // Skip API paths, admin paths, and paths that already have a file extension
  if (
    req.path.startsWith('/api/') ||
    req.path.startsWith('/admin/') ||
    path.extname(req.path)
  ) {
    return next();
  }

  const cleanPath = req.path.replace(/\/$/, '') || '/index';
  const htmlFile = path.join(__dirname, 'public', cleanPath + '.html');

  if (fs.existsSync(htmlFile)) {
    return res.sendFile(htmlFile);
  }

  // Nothing found — send the homepage rather than a bare Express 404
  res.status(404).sendFile(path.join(__dirname, 'public', 'index.html'));
});

server.on('error', (e) => {
  if (e.code === 'EADDRINUSE') {
    console.error(`Port ${PORT} is already in use. Retrying with a different port...`);
    setTimeout(() => {
      server.close();
      server.listen(0);
    }, 1000);
  } else {
    console.error('Server error:', e);
  }
});
