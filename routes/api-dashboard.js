/**
 * routes/api-dashboard.js
 * Orders, Work Items, and Dashboard summary endpoints.
 *
 * In-memory workItems store is kept here for now.
 * Orders are backed by SQLite via db (req.app.get('db')).
 */
const express = require('express');
const { body, validationResult } = require('express-validator');

const router = express.Router();

// ── Work items in-memory store ───────────────────────────────────────────────
const workItems = [];
let workItemCounter = 0;

// ── Dashboard summary ────────────────────────────────────────────────────────
router.get('/dashboard', (req, res) => {
  const db = req.app.get('db');
  const clients = db.prepare('SELECT * FROM clients').all();
  const orders  = db.prepare('SELECT * FROM orders').all();

  const activeCount   = clients.filter(c => c.status === 'active').length;
  const proposalCount = clients.filter(c => c.status === 'proposal').length;
  const totalPipeline = clients.reduce((sum, c) => sum + (c.dealValue || 0), 0);

  const oneWeekAgo = new Date();
  oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
  const oneWeekAgoStr = oneWeekAgo.toISOString().split('T')[0];
  const todayStr      = new Date().toISOString().split('T')[0];

  res.json({
    summary: {
      activeClients:    activeCount,
      proposals:        proposalCount,
      pipelineValue:    totalPipeline,
      thisWeekOrders:   orders.filter(o => o.date >= oneWeekAgoStr).length,
      todayOrders:      orders.filter(o => o.date === todayStr).length
    },
    recentOrders: orders.slice(-5).reverse(),
    clients
  });
});

// ── Orders ───────────────────────────────────────────────────────────────────
router.get('/orders', (req, res) => {
  const db = req.app.get('db');
  const orders = db.prepare('SELECT * FROM orders ORDER BY createdAt DESC').all();
  res.json(orders);
});

