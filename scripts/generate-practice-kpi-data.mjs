/**
 * generate-practice-kpi-data.mjs
 * Seeded synthetic dataset for the public Practice KPI demo dashboard (/demo).
 *
 * Fictional 4-partner CPA firm ("Meridian & Vale CPAs") — 24 months of
 * per-partner billings, realization, utilization, WIP, and close-days, plus a
 * current AR aging snapshot. Deterministic: same seed → same data, so the demo
 * is regenerable and numbers quoted in outreach/walkthroughs stay stable.
 *
 * Run:    node scripts/generate-practice-kpi-data.mjs
 * Output: web/src/data/practiceKpiData.json
 */

import { writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const SEED = 52026; // bump to reroll the firm

// mulberry32 — small deterministic PRNG
function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a |= 0; a = (a + 0x6D2B79F5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
const rand = mulberry32(SEED);
const jitter = (base, spread) => base + (rand() * 2 - 1) * spread;
const round = (n, d = 0) => Math.round(n * 10 ** d) / 10 ** d;

// ── Firm shape ────────────────────────────────────────────────────────────────
// Four partner archetypes with different problems, so every chart has a story.
const partners = [
  {
    id: 'ellison',
    name: 'D. Ellison',
    role: 'Managing Partner',
    focus: 'Advisory & CAS',
    baseBillings: 68000,   // steady book, light seasonality
    seasonalWeight: 0.35,
    realizationBase: 0.93, // runs a clean book
    utilizationBase: 0.58, // admin load of managing the firm
    wipBase: 41000,
    wipDrift: 0.9,         // keeps WIP moving
  },
  {
    id: 'okafor',
    name: 'A. Okafor',
    role: 'Partner',
    focus: 'Tax',
    baseBillings: 74000,   // biggest book, extreme seasonality
    seasonalWeight: 1.0,
    realizationBase: 0.86, // discounts under deadline pressure
    utilizationBase: 0.71,
    wipBase: 63000,
    wipDrift: 1.15,        // WIP balloons every season
  },
  {
    id: 'reyes',
    name: 'M. Reyes',
    role: 'Partner',
    focus: 'Audit & Assurance',
    baseBillings: 58000,   // engagement-driven, spring fieldwork
    seasonalWeight: 0.6,
    realizationBase: 0.89,
    utilizationBase: 0.66,
    wipBase: 52000,
    wipDrift: 1.0,
  },
  {
    id: 'nguyen',
    name: 'T. Nguyen',
    role: 'Partner (new)',
    focus: 'Client Advisory',
    baseBillings: 31000,   // growing book, worst collections habits
    seasonalWeight: 0.4,
    realizationBase: 0.81, // under-bills to win clients
    utilizationBase: 0.74,
    wipBase: 34000,
    wipDrift: 1.3,         // the firm's WIP problem child
    growth: 0.022,         // fast MoM book growth
  },
];

// Tax-season curve by calendar month (1-indexed). Feb–Apr spike, Sep–Oct mini
// spike (extension season), summer trough.
const SEASONALITY = {
  1: 1.06, 2: 1.32, 3: 1.58, 4: 1.44, 5: 0.96, 6: 0.85,
  7: 0.82, 8: 0.86, 9: 1.08, 10: 1.12, 11: 0.94, 12: 1.02,
};

const MONTHS = 24;
const START = { year: 2024, month: 7 }; // Jul 2024 → Jun 2026
const FIRM_GROWTH = 0.007; // ~8.7% annualized

const monthLabel = (y, m) =>
  `${['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][m - 1]} ${String(y).slice(2)}`;

const months = [];
for (let i = 0; i < MONTHS; i++) {
  const m = ((START.month - 1 + i) % 12) + 1;
  const y = START.year + Math.floor((START.month - 1 + i) / 12);
  months.push({ index: i, year: y, month: m, label: monthLabel(y, m) });
}

// ── Per-partner monthly series ────────────────────────────────────────────────
for (const p of partners) {
  p.series = months.map(({ index, month }) => {
    const season = 1 + (SEASONALITY[month] - 1) * p.seasonalWeight;
    const growth = (1 + FIRM_GROWTH + (p.growth ?? 0)) ** index;
    const billings = jitter(p.baseBillings * season * growth, p.baseBillings * 0.05);

    // Realization dips when the season is hot (write-downs under pressure)
    const seasonPenalty = (season - 1) * 0.055;
    const realization = Math.min(0.97, jitter(p.realizationBase - seasonPenalty, 0.012));

    // Utilization rises with the season
    const utilization = Math.min(0.92, jitter(p.utilizationBase + (season - 1) * 0.16, 0.02));

    // WIP builds during the season, bleeds off after (lagged by drift habit)
    const wip = jitter(p.wipBase * (1 + (season - 1) * 0.75) * p.wipDrift * growth ** 0.5, p.wipBase * 0.07);

    // Days to close the month's books — worse in season, worse for WIP-heavy partners
    const closeDays = Math.max(4, round(jitter(6.5 + (season - 1) * 5.5 + (p.wipDrift - 1) * 4, 0.8), 1));

    return {
      billings: round(billings),
      realization: round(realization, 3),
      utilization: round(utilization, 3),
      wip: round(wip),
      closeDays,
    };
  });
}

// ── Firm-level rollups ────────────────────────────────────────────────────────
const firmSeries = months.map((m, i) => {
  const rows = partners.map((p) => p.series[i]);
  const billings = rows.reduce((s, r) => s + r.billings, 0);
  const wip = rows.reduce((s, r) => s + r.wip, 0);
  const weight = rows.reduce((s, r) => s + r.billings, 0);
  const realization = rows.reduce((s, r) => s + r.realization * r.billings, 0) / weight;
  const utilization = rows.reduce((s, r) => s + r.utilization, 0) / rows.length;
  const closeDays = Math.max(...rows.map((r) => r.closeDays));
  return {
    label: m.label,
    billings: round(billings),
    realization: round(realization, 3),
    utilization: round(utilization, 3),
    wip: round(wip),
    closeDays,
  };
});

// ── AR aging snapshot (current) ───────────────────────────────────────────────
// Roughly one month of firm billings outstanding, skewed by partner habits.
const arAging = partners.map((p) => {
  const monthly = p.series[MONTHS - 1].billings;
  const laxity = p.wipDrift; // collections habits track WIP habits
  const current = jitter(monthly * 0.52, monthly * 0.05);
  const d30 = jitter(monthly * 0.24 * laxity, monthly * 0.04);
  const d60 = jitter(monthly * 0.11 * laxity ** 1.5, monthly * 0.03);
  const d90 = jitter(monthly * 0.05 * laxity ** 2.2, monthly * 0.02);
  return {
    partnerId: p.id,
    buckets: [round(current), round(d30), round(d60), round(d90)],
  };
});

// ── Assemble ──────────────────────────────────────────────────────────────────
const out = {
  meta: {
    firmName: 'Meridian & Vale CPAs',
    disclaimer: 'Fictional demo firm. Every number on this page is synthetic and regenerable from a seeded script.',
    seed: SEED,
    generatedAt: new Date().toISOString().slice(0, 10),
    months: months.map((m) => m.label),
    arBuckets: ['Current', '31–60', '61–90', '90+'],
    targets: { realization: 0.9, utilization: 0.68, closeDays: 8 },
  },
  partners: partners.map(({ id, name, role, focus, series }) => ({ id, name, role, focus, series })),
  firm: firmSeries,
  arAging,
};

const here = dirname(fileURLToPath(import.meta.url));
const dest = join(here, '..', 'web', 'src', 'data', 'practiceKpiData.json');
writeFileSync(dest, JSON.stringify(out, null, 2));

const last = firmSeries[MONTHS - 1];
console.log(`✓ wrote ${dest}`);
console.log(`  latest month: ${last.label} — billings $${last.billings.toLocaleString()}, realization ${(last.realization * 100).toFixed(1)}%, WIP $${last.wip.toLocaleString()}`);
