/**
 * Cloudflare Pages Function: POST /api/webhooks/calendly
 *
 * Handles Calendly webhook events (invitee.created, invitee.canceled).
 * - Verifies the HMAC-SHA256 signature using the Web Crypto API
 * - Sends an internal notification email via Resend
 * - Optionally stores the lead in Cloudflare KV if CALENDLY_LEADS_KV is bound
 *
 * Required Cloudflare Pages env secrets (set in dashboard → Settings → Variables):
 *   CALENDLY_WEBHOOK_SIGNING_KEY   — from webhook registration
 *   RESEND_API_KEY                 — Resend API key
 *   DEFAULT_FROM                   — sender address  (e.g. nick@5cypress.com)
 *
 * Optional KV binding:
 *   CALENDLY_LEADS_KV              — KV namespace for persisting leads
 */

// ── Signature verification (Web Crypto API — no Node.js crypto needed) ───────

async function verifyCalendlySignature(request, rawBody, signingKey) {
  if (!signingKey) {
    // Dev mode: skip verification when key not configured
    console.warn('[Calendly] CALENDLY_WEBHOOK_SIGNING_KEY not set — skipping signature check');
    return true;
  }

  const header = request.headers.get('calendly-webhook-signature');
  if (!header) return false;

  // Parse "t=<timestamp>,v1=<hex_sig>"
  const parts = {};
  header.split(',').forEach(part => {
    const idx = part.indexOf('=');
    if (idx > -1) parts[part.substring(0, idx)] = part.substring(idx + 1);
  });
  if (!parts.t || !parts.v1) return false;

  const signed = `${parts.t}.${rawBody}`;

  // Import the signing key
  const enc = new TextEncoder();
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    enc.encode(signingKey),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  // Compute HMAC
  const sigBuffer = await crypto.subtle.sign('HMAC', keyMaterial, enc.encode(signed));
  const computed = Array.from(new Uint8Array(sigBuffer))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');

  // Constant-time compare
  if (computed.length !== parts.v1.length) return false;
  let diff = 0;
  for (let i = 0; i < computed.length; i++) {
    diff |= computed.charCodeAt(i) ^ parts.v1.charCodeAt(i);
  }
  return diff === 0;
}

// ── Email notification via Resend ─────────────────────────────────────────────

async function sendNotificationEmail(env, lead) {
  if (!env.RESEND_API_KEY) {
    console.log('[Calendly] RESEND_API_KEY not set — skipping notification email');
    return;
  }

  const startFormatted = lead.startTime
    ? new Date(lead.startTime).toLocaleString('en-US', {
        timeZone: 'America/Chicago',
        dateStyle: 'full',
        timeStyle: 'short'
      })
    : 'See Calendly';

  const from = env.DEFAULT_FROM || 'nick@5cypress.com';

  const response = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${env.RESEND_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      from: `5 Cypress <${from}>`,
      to: 'nick@5cypress.com',
      reply_to: lead.email,
      subject: `📅 New Discovery Call: ${lead.name}`,
      html: `
        <div style="font-family:sans-serif;max-width:560px;margin:auto">
          <h2 style="color:#5d8c5d">New Discovery Call Booked</h2>
          <table style="width:100%;border-collapse:collapse">
            <tr>
              <td style="padding:8px;color:#666;width:120px"><strong>Name</strong></td>
              <td style="padding:8px">${lead.name}</td>
            </tr>
            <tr>
              <td style="padding:8px;color:#666"><strong>Email</strong></td>
              <td style="padding:8px"><a href="mailto:${lead.email}">${lead.email}</a></td>
            </tr>
            <tr>
              <td style="padding:8px;color:#666"><strong>Meeting time</strong></td>
              <td style="padding:8px">${startFormatted} (CT)</td>
            </tr>
            ${lead.timezone ? `<tr><td style="padding:8px;color:#666"><strong>Timezone</strong></td><td style="padding:8px">${lead.timezone}</td></tr>` : ''}
            ${lead.calendlyEventUri ? `<tr><td style="padding:8px;color:#666"><strong>Calendly link</strong></td><td style="padding:8px"><a href="${lead.calendlyEventUri}">${lead.calendlyEventUri}</a></td></tr>` : ''}
          </table>
          <hr style="border:0;border-top:1px solid #eee;margin:24px 0"/>
          <p style="color:#999;font-size:0.8em">Sent automatically by the 5 Cypress booking system · 5cypress.com</p>
        </div>
      `
    })
  });

  if (!response.ok) {
    const err = await response.text();
    console.error('[Calendly] Resend error:', err);
  } else {
    console.log('[Calendly] Notification email sent → nick@5cypress.com');
  }
}

// ── Optional KV persistence ───────────────────────────────────────────────────

async function persistLead(env, lead) {
  if (!env.CALENDLY_LEADS_KV) return; // KV not bound — skip silently
  const key = `lead:${lead.id}`;
  await env.CALENDLY_LEADS_KV.put(key, JSON.stringify(lead), {
    expirationTtl: 60 * 60 * 24 * 90 // Keep 90 days
  });
  console.log(`[Calendly] Lead stored in KV: ${key}`);
}

// ── Handler ───────────────────────────────────────────────────────────────────

export async function onRequestPost({ request, env }) {
  // Read raw body first (needed for signature verification)
  const rawBody = await request.text();

  // Verify signature
  const valid = await verifyCalendlySignature(request, rawBody, env.CALENDLY_WEBHOOK_SIGNING_KEY);
  if (!valid) {
    console.warn('[Calendly] Invalid webhook signature — rejected');
    return new Response(JSON.stringify({ error: 'Invalid signature' }), {
      status: 403,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  let event;
  try {
    event = JSON.parse(rawBody);
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  const eventType    = event?.event;
  const invitee      = event?.payload?.invitee;
  const eventDetails = event?.payload?.event;

  if (!eventType) {
    return new Response(JSON.stringify({ error: 'Missing event type' }), {
      status: 400,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  console.log(`[Calendly] Event received: ${eventType}`);

  // ── invitee.created → new booking ─────────────────────────────────────────
  if (eventType === 'invitee.created' && invitee) {
    const lead = {
      id: `cal_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
      name: invitee.name || 'Unknown',
      email: (invitee.email || '').toLowerCase(),
      source: 'calendly_webhook',
      service: 'discovery_call',
      status: 'booked',
      calendlyEventUri: eventDetails?.uri || null,
      startTime: eventDetails?.start_time || null,
      timezone: invitee.timezone || null,
      createdAt: new Date().toISOString()
    };

    // Fire-and-forget (Pages Functions can use waitUntil via ctx, but we await here for simplicity)
    await Promise.allSettled([
      sendNotificationEmail(env, lead),
      persistLead(env, lead)
    ]);
  }

  // ── invitee.canceled ──────────────────────────────────────────────────────
  if (eventType === 'invitee.canceled') {
    console.log(`[Calendly] Cancellation received for: ${invitee?.email || 'unknown'}`);
    // If KV is bound, you can look up and update the lead record here
  }

  return new Response(JSON.stringify({ received: true, event: eventType }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
}

// Only POST is allowed — return 405 for everything else
export async function onRequest({ request }) {
  if (request.method !== 'POST') {
    return new Response('Method Not Allowed', { status: 405 });
  }
}
