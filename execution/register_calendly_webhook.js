#!/usr/bin/env node
/**
 * register_calendly_webhook.js
 *
 * One-time script to register a Calendly webhook subscription for the
 * invitee.created and invitee.canceled events.
 *
 * Prerequisites:
 *   - CALENDLY_TOKEN set in .env (your Personal Access Token)
 *   - CALENDLY_WEBHOOK_URL set in .env  OR passed as an arg
 *     Example: https://yourapp.com/api/webhooks/calendly
 *
 * Usage:
 *   node execution/register_calendly_webhook.js
 *   node execution/register_calendly_webhook.js https://yourapp.com/api/webhooks/calendly
 *
 * After running, copy the printed signing_key value into .env as:
 *   CALENDLY_WEBHOOK_SIGNING_KEY=<value>
 */

'use strict';

require('dotenv').config();

const https = require('https');

const PAT    = process.env.CALENDLY_TOKEN;
const BASE   = 'https://api.calendly.com';
const EVENTS = ['invitee.created', 'invitee.canceled'];

if (!PAT) {
  console.error('❌  CALENDLY_TOKEN is not set in .env');
  process.exit(1);
}

// Webhook callback URL: CLI arg or env var
const WEBHOOK_URL = process.argv[2] || process.env.CALENDLY_WEBHOOK_URL;
if (!WEBHOOK_URL) {
  console.error('❌  Provide the webhook URL as an argument or set CALENDLY_WEBHOOK_URL in .env');
  console.error('    Example: node execution/register_calendly_webhook.js https://yourapp.com/api/webhooks/calendly');
  process.exit(1);
}

// ── Helpers ──────────────────────────────────────────────────────────────────

function apiRequest(method, urlPath, body = null) {
  return new Promise((resolve, reject) => {
    const payload = body ? JSON.stringify(body) : null;
    const url = new URL(urlPath, BASE);
    const options = {
      hostname: url.hostname,
      path: url.pathname + url.search,
      method,
      headers: {
        Authorization: `Bearer ${PAT}`,
        'Content-Type': 'application/json',
        ...(payload ? { 'Content-Length': Buffer.byteLength(payload) } : {})
      }
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => (data += chunk));
      res.on('end', () => {
        try {
          const parsed = JSON.parse(data);
          if (res.statusCode >= 400) {
            reject(new Error(`HTTP ${res.statusCode}: ${JSON.stringify(parsed)}`));
          } else {
            resolve(parsed);
          }
        } catch {
          reject(new Error(`Non-JSON response (${res.statusCode}): ${data}`));
        }
      });
    });

    req.on('error', reject);
    if (payload) req.write(payload);
    req.end();
  });
}

// ── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  console.log('🔍  Fetching Calendly user info...');
  const me = await apiRequest('GET', '/users/me');
  const userUri = me?.resource?.uri;
  const orgUri  = me?.resource?.current_organization;

  if (!userUri) {
    throw new Error('Could not retrieve user URI from /users/me response');
  }

  console.log(`✅  User URI: ${userUri}`);
  console.log(`✅  Org URI:  ${orgUri}`);

  // List existing subscriptions so we don't create duplicates
  console.log('\n🔍  Checking for existing webhook subscriptions...');
  let existing;
  try {
    existing = await apiRequest('GET', `/webhook_subscriptions?organization=${encodeURIComponent(orgUri)}&user=${encodeURIComponent(userUri)}&scope=user`);
  } catch (e) {
    existing = { collection: [] };
  }

  const duplicate = (existing?.collection || []).find(
    s => s.callback_url === WEBHOOK_URL
  );

  if (duplicate) {
    console.log(`⚠️   Webhook already registered for ${WEBHOOK_URL}`);
    console.log(`    UUID:        ${duplicate.uri.split('/').pop()}`);
    console.log(`    State:       ${duplicate.state}`);
    console.log(`    Signing key: ${duplicate.signing_key || '(not shown in list — check Calendly dashboard)'}`);
    console.log('\nNothing to do. If you need the signing key, check your Calendly Developer dashboard.');
    return;
  }

  console.log(`\n📡  Registering webhook → ${WEBHOOK_URL}`);

  const result = await apiRequest('POST', '/webhook_subscriptions', {
    url: WEBHOOK_URL,
    events: EVENTS,
    organization: orgUri,
    user: userUri,
    scope: 'user'
  });

  const sub = result?.resource;
  if (!sub) throw new Error('Unexpected response from webhook registration: ' + JSON.stringify(result));

  console.log('\n╔══════════════════════════════════════════════════════════╗');
  console.log('║   ✅  Calendly Webhook Registered Successfully!          ║');
  console.log('╠══════════════════════════════════════════════════════════╣');
  console.log(`║  UUID:         ${sub.uri.split('/').pop().padEnd(40)}║`);
  console.log(`║  Callback URL: ${WEBHOOK_URL.substring(0, 40).padEnd(40)}║`);
  console.log(`║  Events:       ${EVENTS.join(', ').substring(0, 40).padEnd(40)}║`);
  console.log(`║  State:        ${(sub.state || '').padEnd(40)}║`);
  console.log('╠══════════════════════════════════════════════════════════╣');
  console.log(`║  Signing Key:  ${(sub.signing_key || '').substring(0, 40).padEnd(40)}║`);
  console.log('╚══════════════════════════════════════════════════════════╝');

  if (sub.signing_key) {
    console.log('\n👉  Add this to your .env file:');
    console.log(`    CALENDLY_WEBHOOK_SIGNING_KEY=${sub.signing_key}\n`);
  } else {
    console.log('\n⚠️   No signing_key in response. Check the Calendly developer dashboard for the key.');
  }
}

main().catch(err => {
  console.error('❌  Registration failed:', err.message);
  process.exit(1);
});
