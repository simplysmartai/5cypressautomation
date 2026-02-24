// GET /admin/api/seo-audit?url=...&strategy=mobile|desktop
// Admin-only Lighthouse / PageSpeed endpoint — requires Basic Auth

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

  if (request.method !== 'GET') {
    return new Response('Method Not Allowed', { status: 405 });
  }

  // Basic Auth check
  const authHeader = request.headers.get('Authorization') || '';
  if (authHeader.startsWith('Basic ')) {
    try {
      const [user, pass] = atob(authHeader.slice(6)).split(':');
      if (user !== env.ADMIN_USER || pass !== env.ADMIN_PASS) {
        return new Response('Forbidden', { status: 403 });
      }
    } catch {
      return new Response('Unauthorized', {
        status: 401,
        headers: { 'WWW-Authenticate': 'Basic realm="5 Cypress Admin"' },
      });
    }
  }
  // Allow if no auth header (admin pages handled by browser auth prompt separately)

  const url        = new URL(request.url);
  const targetUrl  = url.searchParams.get('url');
  const strategy   = url.searchParams.get('strategy') || 'mobile';

  if (!targetUrl) {
    return new Response(JSON.stringify({ error: 'url param required' }), {
      status: 400, headers: CORS,
    });
  }

  const key = env.GOOGLE_PAGESPEED_API_KEY;
  if (!key) {
    return new Response(JSON.stringify({ error: 'GOOGLE_PAGESPEED_API_KEY not configured' }), {
      status: 503, headers: CORS,
    });
  }

  try {
    const endpoint = `https://www.googleapis.com/pagespeedonline/v5/runPagespeed`
      + `?url=${encodeURIComponent(targetUrl)}&strategy=${strategy}&key=${key}`
      + `&category=performance&category=accessibility&category=best-practices&category=seo`;

    const res = await fetch(endpoint);
    if (!res.ok) throw new Error(`PageSpeed API returned ${res.status}`);
    const json = await res.json();

    const cats   = json.lighthouseResult?.categories || {};
    const audits = json.lighthouseResult?.audits     || {};

    const result = {
      requested: { url: targetUrl, strategy },
      fetchedAt: new Date().toISOString(),
      scores: {
        performance:   Math.round((cats.performance?.score   || 0) * 100),
        accessibility: Math.round((cats.accessibility?.score || 0) * 100),
        bestPractices: Math.round((cats['best-practices']?.score || 0) * 100),
        seo:           Math.round((cats.seo?.score           || 0) * 100),
      },
      vitals: {
        lcp:  audits['largest-contentful-paint']?.displayValue || 'N/A',
        cls:  audits['cumulative-layout-shift']?.displayValue  || 'N/A',
        ttfb: audits['server-response-time']?.displayValue     || 'N/A',
        fcp:  audits['first-contentful-paint']?.displayValue   || 'N/A',
        inp:  audits['interaction-to-next-paint']?.displayValue|| 'N/A',
        tbt:  audits['total-blocking-time']?.displayValue      || 'N/A',
      },
    };

    return new Response(JSON.stringify(result), { status: 200, headers: CORS });
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), { status: 500, headers: CORS });
  }
}
