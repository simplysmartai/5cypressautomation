/**
 * POST /api/contact — Cloudflare Pages Function
 *
 * Production handler for the fit-call/booking form (BookingModal.astro).
 * Defense in depth (see directives/prevent_contact_form_spam.md):
 *   1. Method + content-type + body-size guards
 *   2. Same-origin check (blocks cross-site form abuse)
 *   3. Honeypot + submission-timing check (blocks fast/direct bots)
 *   4. Keyword/link spam heuristics + strict field validation
 *   5. Per-IP rate limiting (KV, graceful no-op if unbound)
 *   6. Cloudflare Turnstile verification (graceful skip if secret unset)
 * Then: team notification + instant prospect autoresponder via Resend.
 *
 * Required Pages secret: RESEND_API_KEY
 * Optional (recommended, drop-in when provisioned):
 *   - RATE_LIMIT   : KV namespace binding for per-IP throttling
 *   - TURNSTILE_SECRET : enables server-side Turnstile verification
 * No storage yet — pipeline capture (D1/KV + ops/PIPELINE.md) is Phase 3.
 */

interface Env {
  RESEND_API_KEY: string;
  RATE_LIMIT?: KVNamespace;
  TURNSTILE_SECRET?: string;
}

interface ContactPayload {
  name?: string;
  email?: string;
  company?: string;
  challenge?: string;
  timeline?: string;
  website?: string; // honeypot — must be blank
  t?: number | string; // client render timestamp (ms) for timing check
  turnstileToken?: string;
  source?: string;
}

const NOTIFY_TO = 'jimmy@5cypress.com';
const NOTIFY_CC = 'nick@5cypress.com';
const FROM_INTERNAL = '5 Cypress Leads <admin@5cypress.com>';
const FROM_PROSPECT = '5 Cypress <nick@5cypress.com>';

// Same-origin allowlist. Requests carrying a mismatched Origin/Referer are dropped.
const ALLOWED_HOSTS = ['5cypress.com', 'www.5cypress.com', 'localhost', '127.0.0.1'];

// Throttling + timing thresholds.
const MAX_PER_HOUR = 5;
const MIN_FILL_MS = 3000; // humans take >3s to fill the form
const MAX_AGE_MS = 60 * 60 * 1000; // stale page / replayed token
const MAX_BODY_BYTES = 10_000;

const SPAM_KEYWORDS = [
  'casino', 'poker', 'viagra', 'cialis', 'pharmacy', 'bitcoin', 'crypto',
  'forex', 'trading', 'loan', 'mortgage', 'weight loss', 'diet', 'pill',
  'xxx', 'adult', 'gambling', 'replica', 'counterfeit', 'discount',
  'wholesale', 'dropship', 'backlink', 'seo services', 'increase traffic',
];

const SECURITY_HEADERS = {
  'Content-Type': 'application/json',
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'no-referrer',
  'Cache-Control': 'no-store',
};

const OK_BODY = JSON.stringify({
  success: true,
  message: "We'll be in touch within one business day.",
});

const json = (body: string, status = 200) =>
  new Response(body, { status, headers: SECURITY_HEADERS });

const fail = (message: string, status: number) =>
  json(JSON.stringify({ success: false, message }), status);

function originAllowed(request: Request): boolean {
  const raw = request.headers.get('Origin') || request.headers.get('Referer');
  if (!raw) return true; // no header present — defer to the other layers
  try {
    return ALLOWED_HOSTS.includes(new URL(raw).hostname);
  } catch {
    return false;
  }
}

function isSpam(data: ContactPayload): boolean {
  const content = `${data.name ?? ''} ${data.challenge ?? ''} ${data.company ?? ''}`.toLowerCase();
  if (SPAM_KEYWORDS.some((k) => content.includes(k))) return true;
  const urls = (data.challenge ?? '').match(/(https?:\/\/|www\.)/gi);
  return (urls?.length ?? 0) > 3;
}

function submittedTooFast(data: ContactPayload): boolean {
  const t = Number(data.t);
  if (!t || Number.isNaN(t)) return false; // no timestamp — don't penalize
  const age = Date.now() - t;
  return age < MIN_FILL_MS || age > MAX_AGE_MS;
}

// Per-IP sliding throttle. No-ops safely when the KV namespace isn't bound.
async function rateLimited(env: Env, ip: string): Promise<boolean> {
  if (!env.RATE_LIMIT || !ip) return false;
  const key = `rl:${ip}`;
  const current = Number((await env.RATE_LIMIT.get(key)) ?? '0');
  if (current >= MAX_PER_HOUR) return true;
  await env.RATE_LIMIT.put(key, String(current + 1), { expirationTtl: 3600 });
  return false;
}

