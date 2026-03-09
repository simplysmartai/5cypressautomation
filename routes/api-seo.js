/**
 * routes/api-seo.js
 * SEO analysis, Stripe checkout, report retrieval, and config endpoints.
 * stripe instance is injected via req.app.get('stripe').
 */
const express = require('express');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

const router = express.Router();
const ROOT = path.join(__dirname, '..');

// ── SEO config (tells frontend which features are enabled) ───────────────────
router.get('/config', (req, res) => {
  const stripe    = req.app.get('stripe');
  const adminUser = process.env.ADMIN_USER;
  const adminPass = process.env.ADMIN_PASS;
  let isAdmin = false;

  const authHeader = req.headers.authorization;
  if (authHeader && authHeader.startsWith('Basic ') && adminUser && adminPass) {
    const creds = Buffer.from(authHeader.split(' ')[1], 'base64').toString('utf8');
    const [user, pass] = creds.split(':');
    if (user === adminUser && pass === adminPass) isAdmin = true;
  }

  res.json({
    stripe_enabled:       !!(stripe && process.env.STRIPE_SECRET_KEY),
    is_admin:             isAdmin,
    dataforseo_enabled:   !!(process.env.DATAFORSEO_USERNAME && process.env.DATAFORSEO_PASSWORD),
    pagespeed_enabled:    !!process.env.GOOGLE_PAGESPEED_API_KEY,
    calendly_url:         process.env.CALENDLY_URL || 'https://calendly.com/jimmy-5cypress/30min',
    brand:                '5 Cypress Automation'
  });
});

// ── Full SEO analysis (spawns Python script) ─────────────────────────────────
router.post('/analyze', async (req, res) => {
  const { website_url, keywords, modules, competitors } = req.body;

  if (!website_url) return res.status(400).json({ error: 'Missing website_url parameter' });

  try {
    new URL(website_url.startsWith('http') ? website_url : 'https://' + website_url);
  } catch {
    return res.status(400).json({ error: 'Invalid URL format' });
  }

  const outputDir = path.join(ROOT, '.tmp', 'seo_reports');
  fs.mkdirSync(outputDir, { recursive: true });

  const domain     = new URL(website_url.startsWith('http') ? website_url : 'https://' + website_url)
    .hostname.replace(/[^a-z0-9]/gi, '-');
  const outputPath = path.join(outputDir, `${domain}.json`);

  console.log(`[SEO] Starting analysis for ${website_url}`);

  const pythonProcess = spawn('python', [
    path.join(ROOT, 'execution', 'seo_audit_runner.py'),
    '--website-url', website_url,
    '--keywords',    keywords    ? (Array.isArray(keywords)    ? keywords.join(',')    : keywords)    : '',
    '--modules',     modules     ? (Array.isArray(modules)     ? modules.join(',')     : modules)     : 'on_page',
    '--competitors', competitors ? (Array.isArray(competitors) ? competitors.join(',') : competitors) : '',
    '--output', outputPath
  ]);

  let stderr = '';
  pythonProcess.stdout.on('data', d => console.log(`[SEO] ${d.toString().trim()}`));
  pythonProcess.stderr.on('data', d => { stderr += d.toString(); console.error(`[SEO ERR] ${d.toString().trim()}`); });

  // 2-minute timeout
  const timeout = setTimeout(() => {
    pythonProcess.kill();
    res.status(504).json({ error: 'Analysis timeout — website may be too large or slow' });
  }, 120_000);

  pythonProcess.on('close', (code) => {
    clearTimeout(timeout);
    if (res.headersSent) return;
    if (code !== 0) {
      return res.status(500).json({ error: 'SEO analysis failed', details: stderr || 'Unknown error' });
    }
    try {
      const db       = req.app.get('db');
      const report    = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
      const reportRaw = JSON.stringify(report);
      try {
        const exists = db.prepare('SELECT id FROM seo_audits WHERE domain = ? AND status = "pending"').get(domain);
        if (exists) {
          db.prepare('UPDATE seo_audits SET report_data = ? WHERE id = ?').run(reportRaw, exists.id);
        } else {
          db.prepare('INSERT INTO seo_audits (domain, report_data, status) VALUES (?, ?, "pending")').run(domain, reportRaw);
        }
      } catch (dbErr) {
        console.error('[SEO] DB logging failed:', dbErr.message);
      }
      res.json(report);
    } catch {
      res.status(500).json({ error: 'Failed to read analysis results' });
    }
  });
});

