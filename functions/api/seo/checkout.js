/**
 * POST /api/seo/checkout
 * 
 * Creates a Stripe Checkout Session for the $49 premium SEO report.
 * Stores a pending session record in KV keyed by session_id.
 * 
 * Body: { domain, email, audit_id }
 * Returns: { url } — redirect to Stripe hosted checkout
 * 
 * On success Stripe will redirect to: /seo-report.html?session_id={id}
 * A Stripe webhook at /api/seo/webhook handles fulfillment after payment.
 */

import Stripe from 'stripe';

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Content-Type': 'application/json',
};

export async function onRequest(context) {
  const { request, env } = context;

  if (request.method === 'OPTIONS') {
    return new Response(null, {
      status: 204,
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  }

  if (request.method !== 'POST') {
    return err('Method not allowed', 405);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return err('Invalid JSON body', 400);
  }

  const { domain, email, audit_id } = body;
  if (!domain) return err('domain is required', 400);

  // ── Stripe not configured: fall back to Calendly consultation ────────────
  if (!env.STRIPE_SECRET_KEY) {
    const calendlyUrl = env.CALENDLY_URL || 'https://calendly.com/jimmy-5cypress/30min';
    return new Response(JSON.stringify({
      error: 'stripe_not_configured',
      fallback: 'calendly',
      message: 'Premium report available via consultation. Book a free call instead.',
      calendly_url: calendlyUrl,
    }), { status: 402, headers: CORS });
  }

  // ── KV not configured ─────────────────────────────────────────────────────
  if (!env.SEO_AUDITS_KV) {
    return err('Storage not configured (SEO_AUDITS_KV missing)', 500);
  }

  try {
    const stripe = new Stripe(env.STRIPE_SECRET_KEY, {
      apiVersion: '2024-06-20',
    });

    const baseUrl = 'https://www.5cypress.com';
    const successUrl = `${baseUrl}/seo-report.html?session_id={CHECKOUT_SESSION_ID}&domain=${encodeURIComponent(domain)}`;
    const cancelUrl  = `${baseUrl}/seo-dashboard`;

    const session = await stripe.checkout.sessions.create({
      payment_method_types: ['card'],
      customer_email: email || undefined,
      line_items: [
        {
          price_data: {
            currency: 'usd',
            unit_amount: 4900, // $49.00
            product_data: {
              name: '5 Cypress SEO Intelligence Report',
              description: `Full technical SEO analysis for ${domain} — expert explanations, priority fix list, AI-ready prompts, and a 90-day roadmap.`,
              images: ['https://www.5cypress.com/assets/brand/logo-5cypress.jpg'],
            },
          },
          quantity: 1,
        },
      ],
      mode: 'payment',
      success_url: successUrl,
      cancel_url:  cancelUrl,
      metadata: { domain, audit_id: audit_id || '', email: email || '' },
      payment_intent_data: {
        metadata: { domain, audit_id: audit_id || '' },
      },
    });

    // Store pending session in KV (TTL: 7 days)
    await env.SEO_AUDITS_KV.put(
      `session:${session.id}`,
      JSON.stringify({ domain, email: email || '', audit_id: audit_id || '', status: 'pending', created_at: new Date().toISOString() }),
      { expirationTtl: 604800 }
    );

    return new Response(JSON.stringify({ url: session.url, session_id: session.id }), {
      status: 200,
      headers: CORS,
    });

  } catch (e) {
    console.error('[seo/checkout] Stripe error:', e.message);
    return err(`Checkout failed: ${e.message}`, 500);
  }
}

function err(msg, status = 400) {
  return new Response(JSON.stringify({ error: msg }), { status, headers: CORS });
}
