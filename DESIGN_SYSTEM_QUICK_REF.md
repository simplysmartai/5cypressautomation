# 5 CYPRESS - Design System Reference Card

## 🎨 Quick Token Reference

### Colors

#### Brand
```css
--brand-primary: #5D8C5D;      /* Swamp Green */
--brand-accent: #FBBF24;       /* Gold */
```

#### Backgrounds
```css
--bg-void: #000000;
--bg-main: #0A0A0C;
--bg-surface: #141418;
--bg-surface-hover: #1C1C22;
```

#### Text
```css
--text-primary: #FEFEFE;
--text-secondary: #D4D4D8;
--text-tertiary: #A1A1AA;
```

#### Semantic
```css
--success: #10B981;
--warning: #F59E0B;
--error: #EF4444;
--info: #3B82F6;
```

### Typography

#### Fonts
```css
--font-display: 'Playfair Display', Georgia, serif;
--font-heading: 'Space Grotesk', 'Inter', sans-serif;
--font-body: 'DM Sans', 'Inter', sans-serif;
--font-mono: 'JetBrains Mono', monospace;
```

#### Sizes
```css
--text-xs: 0.75rem;     /* 12px */
--text-sm: 0.875rem;    /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg: 1.125rem;    /* 18px */
--text-5xl: 3rem;       /* 48px */
--text-7xl: 4.5rem;     /* 72px */
```

### Spacing (8pt Grid)
```css
--space-2: 0.5rem;      /* 8px */
--space-4: 1rem;        /* 16px */
--space-6: 1.5rem;      /* 24px */
--space-8: 2rem;        /* 32px */
--space-12: 3rem;       /* 48px */
--space-16: 4rem;       /* 64px */
```

### Border Radius
```css
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 24px;
--radius-full: 9999px;
```

### Shadows
```css
--shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.4);
--shadow-md: 0 8px 24px rgba(0, 0, 0, 0.5);
--shadow-lg: 0 24px 48px rgba(0, 0, 0, 0.6);
--shadow-glow: 0 0 40px rgba(93, 140, 93, 0.3);
```

### Animations
```css
--duration-fast: 200ms;
--duration-normal: 300ms;
--duration-slow: 500ms;

--ease-out: cubic-bezier(0.16, 1, 0.3, 1);        /* Apple */
--ease-bounce: cubic-bezier(0.34, 1.56, 0.64, 1);
```

---

## 🧩 Component Classes

### Buttons
```html
<button class="btn btn-primary">Primary</button>
<button class="btn btn-secondary">Secondary</button>
<button class="btn btn-ghost">Ghost</button>
<button class="btn btn-primary btn-lg">Large</button>
```

### Cards
```html
<div class="card">Basic Card</div>
<div class="card card-glass">Glass Card</div>
<div class="card card-glow">Glowing Card</div>
```

### Text Utilities
```html
<span class="text-gradient">Gradient Text</span>
<span class="text-shimmer">Animated Shimmer</span>
<h1 class="font-display">Editorial Headline</h1>
<p class="font-body">Body Text</p>
```

### Animations
```html
<div class="animate-in">Fades in</div>
<div class="animate-in animate-in-delay-2">Delayed</div>
<div class="reveal">Reveal on scroll</div>
<div data-reveal="stagger">Stagger children</div>
<div class="floating">Float animation</div>
```

### Layout
```html
<div class="container">Centered container</div>
<div class="grid grid-cols-3 gap-8">3 column grid</div>
<div class="flex items-center justify-between">Flex row</div>
```

---

## 🎯 Usage Examples

### Editorial Hero
```html
<h1 class="font-display" style="font-size: var(--text-7xl); font-style: italic;">
  Distinctive Headline
</h1>
```

### Gradient CTA
```html
<button class="btn btn-primary btn-lg">
  <span>Get Started</span>
  <i class="ri-arrow-right-line"></i>
</button>
```

### Stats Card
```html
<div class="data-card">
  <div class="data-label">Active Workflows</div>
  <div class="data-value">
    847 
    <span class="data-trend">
      <i class="ri-arrow-right-up-line"></i> 12%
    </span>
  </div>
  <div class="mini-chart">
    <div class="m-bar" style="height: 65%"></div>
    <div class="m-bar" style="height: 85%"></div>
    <!-- More bars -->
  </div>
</div>
```

### Glass Panel
```html
<div class="card card-glass" style="padding: var(--space-8);">
  <h3 style="margin-bottom: var(--space-4);">Premium Feature</h3>
  <p style="color: var(--text-secondary);">Description text</p>
</div>
```

---

## 📐 Breakpoints

```css
/* Tablet */
@media (max-width: 1024px) { }

/* Mobile */
@media (max-width: 768px) { }

/* Small Mobile */
@media (max-width: 480px) { }
```

---

## 🎨 Color Combinations

### Primary Variants
- Primary: `#5D8C5D`
- Dark: `#2D5A3A`
- Light: `#7BA87B`
- Glow: `rgba(93, 140, 93, 0.3)`

### Accent Variants
- Accent: `#FBBF24`
- Dark: `#D97706`
- Light: `#FCD34D`
- Glow: `rgba(251, 191, 36, 0.3)`

### Best Pairings
1. Swamp on Black: `#5D8C5D` on `#000000`
2. Gold on Dark: `#FBBF24` on `#0A0A0C`
3. White on Swamp: `#FEFEFE` on `#5D8C5D`
4. Gradient: `linear-gradient(135deg, #5D8C5D, #FBBF24)`

---

## ⚡ Performance Tips

### DO
- ✅ Use CSS transforms (hardware accelerated)
- ✅ Debounce scroll events
- ✅ Use `will-change` sparingly
- ✅ Lazy load images
- ✅ Minify production assets

### DON'T
- ❌ Animate width/height directly
- ❌ Use too many box-shadows
- ❌ Animate on scroll without throttle
- ❌ Load large images immediately
- ❌ Nest too many blur effects

---

## 🔧 Customization

### Change Primary Color
```css
:root {
  --brand-primary: #YOUR_COLOR;
  --brand-primary-dark: #DARKER_SHADE;
  --brand-primary-light: #LIGHTER_SHADE;
  --shadow-glow: 0 0 40px rgba(YOUR_RGB, 0.3);
}
```

### Adjust Typography Scale
```css
:root {
  --text-base: 1.125rem; /* 18px instead of 16px */
}

/* Or use CSS clamp for fluid typography */
h1 {
  font-size: clamp(2.5rem, 5vw, 6rem);
}
```

### Change Animation Speed
```css
:root {
  --duration-normal: 400ms; /* Slower */
  --duration-fast: 150ms;   /* Faster */
}
```

---

Print this card. Keep it handy. Build consistently. 🎨
