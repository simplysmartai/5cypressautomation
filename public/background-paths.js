/**
 * background-paths.js
 * Animated floating SVG paths — vanilla JS port of the BackgroundPaths React component.
 * Uses the Web Animations API for the pathOffset + opacity effect from framer-motion.
 */

(function () {
  "use strict";

  /**
   * Generate the 36-path data array for a given position (1 or -1).
   */
  function generatePaths(position) {
    return Array.from({ length: 36 }, (_, i) => {
      const p = i * 5 * position;
      const q = i * 6;
      return {
        id: i,
        d: `M-${380 - p} -${189 + q}C-${380 - p} -${189 + q} -${312 - p} ${216 - q} ${152 - p} ${343 - q}C${616 - p} ${470 - q} ${684 - p} ${875 - q} ${684 - p} ${875 - q}`,
        strokeOpacity: 0.1 + i * 0.03,
        strokeWidth: 0.5 + i * 0.03,
      };
    });
  }

  /**
   * Build one <svg> containing 36 animated paths for the given position.
   */
  function buildSVG(position, color) {
    const ns = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(ns, "svg");
    svg.setAttribute("viewBox", "-420 -420 1160 1360");
    svg.setAttribute("fill", "none");
    svg.setAttribute("aria-hidden", "true");
    svg.setAttribute("preserveAspectRatio", "none");
    svg.className = "bp-svg";

    const pathsData = generatePaths(position);

    pathsData.forEach((data) => {
      const el = document.createElementNS(ns, "path");
      el.setAttribute("d", data.d);
      el.setAttribute("stroke", color);
      el.setAttribute("stroke-width", data.strokeWidth);
      el.setAttribute("stroke-opacity", String(Math.min(data.strokeOpacity, 0.85)));
      el.setAttribute("stroke-linecap", "round");
      // We'll set dasharray/dashoffset after measuring length
      el.dataset.initialOpacity = data.strokeOpacity;
      svg.appendChild(el);
    });

    return svg;
  }

  /**
   * Animate a single path element using the Web Animations API.
   * Mimics framer-motion's:
   *   initial: { pathLength: 0.3, opacity: 0.6 }
   *   animate: { pathLength: 1, opacity: [0.3, 0.6, 0.3], pathOffset: [0, 1, 0] }
   *   transition: { duration: 20-30s, repeat: Infinity, ease: "linear" }
   */
  function animatePath(el) {
    try {
      const totalLength = el.getTotalLength();
      if (!totalLength || totalLength === 0) return;

      // Keep a visible moving segment so the paths are readable on load.
      const dashLen = totalLength * 0.22;

      el.style.strokeDasharray = `${dashLen} ${totalLength}`;
      el.style.strokeDashoffset = "0";

      const baseOpacity = Math.min(parseFloat(el.dataset.initialOpacity) || 0.15, 0.85);
      const duration = (20 + Math.random() * 10) * 1000; // 20–30 s
      const delay = Math.random() * -20000; // stagger start positions

      // pathOffset [0 → 1 → 0] means the visible segment travels the full length and back.
      // Expressed as stroke-dashoffset going negative (the path "travels" forward).
      el.animate(
        [
          { strokeDashoffset: 0, opacity: Math.max(baseOpacity * 0.65, 0.16) },
          { strokeDashoffset: -(totalLength * 0.5), opacity: baseOpacity },
          { strokeDashoffset: -(totalLength), opacity: Math.max(baseOpacity * 0.7, 0.18) },
          { strokeDashoffset: -(totalLength * 1.5), opacity: baseOpacity },
          { strokeDashoffset: -(totalLength * 2), opacity: Math.max(baseOpacity * 0.65, 0.16) },
        ],
        {
          duration,
          delay,
          iterations: Infinity,
          easing: "linear",
          fill: "both",
        }
      );
    } catch (e) {
      // getTotalLength not supported — static fallback
      el.style.strokeOpacity = el.dataset.initialOpacity;
    }
  }

  /**
   * Initialise the background — called once the container element exists.
   */
  function init(container) {
    // Prefer white strokes (site is dark-themed).
    // If you ever switch to a light theme, change to '#0f172a' (slate-950).
    const strokeColor = "rgba(255,255,255,1)";

    container.animate(
      [
        { transform: "translate3d(0, 0, 0) scale(1)", opacity: 0.94 },
        { transform: "translate3d(0, -0.5%, 0) scale(1.01)", opacity: 1 },
        { transform: "translate3d(0, 0, 0) scale(1)", opacity: 0.94 },
      ],
      {
        duration: 10000,
        iterations: Infinity,
        easing: "ease-in-out",
      }
    );

    [1, -1].forEach((position) => {
      const svg = buildSVG(position, strokeColor);
      svg.animate(
        [
          { transform: `translate3d(${position * -1.5}%, 0%, 0) scale(1.08)` },
          { transform: `translate3d(${position * 1.5}%, -1.2%, 0) scale(1.11)` },
          { transform: `translate3d(${position * -1.5}%, 0%, 0) scale(1.08)` },
        ],
        {
          duration: 18000 + Math.random() * 4000,
          iterations: Infinity,
          easing: "ease-in-out",
        }
      );

      container.appendChild(svg);

      // Animate after the SVG is in the DOM so getTotalLength() works.
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          svg.querySelectorAll("path").forEach(animatePath);
        });
      });
    });
  }

  /**
   * Entry point — wait for DOM then wire up the container.
   */
  function mount() {
    const container = document.getElementById("background-paths");
    if (container) {
      init(container);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mount);
  } else {
    mount();
  }
})();
