'use strict';

const express = require('express');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const crypto = require('crypto');
const PDFDocument = require('pdfkit');
const { body, validationResult } = require('express-validator');
const verifyGigClockToken = require('../middleware/gigclockAuth');

const router = express.Router();

// ── Helpers ───────────────────────────────────────────────────────────────────

function isPro(user) {
  if (user.plan !== 'pro') return false;
  if (!user.plan_expires_at) return false;
  return new Date(user.plan_expires_at) > new Date();
}

function signToken(user) {
  return jwt.sign(
    { id: user.id, email: user.email, plan: user.plan, plan_expires_at: user.plan_expires_at },
    process.env.GC_JWT_SECRET,
    { expiresIn: '7d' }
  );
}

function userPublic(user) {
  return { id: user.id, email: user.email, name: user.name, brand_name: user.brand_name, plan: user.plan, plan_expires_at: user.plan_expires_at };
}

function handleValidation(req, res) {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    res.status(400).json({ error: 'Validation failed', details: errors.array() });
    return false;
  }
  return true;
}

function secondsToHours(s) { return Math.round((s / 3600) * 100) / 100; }

function elapsedSeconds(startedAt) {
  return Math.floor((Date.now() - new Date(startedAt).getTime()) / 1000);
}

// ── A. Auth endpoints ─────────────────────────────────────────────────────────

// POST /api/gigclock/register
router.post('/register', [
  body('email').isEmail().normalizeEmail(),
  body('password').isLength({ min: 8, max: 100 }),
  body('name').trim().notEmpty().isLength({ max: 150 }).escape(),
  body('brand_name').optional().trim().isLength({ max: 100 }).escape(),
], async (req, res) => {
  if (!handleValidation(req, res)) return;
  const db = req.app.get('db');
  const { email, password, name, brand_name } = req.body;

  const existing = db.prepare('SELECT id FROM gc_users WHERE email = ?').get(email);
  if (existing) return res.status(409).json({ error: 'An account with that email already exists' });

  const password_hash = await bcrypt.hash(password, 12);
  const stmt = db.prepare('INSERT INTO gc_users (email, password_hash, name, brand_name) VALUES (?, ?, ?, ?)');
  const result = stmt.run(email, password_hash, name, brand_name || null);
  const user = db.prepare('SELECT * FROM gc_users WHERE id = ?').get(result.lastInsertRowid);

  res.status(201).json({ token: signToken(user), user: userPublic(user) });
});

// POST /api/gigclock/login
router.post('/login', [
  body('email').isEmail().normalizeEmail(),
  body('password').notEmpty(),
], async (req, res) => {
  if (!handleValidation(req, res)) return;
  const db = req.app.get('db');
  const { email, password } = req.body;

  const user = db.prepare('SELECT * FROM gc_users WHERE email = ?').get(email);
  if (!user) return res.status(401).json({ error: 'Invalid credentials' });

  const match = await bcrypt.compare(password, user.password_hash);
  if (!match) return res.status(401).json({ error: 'Invalid credentials' });

  res.json({ token: signToken(user), user: userPublic(user) });
});

// GET /api/gigclock/me — return current user profile (refreshes plan state)
router.get('/me', verifyGigClockToken, (req, res) => {
  const db = req.app.get('db');
  const user = db.prepare('SELECT * FROM gc_users WHERE id = ?').get(req.gcUser.id);
  if (!user) return res.status(404).json({ error: 'User not found' });
  res.json({ user: userPublic(user), token: signToken(user) });
});

// PUT /api/gigclock/me — update name and brand_name
router.put('/me', verifyGigClockToken, [
  body('name').optional().trim().notEmpty().isLength({ max: 150 }).escape(),
  body('brand_name').optional().trim().isLength({ max: 100 }).escape(),
], (req, res) => {
  if (!handleValidation(req, res)) return;
  const db = req.app.get('db');
  const { name, brand_name } = req.body;
  db.prepare('UPDATE gc_users SET name = COALESCE(?, name), brand_name = ? WHERE id = ?')
    .run(name || null, brand_name !== undefined ? brand_name : db.prepare('SELECT brand_name FROM gc_users WHERE id = ?').get(req.gcUser.id).brand_name, req.gcUser.id);
  const user = db.prepare('SELECT * FROM gc_users WHERE id = ?').get(req.gcUser.id);
  res.json({ user: userPublic(user) });
});

