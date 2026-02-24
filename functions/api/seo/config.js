// GET /api/seo/config — returns live API status to the frontend
export async function onRequestGet(context) {
  const { env } = context;

  const cors = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'application/json',
  };

  return new Response(JSON.stringify({
    dataforseo_enabled: !!(env.DATAFORSEO_USERNAME && env.DATAFORSEO_PASSWORD),
    pagespeed_enabled:  !!(env.GOOGLE_PAGESPEED_API_KEY),
    stripe_enabled:     !!(env.STRIPE_SECRET_KEY),
    resend_enabled:     !!(env.RESEND_API_KEY),
    calendly_url:       env.CALENDLY_URL || '',
    brand:              '5 Cypress Automation',
    is_admin:           false,
    env:                'cloudflare-pages',
  }), { status: 200, headers: cors });
}

export async function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
