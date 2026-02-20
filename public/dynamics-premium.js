/**
 * 5 CYPRESS - PREMIUM INTERACTIONS
 * Sophisticated animations and micro-interactions
 */

// ===================================
// UTILITIES
// ===================================

const lerp = (start, end, factor) => start + (end - start) * factor;

const clamp = (value, min, max) => Math.min(Math.max(value, min), max);

const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// ===================================
// SMOOTH SCROLL
// ===================================

document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// ===================================
// NAVBAR SCROLL BEHAVIOR
// ===================================

let lastScrollY = window.scrollY;
const navbar = document.querySelector('.navbar');

const updateNavbar = () => {
  const currentScrollY = window.scrollY;
  
  // Add/remove scrolled class
  if (currentScrollY > 50) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
  
  // Hide on scroll down, show on scroll up
  if (currentScrollY > lastScrollY && currentScrollY > 200) {
    navbar.style.transform = 'translateY(-100%)';
  } else {
    navbar.style.transform = 'translateY(0)';
  }
  
  lastScrollY = currentScrollY;
};

window.addEventListener('scroll', updateNavbar);

// ===================================
// MOBILE MENU
// ===================================

window.toggleMobileMenu = () => {
  const mobileMenu = document.getElementById('mobileMenu');
  const body = document.body;
  
  if (mobileMenu.classList.contains('active')) {
    mobileMenu.classList.remove('active');
    body.style.overflow = '';
  } else {
    mobileMenu.classList.add('active');
    body.style.overflow = 'hidden';
  }
};

window.closeMobileMenu = () => {
  const mobileMenu = document.getElementById('mobileMenu');
  mobileMenu.classList.remove('active');
  document.body.style.overflow = '';
};

// Close mobile menu on escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    closeMobileMenu();
  }
});

// Close mobile menu on window resize
window.addEventListener('resize', debounce(() => {
  if (window.innerWidth > 1024) {
    closeMobileMenu();
  }
}, 250));

// ===================================
// SCROLL REVEAL ANIMATIONS
// ===================================

const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('revealed');
      // Unobserve after revealing for better performance
      revealObserver.unobserve(entry.target);
    }
  });
}, observerOptions);

// Observe all reveal elements
document.querySelectorAll('.reveal, [data-reveal]').forEach((el) => {
  revealObserver.observe(el);
});

// ===================================
// MAGNETIC BUTTON EFFECT
// ===================================

const magneticButtons = document.querySelectorAll('.btn-magnetic, .btn-primary');

magneticButtons.forEach(button => {
  button.addEventListener('mousemove', (e) => {
    const rect = button.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    
    // Limit the effect to 20px movement
    const moveX = clamp(x * 0.3, -20, 20);
    const moveY = clamp(y * 0.3, -20, 20);
    
    button.style.transform = `translate(${moveX}px, ${moveY}px) scale(1.02)`;
  });
  
  button.addEventListener('mouseleave', () => {
    button.style.transform = 'translate(0, 0) scale(1)';
  });
});

// ===================================
// PARALLAX SCROLL EFFECT
// ===================================

let ticking = false;

const updateParallax = () => {
  const scrolled = window.scrollY;
  
  // Hero visual parallax
  const heroVisual = document.querySelector('.hero-visual .visual-container');
  if (heroVisual) {
    const offset = scrolled * 0.3;
    heroVisual.style.transform = `rotateX(${8 - offset * 0.01}deg) rotateY(${-2 + offset * 0.005}deg) translateY(${offset}px)`;
  }
  
  // Floating elements
  const floatingElements = document.querySelectorAll('.dash-notification');
  floatingElements.forEach((el, index) => {
    const speed = 0.5 + (index * 0.2);
    const offset = scrolled * speed;
    el.style.transform = `translateY(${offset}px)`;
  });
  
  ticking = false;
};

window.addEventListener('scroll', () => {
  if (!ticking) {
    window.requestAnimationFrame(updateParallax);
    ticking = true;
  }
});

// ===================================
// MOUSE TRAIL EFFECT (Subtle)
// ===================================

