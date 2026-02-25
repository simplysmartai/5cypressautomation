/**
 * Cloudflare Pages Function: POST /api/lead-capture
 *
 * Manual lead capture form (not Calendly — the booking modal on the site).
 * Validates input, sends notification email, and optionally stores in KV.
 *
 * Required env secrets:
 *   RESEND_API_KEY
 *   DEFAULT_FROM
 *
 * Optional:
 *   CALENDLY_LEADS_KV   — KV namespace for persistence
 */

function corsHeaders() {
  return {
    'Access-Control-Allow-Origin': 'https://5cypress.com',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Content-Type': 'application/json'
  };
}

export async function onRequestOptions() {
  return new Response(null, { status: 204, headers: corsHeaders() });
}

export async function onRequestPost({ request, env }) {
  let data;
  try {
    data = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: 'Invalid JSON' }), {
      status: 400, headers: corsHeaders()
    });
  }

  const { name, email, source, service } = data;

  if (!name || !email) {
    return new Response(JSON.stringify({ error: 'Missing required fields: name, email' }), {
      status: 400, headers: corsHeaders()
    });
  }

  // Basic email format check
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return new Response(JSON.stringify({ error: 'Invalid email format' }), {
      status: 400, headers: corsHeaders()
    });
  }

  const lead = {
    id: `form_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
    name: name.substring(0, 100),
    email: email.toLowerCase().substring(0, 254),
    source: (source || 'website_form').substring(0, 50),
    service: (service || 'general').substring(0, 100),
    status: 'new',
    createdAt: new Date().toISOString()
  };

  // Send notification email
  if (env.RESEND_API_KEY) {
    await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.RESEND_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: `5 Cypress <${env.DEFAULT_FROM || 'nick@5cypress.com'}>`,
        to: 'nick@5cypress.com',
        reply_to: lead.email,
        subject: `🎯 New Lead: ${lead.name}`,
        html: `
          <div style="font-family:sans-serif;max-width:560px;margin:auto">
            <h2 style="color:#5d8c5d">New Lead Captured</h2>
            <table style="width:100%;border-collapse:collapse">
              <tr><td style="padding:8px;color:#666;width:100px"><strong>Name</strong></td><td style="padding:8px">${lead.name}</td></tr>
              <tr><td style="padding:8px;color:#666"><strong>Email</strong></td><td style="padding:8px"><a href="mailto:${lead.email}">${lead.email}</a></td></tr>
              <tr><td style="padding:8px;color:#666"><strong>Service</strong></td><td style="padding:8px">${lead.service}</td></tr>
              <tr><td style="padding:8px;color:#666"><strong>Source</strong></td><td style="padding:8px">${lead.source}</td></tr>
            </table>
            <hr style="border:0;border-top:1px solid #eee;margin:24px 0"/>
            <p style="color:#999;font-size:0.8em">5 Cypress lead capture · 5cypress.com</p>
          </div>
        `
      })
    }).catch(err => console.error('[LeadCapture] Email error:', err));
  }

  // Persist to KV if bound
  if (env.CALENDLY_LEADS_KV) {
    await env.CALENDLY_LEADS_KV.put(`lead:${lead.id}`, JSON.stringify(lead), {
      expirationTtl: 60 * 60 * 24 * 90
    }).catch(err => console.error('[LeadCapture] KV error:', err));
  }

  return new Response(JSON.stringify({ success: true, message: 'Lead captured' }), {
    status: 201, headers: corsHeaders()
  });
}
