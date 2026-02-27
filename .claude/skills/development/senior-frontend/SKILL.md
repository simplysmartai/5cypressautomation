# Senior Frontend (Development)

**Version:** 1.1.0 | **Last Reviewed:** 2026-02-27 | **Review Cadence:** Every 90 days

Expert senior-level front-end engineer skill for building robust, maintainable, and high-performance user interfaces.

---

## Description

- Specializes in modern front-end architectures (React, Vue, Svelte), TypeScript, component design systems, accessibility (a11y), performance optimization, and testing strategies.
- Focus areas: app-scale state management, typed APIs, client-side performance (bundle splitting, caching, font loading strategies), Core Web Vitals (LCP, CLS, TBT, INP), SSR/ISR patterns, progressive enhancement, and developer DX (linting, CI, dev tooling).
- Always audits against the current Lighthouse version scoring weights, WCAG 2.2 AA, and the current browser support tables.

---

## When to Use

- Designing or reviewing large front-end features or entire pages.
- Auditing a site for performance, accessibility, CLS/LCP issues, or Best Practices regressions.
- Creating reusable component libraries or design system tokens.
- Implementing performance-critical pages (landing, hero, conversion funnels).
- Architecting front-end build and deployment flows (Vite, Cloudflare Pages, Wrangler).
- Reviewing CSS and HTML for anti-patterns (inline styles, duplicate loads, missing attributes, render-blocking resources).

---

## Audit Checklist (Run on Every Engagement)

### Performance
- [ ] Google Fonts loaded via `<link>` in `<head>` with `display=swap`, never via CSS `@import`
- [ ] Font preconnects set for `fonts.googleapis.com` and `fonts.gstatic.com`
- [ ] Critical above-fold images have `loading="eager"` and explicit `width`/`height`
- [ ] Below-fold images have `loading="lazy"` and explicit `width`/`height`
- [ ] No duplicate stylesheet loads (CSS @import + HTML `<link>` for the same file)
- [ ] No render-blocking third-party scripts in `<head>` without `defer` or `async`
- [ ] Unused CSS rules < 50% of any individual stylesheet
- [ ] js loaded with `type="module"` or `defer` where possible

### Accessibility (WCAG 2.2 AA)
- [ ] All interactive elements have visible focus indicators
- [ ] `aria-expanded` on disclosure/toggle buttons synced to JS open/close state
- [ ] `aria-controls` on toggle buttons referencing the controlled element's `id`
- [ ] All images have meaningful `alt` text (or `alt=""` for purely decorative)
- [ ] Color contrast ratio ≥ 4.5:1 for normal text, ≥ 3:1 for large text
- [ ] Skip-to-content link present and keyboard-focusable
- [ ] Modal/drawer traps focus and restores on close
- [ ] Escape key closes any open modal or overlay
- [ ] Form inputs have programmatically associated `<label>` elements

### HTML Quality
- [ ] `<!DOCTYPE html>` present
- [ ] `<html lang="en">` (or appropriate locale) present
- [ ] `<meta charset="UTF-8">` present
- [ ] Heading hierarchy is sequential (h1 → h2 → h3, no skips)
- [ ] No inline `<style>` blocks inside `<body>` (move to external CSS files)
- [ ] No inline `onclick=""` handlers — use `addEventListener` via JS or `data-action` hooks

### SEO
- [ ] `<title>` is unique per page and < 60 characters
- [ ] `<meta name="description">` present, unique per page, < 160 characters
- [ ] Canonical URL set
- [ ] Open Graph + Twitter Card tags on all public-facing pages
- [ ] Structured data (JSON-LD) validates on Google's Rich Results Test

---

## Outputs

- Specific, actionable code changes with before/after context and file path.
- Lighthouse score impact estimate for each suggested fix.
- Migration path if changing a broad pattern (e.g., moving from inline styles to CSS classes).
- Verification steps: live URL checks, browser devtools checks, or Lighthouse re-run instructions.

---

## Expectations

- For every change: state **What** changed, **Why** (the problem it solves), and **Impact** (metric or score expected to improve).
- Prefer small, targeted edits over large rewrites — easier to review, test, and revert.
- Always verify changes don't break other pages that share CSS or JS files.
- Test on mobile viewport (375px) and desktop (1440px) at minimum.

---

## Examples of Tasks

- Audit a site for Core Web Vitals issues and fix each one with specific code changes.
- Move Google Fonts from CSS `@import` to HTML `<link>` to eliminate render-blocking waterfall.
- Add `width`/`height` to all `<img>` tags to eliminate Cumulative Layout Shift (CLS).
- Add `aria-expanded` to toggle buttons and sync via JavaScript on open/close.
- Move inline `<style>` blocks in `<body>` to appropriate external CSS files.
- Identify and remove duplicate CSS file loads.
- Add `loading="lazy"` to below-fold images to improve LCP.

---

## Technology Radar (Keep Current)

Update this table when reviewing:

| Technology | Status | Notes |
|-----------|--------|-------|
| Vite 6.x | ✅ Adopt | Default build tool for new projects |
| CSS Layers (`@layer`) | ✅ Adopt | Replaces specificity hacks cleanly |
| Container Queries | ✅ Adopt | Component-responsive design without media queries |
| View Transitions API | ⚠️ Trial | Good browser support (Chrome/Edge), Safari improving |
| React 19 | ✅ Adopt | Server Components stable; Actions API simplifies forms |
| Tailwind v4 | ⚠️ Trial | CSS-first config; monitor ecosystem adoption |
| `font-display: swap` | ✅ Adopt | Always use for web fonts to avoid FOUT |
| Import Maps | ✅ Adopt | Native module resolution; already used in this project |
| INP (Interaction to Next Paint) | ✅ Adopt | Replaced FID in Core Web Vitals — optimize event handlers |
| Speculation Rules API | ⚠️ Trial | Instant page navigations; watch browser support |

---

## Self-Growth Protocol

This skill file **must** be updated when any of the following happen:

1. **Lighthouse scoring changes** — Google periodically shifts metric weights; re-run audit and update scores.
2. **WCAG updates** — Currently 2.2; WCAG 3.0 is in development. Update checklist when ratified.
3. **New browser capabilities hit >85% global support** — Adopt and add to radar.
4. **Project dependencies update** — Three.js, Remixicon, or Calendly widget breaking changes need a matching note.
5. **Core Web Vitals thresholds change** — Google announces these; check quarterly.
6. **Best Practices score drops** — Investigate inspector/console errors; update checklist to catch the class of issue earlier.

**Review trigger:** Run a fresh Lighthouse audit every 90 days on the live site. If any score drops > 5 points, investigate, fix, and update this file with the root cause + fix.

---

## Changelog

| Version | Date | Summary |
|---------|------|---------|
| 1.1.0 | 2026-02-27 | Full audit checklist, technology radar, self-growth protocol. Fixed Google Fonts render-blocking waterfall, duplicate CSS load, CLS-causing missing img attributes, and aria-expanded sync on 5cypress.com. |
| 1.0.0 | 2026-02-27 | Initial skill scaffold. |
