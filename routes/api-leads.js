/**
 * routes/api-leads.js
 * Lead capture, Calendly webhook, and contact/inquiry form endpoints.
 */
const express = require('express');
const crypto = require('crypto');
const { body, validationResult } = require('express-validator');

const router = express.Router();

// ── In-memory leads store (mirrors DB; DB is source of truth for /admin/api/leads) ──
const leads = [];

// ── Calendly webhook signature verifier ─────────────────────────────────────
function verifyCalendlySignature(req) {
  const signingKey = process.env.CALENDLY_WEBHOOK_SIGNING_KEY;
  if (!signingKey) {
    console.warn('[Calendly] CALENDLY_WEBHOOK_SIGNING_KEY not set — skipping signature check (dev mode)');
    return true;
  }
  const header = req.headers['calendly-webhook-signature'];
  if (!header) return false;

  const parts = {};
  header.split(',').forEach(part => {
    const idx = part.indexOf('=');
    if (idx > -1) parts[part.substring(0, idx)] = part.substring(idx + 1);
  });
  if (!parts.t || !parts.v1) return false;

  const rawBody = req.rawBody ? req.rawBody.toString('utf8') : '{}';
  const expected = crypto.createHmac('sha256', signingKey)
    .update(`${parts.t}.${rawBody}`)
    .digest('hex');

  try {
    return crypto.timingSafeEqual(Buffer.from(parts.v1, 'hex'), Buffer.from(expected, 'hex'));
  } catch {
    return false;
  }
}

// ── Lead capture ─────────────────────────────────────────────────────────────
router.post('/lead-capture', (req, res) => {
  const { email, name, source, service } = req.body;
  if (!email || !name) {
    return res.status(400).json({ error: 'Missing required fields: email, name' });
  }

  const db = req.app.get('db');
  let lead;
  try {
    const info = db.prepare(
      'INSERT INTO leads (name, email, source, service, status, followUpDate) VALUES (?, ?, ?, ?, ?, ?)'
    ).run(
      name,
      email.toLowerCase(),
      source  || 'direct',
      service || 'general',
      'new',
      new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
    );
    lead = { id: info.lastInsertRowid, name, email: email.toLowerCase(), source: source || 'direct', service: service || 'general', status: 'new' };
    leads.push(lead); // keep in-memory array in sync
  } catch (dbErr) {
    console.error('[LEAD-CAPTURE] DB insert failed:', dbErr.message);
    return res.status(500).json({ error: 'Failed to save lead' });
  }

  console.log(`[LEAD] ${name} <${email}> source=${source || 'direct'} @ ${new Date().toISOString()}`);
  res.status(201).json({ success: true, message: 'Lead captured successfully', lead });
});

// ── Get all in-memory leads (admin protected in server.js) ───────────────────
router.get('/leads', (req, res) => res.json(leads));