// ── B. Project endpoints ──────────────────────────────────────────────────────

// GET /api/gigclock/projects
router.get('/projects', verifyGigClockToken, (req, res) => {
  const db = req.app.get('db');
  const projects = db.prepare(`
    SELECT p.*,
      e.id AS running_entry_id,
      e.started_at AS running_since,
      e.description AS running_description
    FROM gc_projects p
    LEFT JOIN gc_time_entries e ON e.project_id = p.id AND e.stopped_at IS NULL
    WHERE p.user_id = ? AND p.is_archived = 0
    ORDER BY p.created_at DESC
  `).all(req.gcUser.id);

  res.json(projects);
});

// POST /api/gigclock/projects
router.post('/projects', verifyGigClockToken, [
  body('name').trim().notEmpty().isLength({ max: 200 }).escape(),
  body('client_name').optional().trim().isLength({ max: 200 }).escape(),
  body('hourly_rate').optional().isFloat({ min: 0, max: 99999 }),
], (req, res) => {
  if (!handleValidation(req, res)) return;
  const db = req.app.get('db');
  const user = db.prepare('SELECT * FROM gc_users WHERE id = ?').get(req.gcUser.id);

  if (!isPro(user)) {
    const activeCount = db.prepare('SELECT COUNT(*) as c FROM gc_projects WHERE user_id = ? AND is_archived = 0').get(req.gcUser.id).c;
    if (activeCount >= 1) {
      return res.status(403).json({
        error: 'free_tier_limit',
        message: 'Free plan is limited to 1 active project. Upgrade to Pro for unlimited projects.',
      });
    }
  }

  const { name, client_name, hourly_rate } = req.body;
  const share_token = uuidv4();
  const result = db.prepare('INSERT INTO gc_projects (user_id, name, client_name, hourly_rate, share_token) VALUES (?, ?, ?, ?, ?)')
    .run(req.gcUser.id, name, client_name || null, parseFloat(hourly_rate) || 0, share_token);

  const project = db.prepare('SELECT * FROM gc_projects WHERE id = ?').get(result.lastInsertRowid);
  res.status(201).json(project);
});

