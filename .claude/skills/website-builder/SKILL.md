# Cinematic Landing Page Builder — SKILL.md

<!-- SKILL METADATA -->
<!--
skill_id:     website-builder
version:      1.0.0
domain:       frontend
reviewed:     2026-02-27
status:       READY
changelog:
  1.0.0 - Migrated from .claude/commands/dynamic_website_builder.md and
          converted to canonical skill format with self-annealing header.
-->

## When to load this skill
Load this skill when the user asks to **build a website, landing page, or marketing site** for 5 Cypress Automation or any client. Keywords: "build a site", "landing page", "website for", "cinematic site", "preset", "frontend", "web page".

Do NOT load for: email templates, React component examples, or dashboard /app UI (use `frontend-design` for that).

## Self-healing guidance
If a build fails or looks wrong:
1. Check the GSAP `ctx.revert()` cleanup — missing cleanup causes stale animations
2. Confirm Google Fonts `<link>` tags are in `index.html`, not `App.jsx`
3. If ScrollTrigger pins aren't working, confirm `ScrollTrigger.refresh()` is called after images load
4. Unsplash URLs occasionally 404 — use `?auto=format&fit=crop&w=1920&q=80` params on every URL
5. On mobile, reduce all GSAP `x`/`y` offsets by 50% to prevent layout overflow
6. Record any new patterns that break to `logs/anneal.log` via AnnealLogger

---

## Role

Act as a World-Class Senior Creative Technologist and Lead Frontend Engineer. Objective: Architect and build high-fidelity, cinematic "1:1 Pixel Perfect" landing pages for 5 Cypress Automation. Aesthetic Identity: "High-End Organic Tech"/"Clinical Boutique." Every site you produce should feel like a digital instrument — every scroll intentional, every animation weighted and professional. Eradicate all generic AI patterns.

## Agent Flow — MUST FOLLOW

When the user asks to build a site (or this skill is loaded), immediately ask **exactly these questions** in a single batch, then build the full site from the answers. Do not ask follow-ups. Do not over-discuss. Build.

### Questions (all in one call)

1. **"What's the brand name and one-line purpose?"** — Free text. Example: "Nura Health — precision longevity medicine powered by biological data."
2. **"Pick an aesthetic direction"** — Single-select from the presets below.
3. **"What are your 3 key value propositions?"** — Free text. Brief phrases. These become the Features section cards.
4. **"What should visitors do?"** — Free text. The primary CTA. Example: "Join the waitlist", "Book a consultation", "Start free trial".

---

## Aesthetic Presets

Each preset defines: `palette`, `typography`, `identity` (the overall feel), and `imageMood` (Unsplash search keywords for hero/texture images).

### Preset A — "Organic Tech" (Clinical Boutique)
- **Identity:** A bridge between a biological research lab and an avant-garde luxury magazine.
- **Palette:** Moss `#2E4036` (Primary), Clay `#CC5833` (Accent), Cream `#F2F0E9` (Background), Charcoal `#1A1A1A` (Text/Dark)
- **Typography:** Headings: "Plus Jakarta Sans" + "Outfit" (tight tracking). Drama: "Cormorant Garamond" Italic. Data: `"IBM Plex Mono"`.
- **Image Mood:** dark forest, organic textures, moss, ferns, laboratory glassware.
- **Hero line pattern:** "[Concept noun] is the" (Bold Sans) / "[Power word]." (Massive Serif Italic)

### Preset B — "Midnight Luxe" (Dark Editorial)
- **Identity:** A private members' club meets a high-end watchmaker's atelier.
- **Palette:** Obsidian `#0D0D12` (Primary), Champagne `#C9A84C` (Accent), Ivory `#FAF8F5` (Background), Slate `#2A2A35` (Text/Dark)
- **Typography:** Headings: "Inter" (tight tracking). Drama: "Playfair Display" Italic. Data: `"JetBrains Mono"`.
- **Image Mood:** dark marble, gold accents, architectural shadows, luxury interiors.
- **Hero line pattern:** "[Aspirational noun] meets" (Bold Sans) / "[Precision word]." (Massive Serif Italic)

### Preset C — "Brutalist Signal" (Raw Precision)
- **Identity:** A control room for the future — no decoration, pure information density.
- **Palette:** Paper `#E8E4DD` (Primary), Signal Red `#E63B2E` (Accent), Off-white `#F5F3EE` (Background), Black `#111111` (Text/Dark)
- **Typography:** Headings: "Space Grotesk" (tight tracking). Drama: "DM Serif Display" Italic. Data: `"Space Mono"`.
- **Image Mood:** concrete, brutalist architecture, raw materials, industrial.
- **Hero line pattern:** "[Direct verb] the" (Bold Sans) / "[System noun]." (Massive Serif Italic)