// Verify the Turnstile token. Skips (returns true) until the secret is provisioned.
async function turnstilePassed(env: Env, token: string | undefined, ip: string): Promise<boolean> {
  if (!env.TURNSTILE_SECRET) return true;
  if (!token) return false;
  const body = new URLSearchParams({ secret: env.TURNSTILE_SECRET, response: token });
  if (ip) body.append('remoteip', ip);
  try {
    const res = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST',
      body,
    });
    const out = (await res.json()) as { success?: boolean };
    return out.success === true;
  } catch {
    return false;
  }
}

async function sendEmail(
  apiKey: string,
  message: { from: string; to: string[]; cc?: string[]; reply_to?: string; subject: string; text: string },
): Promise<void> {
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(message),
  });
  if (!res.ok) {
    throw new Error(`Resend ${res.status}: ${await res.text()}`);
  }
}

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  // 1. Transport guards
  const contentType = request.headers.get('content-type') ?? '';
  if (!contentType.includes('application/json')) {
    return fail('Unsupported content type.', 415);
  }
  const declaredLen = Number(request.headers.get('content-length') ?? '0');
  if (declaredLen > MAX_BODY_BYTES) {
    return fail('Request too large.', 413);
  }

  // 2. Same-origin check
  if (!originAllowed(request)) {
    return fail('Forbidden.', 403);
  }

  const ip = request.headers.get('CF-Connecting-IP') ?? '';

  // 3. Rate limit (per IP)
  if (await rateLimited(env, ip)) {
    return fail('Too many requests. Please try again later, or email nick@5cypress.com.', 429);
  }

  // 4. Parse
  let data: ContactPayload;
  try {
    const raw = await request.text();
    if (raw.length > MAX_BODY_BYTES) return fail('Request too large.', 413);
    data = JSON.parse(raw);
  } catch {
    return fail('Invalid request.', 400);
  }

  const name = (data.name ?? '').trim().slice(0, 150);
  const email = (data.email ?? '').trim().slice(0, 200);
  const company = (data.company ?? '').trim().slice(0, 200);
  const challenge = (data.challenge ?? '').trim().slice(0, 2000);
  const timeline = (data.timeline ?? '').trim().slice(0, 200);

  // 5. Field validation
  if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return fail('Name and a valid email are required.', 400);
  }

  // 6. Silent bot traps — honeypot, timing, keyword/link spam.
  //    Return a success shape so bots learn nothing about what tripped them.
  if (data.website || submittedTooFast(data) || isSpam(data)) {
    return json(OK_BODY);
  }

  // 7. Turnstile (human verification) — enforced only once the secret is set.
  if (!(await turnstilePassed(env, data.turnstileToken, ip))) {
    return fail('Verification failed. Please reload and try again.', 403);
  }

  const submittedAt = new Date().toISOString();

  try {
    await sendEmail(env.RESEND_API_KEY, {
      from: FROM_INTERNAL,
      to: [NOTIFY_TO],
      cc: [NOTIFY_CC],
      reply_to: email,
      subject: `New fit-call lead: ${name}${company ? ` (${company})` : ''}`,
      text: [
        'New fit-call request from 5cypress.com',
        '',
        `Name:       ${name}`,
        `Email:      ${email}`,
        `Company:    ${company || '—'}`,
        `Focus:      ${challenge || '—'}`,
        `Timeline:   ${timeline || '—'}`,
        `Received:   ${submittedAt}`,
        '',
        'Reply to this email to respond directly to the prospect.',
        'Log it: ops/PIPELINE.md',
      ].join('\n'),
    });
  } catch (err) {
    // Notification is the one thing that must not fail silently
    console.error('[CONTACT] notification failed:', err instanceof Error ? err.message : err);
    return fail('Something went wrong. Email us at nick@5cypress.com.', 502);
  }

  try {
    await sendEmail(env.RESEND_API_KEY, {
      from: FROM_PROSPECT,
      to: [email],
      reply_to: NOTIFY_CC,
      subject: 'We got your fit-call request',
      text: [
        `Hi ${name.split(' ')[0]},`,
        '',
        'Thanks for reaching out to 5 Cypress. Your request is in.',
        '',
        'What happens next: we review what you sent and reply within one',
        'business day to schedule a short fit call — a look at the numbers',
        'you can never see in time and whether a dashboard or forecast',
        'would help. No pitch deck, no obligation.',
        '',
        'If it is easier, just reply to this email and tell us more about',
        'the decision you keep making late.',
        '',
        '— 5 Cypress',
        'www.5cypress.com | nick@5cypress.com',
      ].join('\n'),
    });
  } catch (err) {
    // Prospect got captured; autoresponder failure shouldn't fail the request
    console.error('[CONTACT] autoresponder failed:', err instanceof Error ? err.message : err);
  }

  return json(OK_BODY);
};