// ── Admin: Free premium report (bypasses payment) ────────────────────────────
router.get('/admin/report/:domain', (req, res) => {
  const safeDomain = req.params.domain.replace(/[^a-z0-9-]/gi, '-');
  const reportPath = path.join(ROOT, '.tmp', 'seo_reports', `${safeDomain}.json`);
  if (!fs.existsSync(reportPath)) {
    return res.status(404).json({ error: 'No cached report found. Run /api/seo/analyze first.' });
  }
  try {
    const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
    res.json({ ...report, admin_access: true, payment_bypassed: true });
  } catch {
    res.status(500).json({ error: 'Failed to read report' });
  }
});

// ── Stripe checkout session ───────────────────────────────────────────────────
router.post('/create-checkout-session', async (req, res) => {
  const { domain, email } = req.body;
  const stripe = req.app.get('stripe');

  if (!domain) return res.status(400).json({ error: 'Domain is required' });

  if (!stripe) {
    const calendlyUrl = process.env.CALENDLY_URL || 'https://calendly.com/jimmy-5cypress/30min';
    return res.status(402).json({
      error:       'stripe_not_configured',
      message:     'Premium report available via consultation. Book a free call instead.',
      fallback:    'calendly',
      calendly_url: calendlyUrl
    });
  }

  try {
    const db = req.app.get('db');
    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      customer_email: email,
      line_items: [{
        price_data: {
          currency:     'usd',
          product_data: {
            name:        'SEO Intelligence Audit - Premium Dossier',
            description: `Deep structural audit and vulnerability report for ${domain}`
          },
          unit_amount: 5000 // $50.00
        },
        quantity: 1
      }],
      mode:        'payment',
      success_url: `${process.env.STRIPE_SUCCESS_URL || 'http://localhost:3000/seo-report.html'}?domain=${domain}&session_id={CHECKOUT_SESSION_ID}`,
      cancel_url:  process.env.STRIPE_CANCEL_URL || 'http://localhost:3000/seo-dashboard.html',
      metadata:    { domain, audit_type: 'premium_dossier' }
    });

    db.prepare('UPDATE seo_audits SET session_id = ?, email = ? WHERE domain = ? AND status = "pending"')
      .run(session.id, email, domain);

    res.json({ id: session.id, url: session.url });
  } catch (error) {
    console.error('[SEO] Stripe error:', error);
    res.status(500).json({ error: 'Failed to create checkout session' });
  }
});

// ── Verify payment + retrieve report ─────────────────────────────────────────
router.get('/report/:sessionId', async (req, res) => {
  const { sessionId } = req.params;
  const db     = req.app.get('db');
  const stripe = req.app.get('stripe');

  try {
    const audit = db.prepare('SELECT * FROM seo_audits WHERE session_id = ?').get(sessionId);
    if (!audit) return res.status(404).json({ error: 'Audit not found' });

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
      return res.json(JSON.parse(audit.report_data));
    }
    res.status(402).json({ error: 'Payment required', status: audit.status });
  } catch (error) {
    console.error('[SEO] Verification error:', error);
    res.status(500).json({ error: 'Failed to verify payment or retrieve report' });
  }
});

// ── Get cached SEO report by domain ──────────────────────────────────────────
router.get('/:domain', (req, res) => {
  const reportPath = path.join(ROOT, '.tmp', 'seo_reports', `${req.params.domain}.json`);
  if (!fs.existsSync(reportPath)) {
    return res.status(404).json({ error: 'No analysis found for this domain' });
  }
  try {
    res.json(JSON.parse(fs.readFileSync(reportPath, 'utf8')));
  } catch {
    res.status(500).json({ error: 'Failed to read analysis report' });
  }
});

module.exports = router;