// PUT /api/gigclock/projects/:id
router.put('/projects/:id', verifyGigClockToken, [
  body('name').optional().trim().notEmpty().isLength({ max: 200 }).escape(),
  body('client_name').optional().trim().isLength({ max: 200 }).escape(),
  body('hourly_rate').optional().isFloat({ min: 0, max: 99999 }),
], (req, res) => {
  if (!handleValidation(req, res)) return;
  const db = req.app.get('db');
  const project = db.prepare('SELECT * FROM gc_projects WHERE id = ? AND user_id = ?').get(req.params.id, req.gcUser.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const { name, client_name, hourly_rate } = req.body;
  db.prepare('UPDATE gc_projects SET name = COALESCE(?, name), client_name = COALESCE(?, client_name), hourly_rate = COALESCE(?, hourly_rate) WHERE id = ?')
    .run(name || null, client_name !== undefined ? client_name : null, hourly_rate !== undefined ? parseFloat(hourly_rate) : null, project.id);

  res.json(db.prepare('SELECT * FROM gc_projects WHERE id = ?').get(project.id));
});

// DELETE /api/gigclock/projects/:id (soft delete)
router.delete('/projects/:id', verifyGigClockToken, (req, res) => {
  const db = req.app.get('db');
  const project = db.prepare('SELECT * FROM gc_projects WHERE id = ? AND user_id = ?').get(req.params.id, req.gcUser.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  db.prepare('UPDATE gc_projects SET is_archived = 1 WHERE id = ?').run(project.id);
  res.json({ success: true });
});

// ── C. Timer and entry endpoints ──────────────────────────────────────────────

// POST /api/gigclock/projects/:id/timer/start
router.post('/projects/:id/timer/start', verifyGigClockToken, [
  body('description').optional().trim().isLength({ max: 500 }).escape(),
], (req, res) => {
  if (!handleValidation(req, res)) return;
  const db = req.app.get('db');
  const project = db.prepare('SELECT * FROM gc_projects WHERE id = ? AND user_id = ?').get(req.params.id, req.gcUser.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  // Check if any timer is already running for this user
  const running = db.prepare(`
    SELECT e.*, p.id as project_id FROM gc_time_entries e
    JOIN gc_projects p ON e.project_id = p.id
    WHERE p.user_id = ? AND e.stopped_at IS NULL
    LIMIT 1
  `).get(req.gcUser.id);

  if (running) {
    return res.status(409).json({
      error: 'timer_already_running',
      running_project_id: running.project_id,
      running_entry_id: running.id,
    });
  }

  const { description } = req.body;
  const result = db.prepare('INSERT INTO gc_time_entries (project_id, description, started_at) VALUES (?, ?, datetime(\'now\'))').run(project.id, description || null);
  const entry = db.prepare('SELECT * FROM gc_time_entries WHERE id = ?').get(result.lastInsertRowid);
  res.status(201).json(entry);
});

// POST /api/gigclock/projects/:id/timer/stop
router.post('/projects/:id/timer/stop', verifyGigClockToken, (req, res) => {
  const db = req.app.get('db');
  const project = db.prepare('SELECT * FROM gc_projects WHERE id = ? AND user_id = ?').get(req.params.id, req.gcUser.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const running = db.prepare('SELECT * FROM gc_time_entries WHERE project_id = ? AND stopped_at IS NULL').get(project.id);
  if (!running) return res.status(404).json({ error: 'No active timer for this project' });

  const stmt = db.prepare(`
    UPDATE gc_time_entries
    SET stopped_at = datetime('now'),
        duration_seconds = CAST(ROUND((julianday('now') - julianday(started_at)) * 86400) AS INTEGER)
    WHERE id = ? AND stopped_at IS NULL
  `);
  const info = stmt.run(running.id);
  if (info.changes === 0) return res.status(409).json({ error: 'Timer was already stopped' });

  const entry = db.prepare('SELECT * FROM gc_time_entries WHERE id = ?').get(running.id);
  res.json(entry);
});

// GET /api/gigclock/projects/:id/entries
router.get('/projects/:id/entries', verifyGigClockToken, (req, res) => {
  const db = req.app.get('db');
  const project = db.prepare('SELECT * FROM gc_projects WHERE id = ? AND user_id = ?').get(req.params.id, req.gcUser.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const entries = db.prepare('SELECT * FROM gc_time_entries WHERE project_id = ? ORDER BY started_at DESC').all(project.id);
  const enriched = entries.map(e => ({
    ...e,
    elapsed_seconds: e.stopped_at === null ? elapsedSeconds(e.started_at) : null,
  }));
  res.json(enriched);
});

// DELETE /api/gigclock/entries/:id
router.delete('/entries/:id', verifyGigClockToken, (req, res) => {
  const db = req.app.get('db');
  // Verify entry belongs to a project owned by this user
  const entry = db.prepare(`
    SELECT e.* FROM gc_time_entries e
    JOIN gc_projects p ON e.project_id = p.id
    WHERE e.id = ? AND p.user_id = ?
  `).get(req.params.id, req.gcUser.id);
  if (!entry) return res.status(404).json({ error: 'Entry not found' });

  db.prepare('DELETE FROM gc_time_entries WHERE id = ?').run(entry.id);
  res.json({ success: true });
});

// GET /api/gigclock/projects/:id/summary
router.get('/projects/:id/summary', verifyGigClockToken, (req, res) => {
  const db = req.app.get('db');
  const project = db.prepare('SELECT * FROM gc_projects WHERE id = ? AND user_id = ?').get(req.params.id, req.gcUser.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const totals = db.prepare(`
    SELECT
      COUNT(*) as entry_count,
      COALESCE(SUM(duration_seconds), 0) as total_seconds
    FROM gc_time_entries
    WHERE project_id = ? AND stopped_at IS NOT NULL
  `).get(project.id);

  const running = db.prepare('SELECT * FROM gc_time_entries WHERE project_id = ? AND stopped_at IS NULL').get(project.id);
  const runningSeconds = running ? elapsedSeconds(running.started_at) : 0;
  const totalSeconds = totals.total_seconds + runningSeconds;

  res.json({
    project_id: project.id,
    total_seconds: totalSeconds,
    total_hours: secondsToHours(totalSeconds),
    total_cost: Math.round(secondsToHours(totalSeconds) * project.hourly_rate * 100) / 100,
    entry_count: totals.entry_count,
    running: !!running,
    running_entry_id: running ? running.id : null,
    running_seconds: runningSeconds,
  });
});

// ── D. Billing endpoints ──────────────────────────────────────────────────────

// POST /api/gigclock/billing/subscribe
router.post('/billing/subscribe', verifyGigClockToken, async (req, res) => {
  const stripe = req.app.get('stripe');
  if (!stripe) return res.status(402).json({ error: 'Billing not configured' });

  const priceId = process.env.GC_STRIPE_PRO_PRICE_ID;
  if (!priceId || priceId === 'price_REPLACEME') {
    return res.status(503).json({ error: 'Pro billing is not yet configured' });
  }

  const db = req.app.get('db');
  let user = db.prepare('SELECT * FROM gc_users WHERE id = ?').get(req.gcUser.id);
  if (!user) return res.status(404).json({ error: 'User not found' });

  // Get or create Stripe customer
  let customerId = user.stripe_customer_id;
  if (!customerId) {
    const customer = await stripe.customers.create({ email: user.email, name: user.name });
    customerId = customer.id;
    db.prepare('UPDATE gc_users SET stripe_customer_id = ? WHERE id = ?').run(customerId, user.id);
  }

  const baseUrl = process.env.GC_BASE_URL || 'http://localhost:3000';
  const session = await stripe.checkout.sessions.create({
    mode: 'subscription',
    customer: customerId,
    line_items: [{ price: priceId, quantity: 1 }],
    success_url: `${baseUrl}/gigclock/app.html?upgraded=1&session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${baseUrl}/gigclock/app.html`,
    metadata: { gc_user_id: String(user.id) },
  });

  res.json({ url: session.url });
});

// GET /api/gigclock/billing/verify?session_id=cs_xxx
router.get('/billing/verify', verifyGigClockToken, async (req, res) => {
  const stripe = req.app.get('stripe');
  if (!stripe) return res.status(402).json({ error: 'Billing not configured' });

  const { session_id } = req.query;
  if (!session_id) return res.status(400).json({ error: 'session_id required' });

  const session = await stripe.checkout.sessions.retrieve(session_id, { expand: ['subscription'] });

  const paid = session.payment_status === 'paid' ||
    (session.subscription && session.subscription.status === 'active');

  if (!paid) return res.status(402).json({ error: 'Payment not complete' });

  const db = req.app.get('db');
  db.prepare(`UPDATE gc_users SET plan = 'pro', plan_expires_at = datetime('now', '+1 month') WHERE id = ?`)
    .run(req.gcUser.id);

  const user = db.prepare('SELECT * FROM gc_users WHERE id = ?').get(req.gcUser.id);
  res.json({ upgraded: true, token: signToken(user), user: userPublic(user) });
});

// POST /api/gigclock/billing/webhook — Stripe subscription events
// Note: must be mounted BEFORE express.json() for raw body access, but we rely on req.rawBody set by server.js
router.post('/billing/webhook', express.raw({ type: 'application/json' }), async (req, res) => {
  const stripe = req.app.get('stripe');
  if (!stripe) return res.sendStatus(200);

  const sig = req.headers['stripe-signature'];
  const secret = process.env.GC_STRIPE_WEBHOOK_SECRET;
  if (!secret || secret === 'whsec_REPLACEME') return res.sendStatus(200);

  let event;
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, secret);
  } catch (err) {
    return res.status(400).json({ error: `Webhook signature verification failed: ${err.message}` });
  }

  if (event.type === 'customer.subscription.deleted') {
    const db = req.app.get('db');
    const customerId = event.data.object.customer;
    db.prepare(`UPDATE gc_users SET plan = 'free', plan_expires_at = NULL WHERE stripe_customer_id = ?`).run(customerId);
  }

  res.sendStatus(200);
});

// ── E. Public endpoints (no auth) ─────────────────────────────────────────────

// GET /api/gigclock/public/:shareToken
router.get('/public/:shareToken', (req, res) => {
  const db = req.app.get('db');
  const project = db.prepare(`
    SELECT p.*, u.plan, u.brand_name, u.plan_expires_at
    FROM gc_projects p
    JOIN gc_users u ON p.user_id = u.id
    WHERE p.share_token = ? AND p.is_archived = 0
  `).get(req.params.shareToken);

  if (!project) return res.status(404).json({ error: 'Project not found' });

  // Record view
  const ipHash = crypto.createHash('sha256').update(req.ip || '').digest('hex');
  db.prepare('INSERT INTO gc_client_views (project_id, ip_hash) VALUES (?, ?)').run(project.id, ipHash);

  const ownerIsPro = project.plan === 'pro' && project.plan_expires_at && new Date(project.plan_expires_at) > new Date();

  const entries = db.prepare('SELECT * FROM gc_time_entries WHERE project_id = ? ORDER BY started_at DESC').all(project.id);
  const running = entries.find(e => e.stopped_at === null);
  const completed = entries.filter(e => e.stopped_at !== null);

  const totalSeconds = completed.reduce((s, e) => s + (e.duration_seconds || 0), 0);
  const runningSeconds = running ? elapsedSeconds(running.started_at) : 0;
  const grandTotal = totalSeconds + runningSeconds;

  res.json({
    project: {
      id: project.id,
      name: project.name,
      client_name: project.client_name,
      hourly_rate: project.hourly_rate,
    },
    brand: {
      name: ownerIsPro && project.brand_name ? project.brand_name : '5 Cypress Automation',
      show_gigclock_branding: !ownerIsPro,
    },
    entries: completed.map(e => ({
      id: e.id,
      description: e.description,
      started_at: e.started_at,
      stopped_at: e.stopped_at,
      duration_seconds: e.duration_seconds,
      hours: secondsToHours(e.duration_seconds || 0),
      cost: Math.round(secondsToHours(e.duration_seconds || 0) * project.hourly_rate * 100) / 100,
    })),
    summary: {
      total_seconds: grandTotal,
      total_hours: secondsToHours(grandTotal),
      total_cost: Math.round(secondsToHours(grandTotal) * project.hourly_rate * 100) / 100,
      entry_count: completed.length,
    },
    running: running ? {
      entry_id: running.id,
      description: running.description,
      started_at: running.started_at,
      elapsed_seconds: runningSeconds,
    } : null,
  });
});

// GET /api/gigclock/public/:shareToken/analytics (Pro owners only)
router.get('/public/:shareToken/analytics', verifyGigClockToken, (req, res) => {
  const db = req.app.get('db');
  const project = db.prepare('SELECT * FROM gc_projects WHERE share_token = ? AND user_id = ? AND is_archived = 0')
    .get(req.params.shareToken, req.gcUser.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const user = db.prepare('SELECT * FROM gc_users WHERE id = ?').get(req.gcUser.id);
  if (!isPro(user)) return res.status(403).json({ error: 'Pro plan required for analytics' });

  const totalViews = db.prepare('SELECT COUNT(*) as c FROM gc_client_views WHERE project_id = ?').get(project.id).c;
  const uniqueIPs = db.prepare('SELECT COUNT(DISTINCT ip_hash) as c FROM gc_client_views WHERE project_id = ?').get(project.id).c;
  const dailyViews = db.prepare(`
    SELECT DATE(viewed_at) as date, COUNT(*) as views
    FROM gc_client_views
    WHERE project_id = ? AND viewed_at >= datetime('now', '-30 days')
    GROUP BY DATE(viewed_at)
    ORDER BY date DESC
  `).all(project.id);

  res.json({ total_views: totalViews, unique_visitors: uniqueIPs, daily_views: dailyViews });
});

// ── F. PDF Export (Pro only) ──────────────────────────────────────────────────

// GET /api/gigclock/projects/:id/export/pdf
router.get('/projects/:id/export/pdf', verifyGigClockToken, (req, res) => {
  const db = req.app.get('db');
  const user = db.prepare('SELECT * FROM gc_users WHERE id = ?').get(req.gcUser.id);
  if (!isPro(user)) return res.status(403).json({ error: 'Pro plan required for PDF export' });

  const project = db.prepare('SELECT * FROM gc_projects WHERE id = ? AND user_id = ?').get(req.params.id, req.gcUser.id);
  if (!project) return res.status(404).json({ error: 'Project not found' });

  const entries = db.prepare('SELECT * FROM gc_time_entries WHERE project_id = ? AND stopped_at IS NOT NULL ORDER BY started_at ASC').all(project.id);
  const totalSeconds = entries.reduce((s, e) => s + (e.duration_seconds || 0), 0);
  const totalHours = secondsToHours(totalSeconds);
  const totalCost = Math.round(totalHours * project.hourly_rate * 100) / 100;

  const brandName = user.brand_name || '5 Cypress Automation';
  const dateStr = new Date().toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });

  res.setHeader('Content-Type', 'application/pdf');
  res.setHeader('Content-Disposition', `attachment; filename="gigclock-${project.id}-${Date.now()}.pdf"`);

  const doc = new PDFDocument({ margin: 50, size: 'letter' });
  doc.pipe(res);

  // Header
  doc.fontSize(22).font('Helvetica-Bold').text(brandName, 50, 50);
  doc.fontSize(11).font('Helvetica').fillColor('#666').text('Time Tracking Report', 50, 78);
  doc.fillColor('#000');

  // Project info
  doc.moveDown(2);
  doc.fontSize(16).font('Helvetica-Bold').text(project.name);
  if (project.client_name) doc.fontSize(12).font('Helvetica').text(`Client: ${project.client_name}`);
  doc.fontSize(11).fillColor('#666').text(`Generated: ${dateStr}`).fillColor('#000');

  // Summary box
  doc.moveDown(1.5);
  doc.fontSize(13).font('Helvetica-Bold').text('Summary');
  doc.moveTo(50, doc.y + 4).lineTo(562, doc.y + 4).stroke('#e5e7eb');
  doc.moveDown(0.5);
  doc.fontSize(11).font('Helvetica');
  doc.text(`Total Hours: ${totalHours}h`);
  doc.text(`Hourly Rate: $${project.hourly_rate}/hr`);
  doc.text(`Total Amount: $${totalCost.toFixed(2)}`);
  doc.text(`Tasks Completed: ${entries.length}`);

  // Entry table
  doc.moveDown(1.5);
  doc.fontSize(13).font('Helvetica-Bold').text('Time Entries');
  doc.moveTo(50, doc.y + 4).lineTo(562, doc.y + 4).stroke('#e5e7eb');
  doc.moveDown(0.5);

  // Table header
  doc.fontSize(10).font('Helvetica-Bold').fillColor('#666');
  doc.text('Date', 50, doc.y, { width: 90 });
  doc.text('Description', 140, doc.y - doc.currentLineHeight(), { width: 260 });
  doc.text('Hours', 400, doc.y - doc.currentLineHeight(), { width: 60, align: 'right' });
  doc.text('Cost', 460, doc.y - doc.currentLineHeight(), { width: 102, align: 'right' });
  doc.fillColor('#000');
  doc.moveDown(0.3);
  doc.moveTo(50, doc.y).lineTo(562, doc.y).stroke('#e5e7eb');
  doc.moveDown(0.3);

  entries.forEach((e) => {
    const dateLabel = new Date(e.started_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    const hrs = secondsToHours(e.duration_seconds || 0);
    const cost = Math.round(hrs * project.hourly_rate * 100) / 100;
    const y = doc.y;
    doc.fontSize(10).font('Helvetica');
    doc.text(dateLabel, 50, y, { width: 90 });
    doc.text(e.description || '—', 140, y, { width: 260 });
    doc.text(`${hrs}h`, 400, y, { width: 60, align: 'right' });
    doc.text(`$${cost.toFixed(2)}`, 460, y, { width: 102, align: 'right' });
    doc.moveDown(0.3);
    doc.moveTo(50, doc.y).lineTo(562, doc.y).stroke('#f3f4f6');
    doc.moveDown(0.2);
  });

  // Total row
  doc.moveDown(0.5);
  doc.moveTo(50, doc.y).lineTo(562, doc.y).stroke('#000');
  doc.moveDown(0.4);
  const y = doc.y;
  doc.fontSize(11).font('Helvetica-Bold');
  doc.text('Total', 50, y, { width: 350 });
  doc.text(`${totalHours}h`, 400, y, { width: 60, align: 'right' });
  doc.text(`$${totalCost.toFixed(2)}`, 460, y, { width: 102, align: 'right' });

  // Footer
  doc.moveDown(3);
  doc.fontSize(9).font('Helvetica').fillColor('#999').text('Generated by GigClock — A 5 Cypress Automation tool', { align: 'center' });

  doc.end();
});

module.exports = router;