router.post('/orders', [
  body('customerName').trim().notEmpty().isLength({ max: 100 }),
  body('customerEmail').isEmail().normalizeEmail(),
  body('productName').trim().notEmpty(),
  body('quantity').isInt({ min: 1 }),
  body('utm_source').optional().trim().escape(),
  body('utm_medium').optional().trim().escape(),
  body('utm_campaign').optional().trim().escape()
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

  const db = req.app.get('db');
  const {
    customerName, customerEmail, date, salesRep, orderType,
    productName, quantity, utm_source, utm_medium, utm_campaign
  } = req.body;

  const info = db.prepare(`
    INSERT INTO orders (customerName, customerEmail, date, salesRep, orderType,
                        productName, quantity, status, utm_source, utm_medium, utm_campaign)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(
    customerName, customerEmail, date, salesRep, orderType,
    productName, parseInt(quantity), 'pending',
    utm_source || null, utm_medium || null, utm_campaign || null
  );

  const invoiceId  = `INV-${info.lastInsertRowid}`;
  const shipmentId = `SHIP-${info.lastInsertRowid}`;

  res.json({
    success: true,
    message: 'Order submitted successfully',
    order: {
      id: info.lastInsertRowid, customerName, customerEmail,
      date, salesRep, orderType, productName,
      quantity: parseInt(quantity), status: 'pending',
      createdAt: new Date(), invoiceId, shipmentId
    },
    automation: {
      qboInvoice:       `Created invoice ${invoiceId}`,
      shipstationOrder: `Created shipment ${shipmentId}`,
      emailSent:        `Confirmation sent to ${customerEmail}`
    }
  });
});

// ── Work Items ───────────────────────────────────────────────────────────────
const DUE_DATE_MAP = {
  new_lead: 2, schedule_discovery_call: 1, create_proposal: 5,
  send_contract: 7, onboard_client: 1, modify_workflow: 3,
  create_invoice: 0, send_payment_reminder: 0, log_payment_received: 0,
  send_email: 0, add_workflow: 0, generate_sow: 7,
  resolve_integration_issue: 0, handle_alert: 0
};

const SCRIPT_MAP = {
  new_lead: 'create_client.py', schedule_discovery_call: 'create_calendar_link.py',
  create_proposal: 'create_proposal.py', send_contract: 'send_contract.py',
  onboard_client: 'onboard_client.py', modify_workflow: 'log_activity.py',
  create_invoice: 'create_invoice.py', send_payment_reminder: 'send_email.py',
  log_payment_received: 'update_client.py', send_email: 'send_email.py',
  add_workflow: 'add_workflow.py', generate_sow: 'create_document.py',
  resolve_integration_issue: 'debug_integration.py', handle_alert: 'monitor_recovery.py'
};

const PREVIEWS = {
  new_lead:                  { directive: 'Capture prospect info and schedule discovery call', template: 'Discovery call scheduling email', execution: 'Creates client folder + sends calendar link' },
  schedule_discovery_call:   { directive: 'Schedule systematic discovery call with prospect', template: 'Calendar link + reminder email', execution: 'Generates scheduling link + sends email' },
  create_proposal:           { directive: 'Generate professional proposal from discovery notes', template: 'Proposal template with pricing', execution: 'Loads discovery data + creates Google Doc + exports PDF + sends email' },
  send_contract:             { directive: 'Route MSA/SOW/NDA to e-signature', template: 'Choose MSA, SOW, or NDA', execution: 'Generates contract document + sends to DocuSign' },
  onboard_client:            { directive: 'Send welcome email and schedule kickoff call', template: 'Kickoff call scheduling email', execution: 'Sends welcome email + generates calendar link' },
  modify_workflow:           { directive: 'Document new feature/modification request', template: 'Follow-up discovery questions', execution: 'Captures scope + schedules follow-up call' },
  create_invoice:            { directive: 'Generate invoice with payment links', template: 'Invoice template with Stripe/PayPal links', execution: 'Creates invoice + generates PDF + sends email' },
  send_payment_reminder:     { directive: 'Send payment reminder for overdue invoice', template: 'Payment reminder email', execution: 'Sends reminder + updates invoice status' },
  send_email:                { directive: 'Send templated email to client', template: 'Template picker (8 available)', execution: 'Loads template + sends to client email' },
  add_workflow:              { directive: 'Document new automation/workflow', template: 'Workflow README template', execution: 'Creates workflow folder + documents process' },
  generate_sow:              { directive: 'Create custom statement of work', template: 'SOW with deliverables + timeline', execution: 'Generates SOW document + stores in client folder' },
  resolve_integration_issue: { directive: 'Handle integration failures (QB, ShipStation, webhook)', template: 'Debug playbook', execution: 'Runs auto-recovery script or escalates' },
  handle_alert:              { directive: 'Respond to monitoring alerts', template: 'Alert context + recovery steps', execution: 'Auto-retry or routes to manual investigation' }
};

router.get('/work-items', (req, res) => {
  const { status, client, type } = req.query;
  let filtered = [...workItems];

  if (status) filtered = filtered.filter(w => w.status === status);
  if (client) filtered = filtered.filter(w => w.client_slug === client);
  if (type)   filtered = filtered.filter(w => w.type === type);

  const priorityOrder = { high: 0, medium: 1, low: 2 };
  filtered.sort((a, b) => {
    const pd = (priorityOrder[a.priority] || 1) - (priorityOrder[b.priority] || 1);
    return pd !== 0 ? pd : new Date(a.due_date) - new Date(b.due_date);
  });

  res.json(filtered);
});

router.post('/work-items', (req, res) => {
  const { type, client_slug, description } = req.body;
  if (!type || !client_slug || !description) {
    return res.status(400).json({ error: 'Missing required fields: type, client_slug, description' });
  }

  const daysToAdd = DUE_DATE_MAP[type] || 0;
  const dueDate   = new Date();
  dueDate.setDate(dueDate.getDate() + daysToAdd);

  workItemCounter++;
  const workItem = {
    id: `WI-${String(workItemCounter).padStart(3, '0')}`,
    type, client_slug, description,
    status: 'pending',
    created_at: new Date().toISOString(),
    due_date: dueDate.toISOString().split('T')[0],
    priority: 'medium',
    context: {},
    preview_generated: false,
    execution: { script: null, status: 'pending', result: null }
  };

  workItems.push(workItem);
  res.json({ success: true, workItem });
});

router.get('/work-items/:id', (req, res) => {
  const workItem = workItems.find(w => w.id === req.params.id);
  if (!workItem) return res.status(404).json({ error: 'Work item not found' });

  res.json({
    workItem,
    preview: PREVIEWS[workItem.type] || { directive: 'Unknown', template: 'None', execution: 'Custom' }
  });
});

router.post('/work-items/:id/execute', (req, res) => {
  const workItem = workItems.find(w => w.id === req.params.id);
  if (!workItem) return res.status(404).json({ error: 'Work item not found' });

  workItem.status           = 'executing';
  workItem.execution.status = 'running';
  workItem.execution.script = SCRIPT_MAP[workItem.type] || 'unknown.py';

  const artifacts = {};
  if (workItem.type === 'create_proposal') {
    artifacts.google_doc_url = 'https://docs.google.com/document/d/example';
    artifacts.pdf_path = `/clients/${workItem.client_slug}/proposals/proposal-${Date.now()}.pdf`;
  } else if (workItem.type === 'create_invoice') {
    artifacts.invoice_number = `INV-${new Date().toISOString().split('T')[0].replace(/-/g, '')}-001`;
    artifacts.invoice_path = `/clients/${workItem.client_slug}/invoices/invoice-${Date.now()}.pdf`;
  } else if (workItem.type === 'send_email') {
    artifacts.timestamp = new Date().toISOString();
  }

  workItem.status           = 'completed';
  workItem.execution.status = 'completed';
  workItem.execution.result = { success: true, artifacts, completed_at: new Date().toISOString() };

  res.json({ success: true, workItem });
});

module.exports = router;
