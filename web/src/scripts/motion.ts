/**
 * motion.ts — single site-wide motion module (bundled by Astro via Layout).
 *
 * Owns: the one prefers-reduced-motion gate, Lenis smooth scroll, the
 * scroll-reveal system (ScrollTrigger driving the existing .reveal /
 * .reveal-stagger classes), magnetic buttons, click ripple, the booking-modal
 * open trigger + Lenis interop, and in-page anchor scrolling.
 *
 * Reduced-motion contract: when the user prefers reduced motion we never start
 * Lenis or a single GSAP tween — we snap every reveal to its final state and
 * wire only the non-animated interactions. Every later effect inherits this.
 */
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import Lenis from 'lenis';

gsap.registerPlugin(ScrollTrigger);

const REVEAL_SELECTOR = '.reveal, .reveal-stagger';
const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function showAllReveals(): void {
  document
    .querySelectorAll<HTMLElement>(REVEAL_SELECTOR)
    .forEach((el) => el.classList.add('is-visible'));
}

// ── Magnetic buttons ─────────────────────────────────────────
function initMagnetic(): void {
  document.querySelectorAll<HTMLElement>('[data-magnetic]').forEach((btn) => {
    btn.addEventListener('mousemove', (e: MouseEvent) => {
      const rect = btn.getBoundingClientRect();
      const x = e.clientX - rect.left - rect.width / 2;
      const y = e.clientY - rect.top - rect.height / 2;
      btn.style.transform = `translate(${x * 0.18}px, ${y * 0.18}px)`;
    });
    btn.addEventListener('mouseleave', () => {
      btn.style.transform = '';
    });
  });
}

// ── Click ripple ─────────────────────────────────────────────
function initRipple(): void {
  document.querySelectorAll<HTMLElement>('[data-ripple]').forEach((btn) => {
    btn.addEventListener('click', (e: MouseEvent) => {
      const rect = btn.getBoundingClientRect();
      const ripple = document.createElement('span');
      ripple.classList.add('ripple-wave');
      ripple.style.left = `${e.clientX - rect.left}px`;
      ripple.style.top = `${e.clientY - rect.top}px`;
      btn.appendChild(ripple);
      ripple.addEventListener('animationend', () => ripple.remove());
    });
  });
}

// ── Booking modal open + Lenis interop ───────────────────────
// Close handling lives in BookingModal.astro; we only watch the modal's class
// so scrolling is frozen/unfrozen no matter how it opens or closes.
function initModal(lenis?: Lenis): void {
  const modal = document.getElementById('booking-modal');
  document.querySelectorAll('[data-open-booking]').forEach((trigger) => {
    trigger.addEventListener('click', () => {
      modal?.classList.add('is-open');
      modal?.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
    });
  });
  if (modal && lenis) {
    const sync = () =>
      modal.classList.contains('is-open') ? lenis.stop() : lenis.start();
    new MutationObserver(sync).observe(modal, {
      attributes: true,
      attributeFilter: ['class'],
    });
  }
}

function main(): void {
  // Interactions that are safe under reduced motion (pointer-driven feedback).
  initRipple();

  if (prefersReduced) {
    showAllReveals();
    initModal();
    return;
  }

  initMagnetic();

  const lenis = new Lenis({ lerp: 0.1, duration: 1.1, smoothWheel: true });
  lenis.on('scroll', ScrollTrigger.update);
  gsap.ticker.add((time) => lenis.raf(time * 1000));
  gsap.ticker.lagSmoothing(0);

  initModal(lenis);

  // In-page anchors route through Lenis so they land smoothly and correctly.
  document.querySelectorAll<HTMLAnchorElement>('a[href^="#"]').forEach((a) => {
    const href = a.getAttribute('href');
    if (!href || href === '#') return;
    a.addEventListener('click', (e) => {
      const target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      lenis.scrollTo(target as HTMLElement, { offset: -80 });
    });
  });

  // Scroll-reveal: same classes, ScrollTrigger driver, plays once per element.
  ScrollTrigger.batch(REVEAL_SELECTOR, {
    start: 'top 88%',
    once: true,
    onEnter: (els) => els.forEach((el) => el.classList.add('is-visible')),
  });

  // Hero: one restrained scroll effect — a slow parallax drift on the visual.
  const heroVisual = document.querySelector('.hero-visual');
  if (heroVisual) {
    gsap.to(heroVisual, {
      yPercent: 6,
      ease: 'none',
      scrollTrigger: {
        trigger: '.hero',
        start: 'top top',
        end: 'bottom top',
        scrub: true,
      },
    });
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', main);
} else {
  main();
}