let mouseX = 0;
let mouseY = 0;
let currentX = 0;
let currentY = 0;

document.addEventListener('mousemove', (e) => {
  mouseX = e.clientX;
  mouseY = e.clientY;
});

// Create cursor glow element
const cursorGlow = document.createElement('div');
cursorGlow.style.cssText = `
  position: fixed;
  width: 300px;
  height: 300px;
  pointer-events: none;
  z-index: 9998;
  background: radial-gradient(circle, rgba(93, 140, 93, 0.08) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(-50%, -50%);
  transition: opacity 0.3s;
  opacity: 0;
`;
document.body.appendChild(cursorGlow);

// Animate cursor glow
const animateCursor = () => {
  currentX = lerp(currentX, mouseX, 0.1);
  currentY = lerp(currentY, mouseY, 0.1);
  
  cursorGlow.style.left = currentX + 'px';
  cursorGlow.style.top = currentY + 'px';
  
  requestAnimationFrame(animateCursor);
};

animateCursor();

document.addEventListener('mouseenter', () => {
  cursorGlow.style.opacity = '1';
});

document.addEventListener('mouseleave', () => {
  cursorGlow.style.opacity = '0';
});

// ===================================
// CARD HOVER TILT EFFECT
// ===================================

const cards = document.querySelectorAll('.card, .data-card');

