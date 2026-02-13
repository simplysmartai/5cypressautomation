const express = require('express');
const path = require('path');
const { exec } = require('child_process');
const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// Basic logger
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} - ${req.method} ${req.url}`);
  next();
});

// In-memory storage for demo
let orders = [
  {
    id: 1,
    customerName: 'Tech Corp',
    customerEmail: 'john@techcorp.com',
    date: '2026-01-20',
    salesRep: 'Doc',
    orderType: 'New',
    productName: 'Laser 1',
    quantity: 2,
    status: 'invoiced',
    createdAt: new Date('2026-01-20')
  },
  {
    id: 2,
    customerName: 'Manufacturing Inc',
    customerEmail: 'sarah@mfg.com',
    date: '2026-01-21',
    salesRep: 'Other guy',
    orderType: 'Renewal',
    productName: 'Mini Laser 2',
    quantity: 1,
    status: 'shipped',
    createdAt: new Date('2026-01-21')
  }
];

let clients = [
  {
    slug: 'remy-lasers',
    name: 'Remy Lasers',
    status: 'prospecting',
    dealValue: 2500,
    nextAction: 'Present 30-day trial program to CFO',
    engagement: 'trial_program',
    industry: 'Laser Manufacturing',
    createdAt: new Date('2026-02-03')
  },
  {
    slug: 'acme-plumbing-co',
    name: 'Acme Plumbing Co',
    status: 'proposal',
    dealValue: 7500,
    nextAction: 'Send proposal and follow up'
  },
  {
    slug: 'tech-corp',
    name: 'Tech Corp',
    status: 'active',
    dealValue: 12000,
    nextAction: 'Weekly check-in'
  },
  {
    slug: 'mfg-inc',
    name: 'Manufacturing Inc',
    status: 'active',
    dealValue: 8500,
    nextAction: 'Monitor deployment'
  }
];

// Work items storage (for operations dashboard)
let workItems = [];
let workItemCounter = 0;

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

app.get('/preview-work-item', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'preview-work-item.html'));
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
  const activeCount = clients.filter(c => c.status === 'active').length;
  const proposalCount = clients.filter(c => c.status === 'proposal').length;
  const totalPipeline = clients.reduce((sum, c) => sum + c.dealValue, 0);
  const thisWeekOrders = orders.filter(o => {
    const orderDate = new Date(o.date);
    const oneWeekAgo = new Date();
    oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
    return orderDate >= oneWeekAgo;
  }).length;

  res.json({
    summary: {
      activeClients: activeCount,
      proposals: proposalCount,
      pipelineValue: totalPipeline,
      thisWeekOrders: thisWeekOrders,
      todayOrders: orders.filter(o => o.date === new Date().toISOString().split('T')[0]).length
    },
    recentOrders: orders.slice(-5).reverse(),
    clients: clients
  });
});

app.get('/api/orders', (req, res) => {
  res.json(orders);
});

app.post('/api/orders', (req, res) => {
  const { customerName, customerEmail, date, salesRep, orderType, productName, quantity } = req.body;
  
  // Validation
  if (!customerName || !customerEmail || !productName || !quantity) {
    return res.status(400).json({ error: 'Missing required fields' });
  }

  const newOrder = {
    id: orders.length + 1,
    customerName,
    customerEmail,
    date,
    salesRep,
    orderType,
    productName,
    quantity: parseInt(quantity),
    status: 'pending',
    createdAt: new Date(),
    invoiceId: `INV-${Date.now()}`,
    shipmentId: `SHIP-${Date.now()}`
  };

  orders.push(newOrder);

  res.json({
    success: true,
    message: 'Order submitted successfully',
    order: newOrder,
    automation: {
      qboInvoice: `Created invoice ${newOrder.invoiceId}`,
      shipstationOrder: `Created shipment ${newOrder.shipmentId}`,
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

// Admin Pipeline Action API
app.post('/api/admin/pipeline-action', (req, res) => {
  const { action, id, data } = req.body;
  console.log(`Received pipeline action: ${action} for ${id}`);
  
  // Simulate processing
  res.json({
    success: true,
    message: `Action ${action} processed successfully for ${id}`,
    timestamp: new Date().toISOString()
  });
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

// Get all leads (admin)
app.get('/api/leads', (req, res) => {
  res.json(leads);
});

// SEO Analysis API
app.post('/api/seo/analyze', async (req, res) => {
  const { website_url } = req.body;
  
  if (!website_url) {
    return res.status(400).json({ error: 'Missing website_url parameter' });
  }
  
  // Validate URL format
  try {
    new URL(website_url);
  } catch (e) {
    return res.status(400).json({ error: 'Invalid URL format' });
  }
  
  const { spawn } = require('child_process');
  const fs = require('fs');
  
  // Create output path
  const outputDir = path.join(__dirname, '.tmp', 'seo_reports');
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true });
  }
  
  const domain = new URL(website_url).hostname.replace(/[^a-z0-9]/gi, '-');
  const outputPath = path.join(outputDir, `${domain}.json`);
  
  console.log(`Starting SEO analysis for ${website_url}`);
  
  // Spawn Python process
  const pythonProcess = spawn('python', [
    path.join(__dirname, 'execution', 'seo_orchestrator.py'),
    '--website-url', website_url,
    '--output', outputPath,
    '--max-pages', '30'
  ]);
  
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

app.post('/api/skills/:id/run', (req, res) => {
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
