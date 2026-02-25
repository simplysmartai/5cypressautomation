/**
 * Cloudflare Pages Function: GET /api/leads
 *
 * Returns all leads stored in KV. Protected by a Bearer token.
 *
 * Required env secrets:
 *   ADMIN_TOKEN          — Bearer token for authorization (keep this secret)
 *   CALENDLY_LEADS_KV    — KV namespace binding
 *
 * Usage:
 *   curl -H "Authorization: Bearer <ADMIN_TOKEN>" https://5cypress.com/api/leads
 */

export async function onRequestGet({ request, env }) {
  // Auth check
  const authHeader = request.headers.get('Authorization') || '';
  const token = authHeader.replace('Bearer ', '').trim();
  const adminToken = env.ADMIN_TOKEN;

  if (!adminToken || token !== adminToken) {
    return new Response(JSON.stringify({ error: 'Unauthorized' }), {
      status: 401,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // Requires KV binding
  if (!env.CALENDLY_LEADS_KV) {
    return new Response(JSON.stringify({ error: 'KV not bound — leads unavailable' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }

  // List all leads from KV
  const list = await env.CALENDLY_LEADS_KV.list({ prefix: 'lead:' });
  const leads = await Promise.all(
    list.keys.map(async ({ name }) => {
      const raw = await env.CALENDLY_LEADS_KV.get(name);
      try { return JSON.parse(raw); } catch { return null; }
    })
  );

  const filtered = leads.filter(Boolean).sort(
    (a, b) => new Date(b.createdAt) - new Date(a.createdAt)
  );

  return new Response(JSON.stringify({ count: filtered.length, leads: filtered }), {
    status: 200,
    headers: { 'Content-Type': 'application/json' }
  });
}
