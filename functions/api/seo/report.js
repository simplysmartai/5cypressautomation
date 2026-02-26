/**
 * GET /api/seo/report?session_id={id}
 * 
 * Returns the enriched premium SEO report after Stripe payment is verified.
 * 
 * Authentication:
 *   - Paid users: ?session_id={stripe_session_id} (verified in KV as status='paid')
 *   - Admin: Authorization: Basic {b64(ADMIN_USER:ADMIN_PASS)} — bypasses payment,
 *            runs full enrichment inline for any domain provided via ?domain={domain}
 * 
 * Response states:
 *   200 — { status: 'ready', enriched: {...} }
 *   202 — { status: 'processing' } — webhook hasn't finished yet, retry in 5s
 *   402 — { status: 'unpaid' } — session exists but not paid
 *   404 — { status: 'not_found' } — unknown session_id
 * 
 * Admin response (bypasses all payment checks):
 *   200 — { status: 'ready', enriched: {...}, admin: true }
 */

import { enrichReport } from '../../lib/seo-enrich.js';

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
        'Access-Control-Allow-Methods': 'GET, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type, Authorization',
      },
    });
  }

  if (request.method !== 'GET') return err('Method not allowed', 405);

  const url    = new URL(request.url);
  const sid    = url.searchParams.get('session_id');
  const domain = url.searchParams.get('domain');

  // ── Admin bypass  ─────────────────────────────────────────────────────────
  const isAdmin = checkAdminAuth(request, env);
  if (isAdmin) {
    return handleAdminRequest(domain, sid, env);
  }

  // ── Paid user flow ────────────────────────────────────────────────────────
  if (!sid) return err('session_id is required', 400);
  if (!env.SEO_AUDITS_KV) return err('Storage not configured', 500);

  // Check if report is ready
  const reportRaw = await env.SEO_AUDITS_KV.get(`report:${sid}`);
  if (reportRaw) {
    const report = JSON.parse(reportRaw);
    return new Response(JSON.stringify({ status: 'ready', ...report }), {
      status: 200,
      headers: CORS,
    });
  }

  // Check session payment status
  const sessionRaw = await env.SEO_AUDITS_KV.get(`session:${sid}`);
  if (!sessionRaw) {
    return new Response(JSON.stringify({ status: 'not_found', message: 'Session not found. This link may have expired.' }), {
      status: 404,
      headers: CORS,
    });
  }

  const session = JSON.parse(sessionRaw);
  if (session.status !== 'paid') {
    return new Response(JSON.stringify({ status: 'unpaid', message: 'Payment not yet confirmed. Please complete payment first.' }), {
      status: 402,
      headers: CORS,
    });
  }

  // Paid but not yet enriched (webhook still processing)
  return new Response(JSON.stringify({ status: 'processing', message: 'Your report is being generated. This usually takes 10–30 seconds.' }), {
    status: 202,
    headers: CORS,
  });
}

/**
 * Admin: generate enriched report on-demand without payment check.
 * If a session_id is provided, try to load that report from KV first.
 * Otherwise run enrichment inline using audit data if available.
 */
async function handleAdminRequest(domain, sid, env) {
  // If session_id provided, return existing report
  if (sid && env.SEO_AUDITS_KV) {
    const reportRaw = await env.SEO_AUDITS_KV.get(`report:${sid}`);
    if (reportRaw) {
      const report = JSON.parse(reportRaw);
      return new Response(JSON.stringify({ status: 'ready', admin: true, ...report }), {
        status: 200,
        headers: CORS,
      });
    }
  }

  // Admin with domain but no stored data: return empty enrichment scaffold
  // (Frontend calls analyze.js first, then stores audit_id, then calls this)
  if (!domain) {
    return new Response(JSON.stringify({
      status: 'ready',
      admin: true,
      domain: 'N/A',
      enriched: {
        executive_summary: 'Run a scan first, then the report will populate here.',
        overall_grade: 'N/A',
        findings: [],
        quick_wins: [],
        roadmap: { phase1: { label: '', focus: '', tasks: [] }, phase2: { label: '', focus: '', tasks: [] }, phase3: { label: '', focus: '', tasks: [] } },
        keyword_strategy: '',
        backlink_insight: '',
      },
    }), { status: 200, headers: CORS });
  }

  // Try to find latest audit for this domain in KV
  // (audit_id is passed from frontend via ?audit_id param)
  const url = new URL(domain.startsWith('http') ? domain : `https://${domain}`);
  const auditIdParam = new URL('https://x.com?' + (env.__request_url_search || '')).searchParams.get('audit_id');

  let auditData = null;
  if (auditIdParam && env.SEO_AUDITS_KV) {
    const raw = await env.SEO_AUDITS_KV.get(`audit:${auditIdParam}`);
    if (raw) {
      try { const parsed = JSON.parse(raw); auditData = parsed.data || parsed; } catch {}
    }
  }

  if (!auditData) {
    auditData = { domain: url.hostname, score: 0, full_report: { on_page: [], technical: [] }, page_speed: {}, keywords: [], backlinks: {} };
  }

  let enriched;
  try {
    enriched = await enrichReport(auditData, env);
  } catch (e) {
    return err(`Enrichment failed: ${e.message}`, 500);
  }

  const reportPayload = {
    session_id: sid || 'admin',
    domain: url.hostname,
    admin: true,
    paid_at: new Date().toISOString(),
    enriched,
    status: 'ready',
  };

  // Cache in KV if session_id provided
  if (sid && env.SEO_AUDITS_KV) {
    await env.SEO_AUDITS_KV.put(`report:${sid}`, JSON.stringify(reportPayload), { expirationTtl: 86400 });
  }

  return new Response(JSON.stringify({ status: 'ready', ...reportPayload }), {
    status: 200,
    headers: CORS,
  });
}

function checkAdminAuth(request, env) {
  const authHeader = request.headers.get('Authorization') || '';
  if (!authHeader.startsWith('Basic ')) return false;
  try {
    const decoded = atob(authHeader.slice(6));
    const [user, pass] = decoded.split(':');
    return user === env.ADMIN_USER && pass === env.ADMIN_PASS;
  } catch {
    return false;
  }
}

function err(msg, status = 400) {
  return new Response(JSON.stringify({ error: msg }), { status, headers: CORS });
}
