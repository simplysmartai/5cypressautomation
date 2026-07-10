# Homepage Motion Pass — Decisions Log

One line per judgment call made during the GSAP/Lenis motion upgrade.

## Phase A — Motion infrastructure
- Moved ALL of Layout.astro's inline JS (reveal, magnetic, ripple, modal open) into `src/scripts/motion.ts` — one module, one reduced-motion gate; Layout's `<script>` just imports it.
- Reveal refactor keeps the existing `.reveal`/`.reveal-stagger` classes and CSS; ScrollTrigger.batch just swaps the IntersectionObserver as the driver (zero per-page markup churn).
- Modal↔Lenis interop done with a MutationObserver on `#booking-modal`'s class instead of editing BookingModal.astro — freezes/unfreezes scroll however the modal opens or closes.
- Ripple kept active under reduced-motion (click feedback, not vestibular motion); magnetic + Lenis + all scroll tweens are gated off.
- Added the minimal Lenis CSS to global.css (self-contained) rather than importing `lenis/dist/lenis.css`, to avoid coupling to the package's dist path.
- `.js` flag added via an inline `<head>` script so reveal hidden-states (`.js .reveal`) never apply when JS is off/disabled.

## Phase B — Hero cashflow chart
- Extracted the hero visual to `components/HeroCashflowChart.astro`, importing `chartSvg.ts` + `cashflowForecastData.json` (no duplicated data/paths).
- Hero chart is **display-only** (no tooltips): the full interactive/tooltip version lives on `/dashboards/cashflow-forecast/`, and the whole card links there.
- Draw choreography is **pure CSS** (`prefers-reduced-motion`-gated), not GSAP: actual line draws via `pathLength="1"` + stroke-dashoffset; band/reserve/today/projection fade in after. Keeps it independent of JS timing and reduced-motion-correct for free.
- KPI numbers reuse the existing `[data-count]` tick-up (index.astro observer) — chose 3 readouts that frame the "will I have enough cash" story: Current cash, 13-wk projected low, Reserve floor.
- Removed `.reveal` from `.hero-copy` and `.hero-visual`; hero now enters via CSS keyframes so the parallax GSAP transform on `.hero-visual` doesn't fight a reveal transform. The h1 (LCP) uses a transform-only keyframe (`heroRiseSolid`) so it never paints at opacity 0.
- Hero scroll effect = single subtle parallax drift (`yPercent: 6`, scrubbed) in motion.ts — chose parallax over scale-down.
- Chart colors `#199E70` (line) and `#101014` (card bg) are NOT new palette: they're the established data-line / card-surface values already used across the live dashboards (cashflow-forecast.astro etc.). Reusing them keeps the hero chart visually identical to the real dashboard it links to.

## Phase C — Body scroll choreography
- Delivered via the Phase A reveal refactor: all body sections already carry `.reveal`/`.reveal-stagger`, now ScrollTrigger-driven (staggered card reveals, headers settle in), and stats/demo numbers count up via the existing `[data-count]` observer.
- Deliberately did NOT add bespoke per-section GSAP timelines — the shared reveal system already satisfies the "play once, restrained, token durations" rules, and extra timelines would be more surface area for no visible gain (restraint + surgical-change principle).

## Phase E — Ambient hero background
- SKIPPED. The brief makes skipping the expected outcome on any performance doubt; the existing film-grain + gradient-mesh already give the hero atmosphere, and adding an animated layer risks the Lighthouse ≥90 budget for no clear payoff.

## Punch list — deferred / unverified (nothing silently dropped)
- **Phase E (ambient background): skipped** — see above. Re-open only if a perf pass shows headroom.
- **`astro check` (full TS type gate) not run** — `@astrojs/check` + `typescript` are not project deps and installing them was out of scope. Relied on the clean `astro build` (esbuild compiles motion.ts + every .astro frontmatter; a real error would fail it). To add a strict type gate: `npm i -D @astrojs/check typescript`.
- **Lighthouse not run** — no confirmed headless Chrome in this environment. Bundle delta instead: the two libs bundle into ONE deferred ~132 KB (~45 KB gzip) JS chunk that never blocks paint; the LCP element (hero `<h1>`) is static server-rendered HTML/CSS. Perf-budget risk is low but should be confirmed with a real Lighthouse pass on `npm run preview`.
- **Live browser checks pending** — responsive (360/768/1440), reduced-motion, no-JS, hero-chart tooltips on `/dashboards/cashflow-forecast/`, modal↔Lenis freeze, and `#workflows`/`#faq` anchors are all handled by construction and verified against the built HTML, but were NOT driven in a real browser here. Recommend a 5-minute manual `npm --prefix web run preview` sweep before shipping.
- **Nav has no in-page `#` anchors** — the anchor→`lenis.scrollTo` handler is in place for any `#`-links (e.g. the FAQ/workflows section ids) but nothing currently links to them from the nav, so that path is untested in practice.

## 2026-07-09 — Full fractional-analyst repositioning pivot

Context: Fable audit flagged the site as reading like a workflow-automation agency, not a
fractional data analyst practice. Founder (Jim) chose a full analyst pivot. Four load-bearing
calls confirmed with Jim before building:

- **Integrity precursor:** the "10+ yrs / a decade" experience claim was a past-build
  fabrication. Corrected sitewide to the true figure — **five years in data analyst / BI roles
  across the telecom (Verizon) and government (U.S. Army) sectors.** Employers, not clients, so
  copy abstracts to sectors. Bank of America / Infinity (data-entry, ~20 yrs ago) deliberately
  excluded from the credential line.
- **Retainer = three tiers by refresh cadence** (per CLAUDE.md §1). Proposed prices to build
  against, AWAITING JIM'S SIGN-OFF: Standard **$600/mo** (daily), Plus **$1,200/mo** (3–8×/day),
  Premium **$2,500/mo** (near-real-time); all include a monthly insight review. Placeholders.
- **Sitewide CTA = "Book a fit call"** (was "Map My Workflow"). Matches CLAUDE.md Phase 1.
- **Automation pages cut from primary surfaces (homepage/nav/footer); URLs stay live.**
  DEVIATION: kept one discreet crawl link to the automation services at the bottom of `/services`
  so Google doesn't deindex them (Jim chose to preserve their SEO). Remove for zero internal links.
- **Brand: tagline rebrand, entity name kept.** Logo subtitle `AUTOMATION` → `DATA ANALYTICS`;
  positioning copy goes fractional-analyst. Legal name "5 Cypress Automation" retained in
  schema/footer/copyright — entity rename is a separate move.
- **Hero H1:** the praised "Your team is not slow. The handoffs are." line is automation-framed;
  replaced with an analyst-decision H1, handoff idea preserved lower on the page.
- **Founding-slots counter:** "5 of 5 founding slots open" advertised zero clients; reframed to a
  limited-time founding rate with no zero-count exposure (Fable fix).