// ── Calendly webhook ─────────────────────────────────────────────────────────
router.post('/webhooks/calendly', async (req, res) => {
  if (!verifyCalendlySignature(req)) {
    console.warn('[Calendly] Invalid webhook signature – request rejected');
    return res.status(403).json({ error: 'Invalid signature' });
  }

  const event        = req.body;
  const eventType    = event?.event;
  const invitee      = event?.payload?.invitee;
  const eventDetails = event?.payload?.event;

  if (!eventType) return res.status(400).json({ error: 'Missing event type' });

  console.log(`[Calendly] Webhook received: ${eventType}`);

  if (eventType === 'invitee.created' && invitee) {
    const db = req.app.get('db');
    const leadData = {
      name:             invitee.name  || 'Unknown',
      email:            (invitee.email || '').toLowerCase(),
      source:           'calendly_webhook',
      service:          'discovery_call',
      status:           'booked',
      calendlyEventUri: eventDetails?.uri        || null,
      startTime:        eventDetails?.start_time || null,
      timezone:         invitee.timezone         || null,
      followUpDate:     new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString()
    };
    let lead;
    try {
      const info = db.prepare(
        'INSERT INTO leads (name, email, source, service, status, calendlyEventUri, startTime, timezone, followUpDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'
      ).run(
        leadData.name, leadData.email, leadData.source, leadData.service, leadData.status,
        leadData.calendlyEventUri, leadData.startTime, leadData.timezone, leadData.followUpDate
      );
      lead = { id: info.lastInsertRowid, ...leadData };
      leads.push(lead); // keep in-memory array in sync
    } catch (dbErr) {
      console.error('[Calendly] DB insert failed:', dbErr.message);
      // Still continue to send notification email even if DB write fails
      lead = { id: Date.now(), ...leadData };
    }

    const startFormatted = lead.startTime
      ? new Date(lead.startTime).toLocaleString('en-US', {
          timeZone: 'America/Chicago', dateStyle: 'full', timeStyle: 'short'
        })
      : 'See Calendly';

    console.log(`[Calendly] Booking: ${lead.name} <${lead.email}> @ ${startFormatted}`);

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

  if (eventType === 'invitee.canceled' && invitee) {
    const cancelEmail = (invitee.email || '').toLowerCase();
    const db = req.app.get('db');
    try {
      db.prepare("UPDATE leads SET status = 'canceled' WHERE email = ? AND status = 'booked'")
        .run(cancelEmail);
      console.log(`[Calendly] Lead ${cancelEmail} marked as canceled in DB`);
    } catch (dbErr) {
      console.error('[Calendly] Failed to update canceled status in DB:', dbErr.message);
    }
    // Also update in-memory
    const existing = leads.find(l => l.email === cancelEmail && l.status === 'booked');
    if (existing) existing.status = 'canceled';
  }

  res.status(200).json({ received: true, event: eventType });
});

// ── General contact form ──────────────────────────────────────────────────────
router.post('/contact', [
  body('name').trim().notEmpty().isLength({ max: 150 }).escape(),
  body('email').isEmail().normalizeEmail(),
  body('website').optional({ checkFalsy: true }).trim().isLength({ max: 200 }),
  body('source').optional().trim().escape(),
  body('scanned_domain').optional().trim().isLength({ max: 200 }),
  body('challenge').optional().trim().isLength({ max: 2000 }),
  body('details').optional().trim().isLength({ max: 2000 }),
  body('company').optional().trim().isLength({ max: 200 }).escape(),
  body('timeline').optional().trim().escape()
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

  const { name, email, website, source, scanned_domain, challenge, details, company, timeline } = req.body;
  const db = req.app.get('db');

  try {
    db.prepare(`
      INSERT INTO leads (name, email, company, website, source, scanned_domain, challenge, timeline)
      VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    `).run(
      name, email, company || null, website || null, source || null,
      scanned_domain || null, (challenge || details) || null, timeline || null
    );
  } catch (dbErr) {
    console.error('[CONTACT] Lead DB log failed (non-fatal):', dbErr.message);
  }

  console.log(`[LEAD] ${name} <${email}> from ${source || 'website'} @ ${new Date().toISOString()}`);
  res.json({ success: true, message: "We'll be in touch within one business day." });
});

// ── Public inquiry / vetting form (submit-inquiry) ───────────────────────────
router.post('/submit-inquiry', [
  body('name').trim().notEmpty().isLength({ max: 150 }).escape(),
  body('email').isEmail().normalizeEmail(),
  body('company').optional({ checkFalsy: true }).trim().isLength({ max: 200 }).escape(),
  body('details').optional({ checkFalsy: true }).trim().isLength({ max: 2000 })
], (req, res) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) return res.status(400).json({ errors: errors.array() });

  const { name, email, company, details } = req.body;
  const db = req.app.get('db');

  try {
    db.prepare(`INSERT INTO leads (name, email, company, source, challenge) VALUES (?, ?, ?, ?, ?)`)
      .run(name, email, company || null, 'website-inquiry', details || null);
  } catch (dbErr) {
    console.error('[INQUIRY] DB log failed (non-fatal):', dbErr.message);
  }

  console.log(`[INQUIRY] New inquiry from ${name} <${email}> @ ${new Date().toISOString()}`);
  res.json({ success: true, message: "Application received. We'll be in touch within one business day." });
});

module.exports = router;
