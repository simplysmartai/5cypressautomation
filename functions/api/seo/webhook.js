/**
 * POST /api/seo/webhook
 * 
 * Stripe webhook handler. Verifies signature, handles payment completion.
 * On checkout.session.completed:
 *   1. Marks session as paid in KV
 *   2. Fetches the raw audit data from KV (saved by analyze.js)
 *   3. Calls OpenAI via seo-enrich.js to generate expert explanations + AI prompts
 *   4. Saves enriched report to KV as report:{session_id}
 * 
 * Register this URL in Stripe Dashboard → Webhooks:
 *   https://www.5cypress.com/api/seo/webhook
 *   Events: checkout.session.completed
 */

import { enrichReport } from '../../lib/seo-enrich.js';

export async function onRequest(context) {
  const { request, env } = context;

  if (request.method !== 'POST') {
    return new Response('Method not allowed', { status: 405 });
  }

  // ── Verify Stripe signature ───────────────────────────────────────────────
  const sig = request.headers.get('stripe-signature');
  const webhookSecret = env.STRIPE_WEBHOOK_SECRET;

  if (!webhookSecret) {
    console.error('[webhook] STRIPE_WEBHOOK_SECRET not configured');
    return new Response('Webhook secret not configured', { status: 500 });
  }

  const rawBody = await request.text();

  // Verify signature using Web Crypto (Cloudflare Workers compatible)
  let isValid = false;
  try {
    isValid = await verifyStripeSignature(rawBody, sig, webhookSecret);
  } catch (e) {
    console.error('[webhook] Signature verification error:', e.message);
    return new Response('Signature verification failed', { status: 400 });
  }

  if (!isValid) {
    console.error('[webhook] Invalid Stripe signature');
    return new Response('Invalid signature', { status: 400 });
  }

  let event;
  try {
    event = JSON.parse(rawBody);
  } catch {
    return new Response('Invalid JSON', { status: 400 });
  }

  // ── Handle events ─────────────────────────────────────────────────────────
  if (event.type === 'checkout.session.completed') {
    const session = event.data.object;
    const sessionId = session.id;
    const domain    = session.metadata?.domain || '';
    const auditId   = session.metadata?.audit_id || '';
    const email     = session.metadata?.email || session.customer_email || '';

    console.log(`[webhook] Payment completed: ${sessionId} for ${domain}`);

    try {
      // 1. Mark session as paid in KV
      const sessionData = { domain, email, audit_id: auditId, status: 'paid', paid_at: new Date().toISOString() };
      await env.SEO_AUDITS_KV.put(`session:${sessionId}`, JSON.stringify(sessionData), { expirationTtl: 2592000 }); // 30 days

      // 2. Fetch raw audit data from KV
      let auditData = null;
      if (auditId) {
        const raw = await env.SEO_AUDITS_KV.get(`audit:${auditId}`);
        if (raw) {
          try { auditData = JSON.parse(raw); } catch {}
        }
      }

      // 3. If no audit_id stored, create a minimal data object so enrichment still works
      if (!auditData) {
        auditData = { domain, score: 0, full_report: { on_page: [], technical: [] }, page_speed: {}, keywords: [], backlinks: {} };
        console.warn(`[webhook] No audit data found for audit_id=${auditId}, enriching with minimal data`);
      } else {
        // auditData from KV is the full analyze.js response — extract the 'data' field
        auditData = auditData.data || auditData;
      }

      // 4. Call OpenAI enrichment (fire & don't await the full error path — store result)
      let enriched;
      try {
        enriched = await enrichReport(auditData, env);
      } catch (e) {
        console.error(`[webhook] OpenAI enrichment failed: ${e.message}`);
        enriched = {
          executive_summary: `Audit complete for ${domain}. Expert analysis could not be generated automatically — you will receive a follow-up email from 5 Cypress within 24 hours.`,
          overall_grade: 'N/A',
          findings: [],
          quick_wins: [],
          roadmap: { phase1: { label: 'Analysis in progress', focus: 'Manual review in progress', tasks: [] }, phase2: { label: '', focus: '', tasks: [] }, phase3: { label: '', focus: '', tasks: [] } },
          keyword_strategy: 'Keyword data not available.',
          backlink_insight: 'Backlink data not available.',
          raw_audit: auditData,
          enriched_at: new Date().toISOString(),
          model_used: 'fallback',
          error: e.message,
        };
      }

      // 5. Save enriched report to KV (30 days TTL)
      const reportPayload = {
        session_id: sessionId,
        domain,
        email,
        paid_at: sessionData.paid_at,
        enriched,
        status: 'ready',
      };
      await env.SEO_AUDITS_KV.put(`report:${sessionId}`, JSON.stringify(reportPayload), { expirationTtl: 2592000 });
      console.log(`[webhook] ✓ Enriched report saved for session ${sessionId}`);

    } catch (e) {
      console.error(`[webhook] Fulfillment error: ${e.message}`);
      // Still return 200 to Stripe — don't retry the webhook
    }
  }

  return new Response(JSON.stringify({ received: true }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });
}

/**
 * Verify Stripe webhook signature using Web Crypto API (Workers compatible).
 * Stripe signs with HMAC-SHA256.
 * Signature header format: t=timestamp,v1=signature
 */
async function verifyStripeSignature(payload, sigHeader, secret) {
  if (!sigHeader) return false;

  const parts = {};
  for (const part of sigHeader.split(',')) {
    const [k, v] = part.split('=');
    parts[k] = v;
  }

  const timestamp = parts['t'];
  const signature = parts['v1'];
  if (!timestamp || !signature) return false;

  const signedPayload = `${timestamp}.${payload}`;
  const enc = new TextEncoder();

  const key = await crypto.subtle.importKey(
    'raw',
    enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false,
    ['sign']
  );

  const sigBytes = await crypto.subtle.sign('HMAC', key, enc.encode(signedPayload));
  const expected = Array.from(new Uint8Array(sigBytes)).map(b => b.toString(16).padStart(2, '0')).join('');

  // Constant-time comparison
  if (expected.length !== signature.length) return false;
  let diff = 0;
  for (let i = 0; i < expected.length; i++) {
    diff |= expected.charCodeAt(i) ^ signature.charCodeAt(i);
  }
  return diff === 0;
}