cards.forEach(card => {
  card.addEventListener('mousemove', (e) => {
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const rotateX = (y - centerY) / 20;
    const rotateY = (centerX - x) / 20;
    
    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-4px)`;
  });
  
  card.addEventListener('mouseleave', () => {
    card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
  });
});

// ===================================
// NUMBER COUNTER ANIMATION
// ===================================

const animateValue = (element, start, end, duration) => {
  let startTimestamp = null;
  const step = (timestamp) => {
    if (!startTimestamp) startTimestamp = timestamp;
    const progress = Math.min((timestamp - startTimestamp) / duration, 1);
    const current = Math.floor(progress * (end - start) + start);
    element.textContent = current.toLocaleString();
    if (progress < 1) {
      window.requestAnimationFrame(step);
    }
  };
  window.requestAnimationFrame(step);
};

const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting && !entry.target.dataset.counted) {
      const targetValue = parseInt(entry.target.dataset.count);
      const isPercentage = entry.target.textContent.includes('%');
      const suffix = isPercentage ? '%' : '';
      
      animateValue(entry.target, 0, targetValue, 2000);
      entry.target.dataset.counted = 'true';
      
      if (suffix) {
        const observer = new MutationObserver(() => {
          if (!entry.target.textContent.includes(suffix)) {
            entry.target.textContent += suffix;
          }
        });
        observer.observe(entry.target, { childList: true, characterData: true, subtree: true });
        setTimeout(() => observer.disconnect(), 2100);
      }
    }
  });
}, { threshold: 0.5 });

document.querySelectorAll('[data-count]').forEach(el => {
  counterObserver.observe(el);
});

// ===================================
// CALENDLY INTEGRATION
// ===================================

// Booking managed by dynamics.js modal
// window.openCalendly removed to prevent conflict

// ===================================
// SMOOTH ENTRANCE ANIMATIONS
// ===================================

// Animate hero elements on load
window.addEventListener('load', () => {
  const heroElements = document.querySelectorAll('.hero-content .animate-in');
  heroElements.forEach((el, index) => {
    setTimeout(() => {
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    }, index * 150);
  });
});

// ===================================
// TYPING EFFECT FOR LOG ENTRIES
// ===================================

const logFeed = document.querySelector('.log-feed');
if (logFeed) {
  // Pause animation on hover
  logFeed.addEventListener('mouseenter', () => {
    const logInner = logFeed.querySelector('.log-inner');
    if (logInner) {
      logInner.style.animationPlayState = 'paused';
    }
  });
  
  logFeed.addEventListener('mouseleave', () => {
    const logInner = logFeed.querySelector('.log-inner');
    if (logInner) {
      logInner.style.animationPlayState = 'running';
    }
  });
}

// ===================================
// INTERSECTION OBSERVER FOR STATS
// ===================================

const statsObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.animationPlayState = 'running';
    }
  });
}, { threshold: 0.3 });

document.querySelectorAll('.data-card, .mini-chart').forEach(el => {
  statsObserver.observe(el);
});

// ===================================
// PERFORMANCE OPTIMIZATIONS
// ===================================

// Lazy load images
if ('loading' in HTMLImageElement.prototype) {
  const images = document.querySelectorAll('img[loading="lazy"]');
  images.forEach(img => {
    img.src = img.dataset.src;
  });
} else {
  // Fallback for browsers that don't support lazy loading
  const script = document.createElement('script');
  script.src = 'https://cdnjs.cloudflare.com/ajax/libs/lazysizes/5.3.2/lazysizes.min.js';
  document.body.appendChild(script);
}

// Preload critical fonts
const fontPrefetch = document.createElement('link');
fontPrefetch.rel = 'prefetch';
fontPrefetch.as = 'font';
fontPrefetch.crossOrigin = 'anonymous';
document.head.appendChild(fontPrefetch);

// ===================================
// CONSOLE BRANDING
// ===================================

console.log('%c5 CYPRESS', 'font-size: 48px; font-weight: 900; color: #5D8C5D; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);');
console.log('%cPrecision Engineering for Business Automation', 'font-size: 14px; color: #FBBF24; font-weight: 600;');
console.log('%cInterested in working with us? hello@5cypress.com', 'font-size: 12px; color: #A1A1AA;');

// ===================================
// ANALYTICS & TRACKING
// ===================================

// Track scroll depth
let maxScroll = 0;
window.addEventListener('scroll', debounce(() => {
  const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
  if (scrollPercent > maxScroll) {
    maxScroll = Math.floor(scrollPercent / 25) * 25; // Track in 25% increments
    // Send to analytics
    if (typeof gtag !== 'undefined') {
      gtag('event', 'scroll_depth', {
        'event_category': 'engagement',
        'event_label': maxScroll + '%'
      });
    }
  }
}, 500));

// Track CTA clicks
document.querySelectorAll('.btn-primary').forEach(btn => {
  btn.addEventListener('click', () => {
    if (typeof gtag !== 'undefined') {
      gtag('event', 'cta_click', {
        'event_category': 'conversion',
        'event_label': btn.textContent.trim()
      });
    }
  });
});

// ===================================
// ACCESSIBILITY ENHANCEMENTS
// ===================================

// Focus visible for keyboard navigation
document.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    document.body.classList.add('keyboard-nav');
  }
});

document.addEventListener('mousedown', () => {
  document.body.classList.remove('keyboard-nav');
});

// Add focus styles for keyboard nav
const style = document.createElement('style');
style.textContent = `
  .keyboard-nav *:focus {
    outline: 2px solid var(--brand-primary);
    outline-offset: 4px;
  }
`;
document.head.appendChild(style);

// ===================================
// EASTER EGG
// ===================================

let konamiCode = [];
const konamiPattern = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];

document.addEventListener('keydown', (e) => {
  konamiCode.push(e.key);
  konamiCode = konamiCode.slice(-konamiPattern.length);
  
  if (konamiCode.join(',') === konamiPattern.join(',')) {
    // Activate rainbow mode
    document.body.style.animation = 'rainbow 3s linear infinite';
    const style = document.createElement('style');
    style.textContent = `
      @keyframes rainbow {
        0% { filter: hue-rotate(0deg); }
        100% { filter: hue-rotate(360deg); }
      }
    `;
    document.head.appendChild(style);
    
    setTimeout(() => {
      document.body.style.animation = '';
      style.remove();
    }, 3000);
    
    console.log('%c🎉 You found the secret! 🎉', 'font-size: 24px; color: #FBBF24;');
  }
});

console.log('%c💡 Tip: Try the Konami Code', 'font-size: 10px; color: #52525B; font-style: italic;');
