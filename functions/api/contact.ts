/**
 * POST /api/contact — Cloudflare Pages Function
 *
 * Production handler for the fit-call/booking form (BookingModal.astro).
 * Mirrors the Express dev handler in routes/api-leads.js: honeypot, spam
 * guard, team notification. Adds an instant autoresponder to the prospect.
 *
 * Required Pages secret: RESEND_API_KEY
 * No storage yet — pipeline capture (D1/KV + ops/PIPELINE.md) is Phase 3.
 */

interface Env {
  RESEND_API_KEY: string;
}

interface ContactPayload {
  name?: string;
  email?: string;
  company?: string;
  challenge?: string;
  timeline?: string;
  website?: string; // honeypot — must be blank
  source?: string;
}

const NOTIFY_TO = 'jimmy@5cypress.com';
const NOTIFY_CC = 'nick@5cypress.com';
const FROM_INTERNAL = '5 Cypress Leads <admin@5cypress.com>';
const FROM_PROSPECT = '5 Cypress Automation <nick@5cypress.com>';

const SPAM_KEYWORDS = [
  'casino', 'poker', 'viagra', 'cialis', 'pharmacy', 'bitcoin', 'crypto',
  'forex', 'trading', 'loan', 'mortgage', 'weight loss', 'diet', 'pill',
  'xxx', 'adult', 'gambling', 'replica', 'counterfeit', 'discount',
  'wholesale', 'dropship', 'backlink',
];

const OK_BODY = JSON.stringify({
  success: true,
  message: "We'll be in touch within one business day.",
});

const json = (body: string, status = 200) =>
  new Response(body, {
    status,
    headers: { 'Content-Type': 'application/json' },
  });

function isSpam(data: ContactPayload): boolean {
  const content = `${data.name ?? ''} ${data.challenge ?? ''} ${data.company ?? ''}`.toLowerCase();
  if (SPAM_KEYWORDS.some((k) => content.includes(k))) return true;
  const urls = (data.challenge ?? '').match(/(https?:\/\/|www\.)/gi);
  return (urls?.length ?? 0) > 3;
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
  let data: ContactPayload;
  try {
    data = await request.json();
  } catch {
    return json(JSON.stringify({ success: false, message: 'Invalid request.' }), 400);
  }

  const name = (data.name ?? '').trim().slice(0, 150);
  const email = (data.email ?? '').trim().slice(0, 200);
  const company = (data.company ?? '').trim().slice(0, 200);
  const challenge = (data.challenge ?? '').trim().slice(0, 2000);
  const timeline = (data.timeline ?? '').trim().slice(0, 200);

  if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return json(JSON.stringify({ success: false, message: 'Name and a valid email are required.' }), 400);
  }

  // Honeypot and spam guard: pretend success so bots learn nothing
  if (data.website || isSpam(data)) {
    return json(OK_BODY);
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
        'New workflow mapping request from 5cypress.com',
        '',
        `Name:       ${name}`,
        `Email:      ${email}`,
        `Company:    ${company || '—'}`,
        `Bottleneck: ${challenge || '—'}`,
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
    return json(JSON.stringify({ success: false, message: 'Something went wrong. Email us at nick@5cypress.com.' }), 502);
  }

  try {
    await sendEmail(env.RESEND_API_KEY, {
      from: FROM_PROSPECT,
      to: [email],
      reply_to: NOTIFY_CC,
      subject: 'We got your workflow mapping request',
      text: [
        `Hi ${name.split(' ')[0]},`,
        '',
        'Thanks for reaching out to 5 Cypress Automation. Your request is in.',
        '',
        'What happens next: we review what you sent and reply within one',
        'business day to schedule a short workflow mapping call. No pitch',
        'deck, no obligation.',
        '',
        'If it is easier, just reply to this email and tell us more about',
        'the workflow that keeps slowing your team down.',
        '',
        '— 5 Cypress Automation',
        'www.5cypress.com | nick@5cypress.com',
      ].join('\n'),
    });
  } catch (err) {
    // Prospect got captured; autoresponder failure shouldn't fail the request
    console.error('[CONTACT] autoresponder failed:', err instanceof Error ? err.message : err);
  }

  return json(OK_BODY);
};