### Preset D — "Vapor Clinic" (Neon Biotech)
- **Identity:** A genome sequencing lab inside a Tokyo nightclub.
- **Palette:** Deep Void `#0A0A14` (Primary), Plasma `#7B61FF` (Accent), Ghost `#F0EFF4` (Background), Graphite `#18181B` (Text/Dark)
- **Typography:** Headings: "Sora" (tight tracking). Drama: "Instrument Serif" Italic. Data: `"Fira Code"`.
- **Image Mood:** bioluminescence, dark water, neon reflections, microscopy.
- **Hero line pattern:** "[Tech noun] beyond" (Bold Sans) / "[Boundary word]." (Massive Serif Italic)

---

## Fixed Design System (NEVER CHANGE)

These rules apply to ALL presets.

### Visual Texture
- Implement a global CSS noise overlay using an inline SVG `<feTurbulence>` filter at **0.05 opacity** to eliminate flat digital gradients.
- Use a `rounded-[2rem]` to `rounded-[3rem]` radius system for all containers. No sharp corners anywhere.

### Micro-Interactions
- All buttons must have a **"magnetic" feel**: subtle `scale(1.03)` on hover with `cubic-bezier(0.25, 0.46, 0.45, 0.94)`.
- Buttons use `overflow-hidden` with a sliding background `<span>` layer for color transitions on hover.
- Links and interactive elements get a `translateY(-1px)` lift on hover.

### Animation Lifecycle
- Use `gsap.context()` within `useEffect` for ALL animations. Return `ctx.revert()` in the cleanup function.
- Default easing: `power3.out` for entrances, `power2.inOut` for morphs.
- Stagger value: `0.08` for text, `0.15` for cards/containers.

---

## Component Architecture (NEVER CHANGE STRUCTURE — only adapt content/colors)

### A. NAVBAR — "The Floating Island"
A `fixed` pill-shaped container, horizontally centered.
- **Morphing Logic:** Transparent at hero top → `bg-[background]/60 backdrop-blur-xl` + border when scrolled past hero.
- Contains: Logo (brand name), 3–4 nav links, accent CTA button.

### B. HERO SECTION — "The Opening Shot"
- `100dvh` height. Full-bleed Unsplash background + primary-to-black gradient overlay.
- Content pushed to bottom-left third using flex + padding.
- Typography: Bold sans + massive serif italic following preset's hero line pattern.
- GSAP staggered `fade-up` for text and CTA.

### C. FEATURES — "Interactive Functional Artifacts"
Three cards (one per value prop), each with a unique interaction:

**Card 1 — "Diagnostic Shuffler":** 3 overlapping cards cycling vertically every 3 seconds with spring-bounce transition.

**Card 2 — "Telemetry Typewriter":** Monospace live-text feed cycling character-by-character with blinking accent cursor.

**Card 3 — "Cursor Protocol Scheduler":** Animated SVG cursor moving across a weekly grid, clicking cells to highlight them.

### D. PHILOSOPHY — "The Manifesto"
Dark background + parallax organic texture. Two contrasting statements:
- "Most [industry] focuses on: [common approach]." — smaller, neutral.
- "We focus on: [differentiated approach]." — massive drama serif, accent keyword.
GSAP word-by-word reveal on scroll.

### E. PROTOCOL — "Sticky Stacking Archive"
3 full-screen cards that stack on scroll. Uses GSAP ScrollTrigger pinning.
Each card has a unique canvas/SVG animation:
1. Rotating geometric motif
2. Scanning horizontal laser line over dot grid
3. Pulsing EKG-style waveform

### F. MEMBERSHIP / PRICING
Three-tier pricing grid. Middle card: primary background + accent CTA. Scale/ring pop.
Non-pricing brands: convert to large single CTA section.

### G. FOOTER
Dark background with `rounded-t-[4rem]`. Grid: brand + tagline, nav columns, legal.
"System Operational" indicator with pulsing green dot.

---

## Technical Requirements

- **Stack:** React 19, Tailwind CSS v3.4.17, GSAP 3 + ScrollTrigger, Lucide React
- **Fonts:** Google Fonts `<link>` in `index.html` per preset
- **Images:** Real Unsplash URLs with `?auto=format&fit=crop&w=1920&q=80`
- **Files:** Single `App.jsx` (or split into `components/` if >600 lines). Single `index.css`.
- **No placeholders.** Every component must be fully implemented.
- **Responsive:** Mobile-first. Stack cards vertically, reduce font sizes, collapse navbar.

---

## Build Sequence

1. Map preset → design tokens (palette, fonts, image mood, identity)
2. Generate hero copy from brand name + purpose + hero line pattern
3. Map 3 value props → 3 Feature card patterns
4. Generate Philosophy contrast statements from brand purpose
5. Generate Protocol steps from brand's methodology
6. Scaffold: `npm create vite@latest`, install deps, write all files
7. Wire every animation, confirm every interaction, verify every image loads

**Execution Mandate:** "Do not build a website; build a digital instrument. Every scroll should feel intentional, every animation weighted and professional. Eradicate all generic AI patterns."
