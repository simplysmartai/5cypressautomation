/* ============================================
   TOUCH GESTURES & MOBILE INTERACTIONS
   ============================================
   
   Following mobile-design skill principles:
   - Touch-first interactions
   - Haptic feedback patterns
   - Gesture recognition
   - Mobile performance optimization
   
   ============================================ */

/* ============================================
   SWIPEABLE TESTIMONIALS
   ============================================ */

class SwipeableTestimonials {
  constructor(container) {
    this.container = container;
    this.track = container.querySelector('.testimonial-track');
    if (!this.track) return;
    
    this.cards = Array.from(this.track.querySelectorAll('.testimonial-card'));
    this.currentIndex = 0;
    this.startX = 0;
    this.currentX = 0;
    this.isDragging = false;
    this.threshold = 50; // Minimum swipe distance
    
    this.init();
  }
  
  init() {
    this.setupIndicators();
    this.setupListeners();
    this.updateIndicators();
  }
  
  setupIndicators() {
    const indicatorContainer = document.createElement('div');
    indicatorContainer.className = 'swipe-indicator';
    
    this.cards.forEach((_, index) => {
      const dot = document.createElement('button');
      dot.className = 'swipe-dot';
      dot.setAttribute('aria-label', `Go to testimonial ${index + 1}`);
      dot.addEventListener('click', () => this.goToSlide(index));
      indicatorContainer.appendChild(dot);
    });
    
    this.container.appendChild(indicatorContainer);
    this.indicators = indicatorContainer.querySelectorAll('.swipe-dot');
  }
  
  setupListeners() {
    // Touch events
    this.track.addEventListener('touchstart', (e) => this.handleTouchStart(e), { passive: true });
    this.track.addEventListener('touchmove', (e) => this.handleTouchMove(e), { passive: false });
    this.track.addEventListener('touchend', (e) => this.handleTouchEnd(e));
    
    // Mouse events for desktop testing
    this.track.addEventListener('mousedown', (e) => this.handleMouseDown(e));
    this.track.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    this.track.addEventListener('mouseup', (e) => this.handleMouseUp(e));
    this.track.addEventListener('mouseleave', (e) => this.handleMouseUp(e));
    
    // Scroll snap fallback
    this.track.addEventListener('scroll', () => {
      const scrollLeft = this.track.scrollLeft;
      const cardWidth = this.cards[0].offsetWidth;
      const newIndex = Math.round(scrollLeft / cardWidth);
      if (newIndex !== this.currentIndex) {
        this.currentIndex = newIndex;
        this.updateIndicators();
      }
    });
  }
  
  handleTouchStart(e) {
    this.startX = e.touches[0].clientX;
    this.isDragging = true;
    this.triggerHaptic('light');
  }
  
  handleTouchMove(e) {
    if (!this.isDragging) return;
    
    this.currentX = e.touches[0].clientX;
    const diff = this.startX - this.currentX;
    
    // Prevent default if horizontal swipe
    if (Math.abs(diff) > 10) {
      e.preventDefault();
    }
  }
  
  handleTouchEnd(e) {
    if (!this.isDragging) return;
    
    const diff = this.startX - this.currentX;
    
    if (Math.abs(diff) > this.threshold) {
      if (diff > 0) {
        this.next();
      } else {
        this.prev();
      }
    }
    
    this.isDragging = false;
  }
  
  handleMouseDown(e) {
    this.startX = e.clientX;
    this.isDragging = true;
    this.track.style.cursor = 'grabbing';
    e.preventDefault();
  }
  
  handleMouseMove(e) {
    if (!this.isDragging) return;
    this.currentX = e.clientX;
  }
  
  handleMouseUp(e) {
    if (!this.isDragging) return;
    
    const diff = this.startX - this.currentX;
    
    if (Math.abs(diff) > this.threshold) {
      if (diff > 0) {
        this.next();
      } else {
        this.prev();
      }
    }
    
    this.isDragging = false;
    this.track.style.cursor = 'grab';
  }
  
  next() {
    if (this.currentIndex < this.cards.length - 1) {
      this.currentIndex++;
      this.goToSlide(this.currentIndex);
      this.triggerHaptic('medium');
    }
  }
  
  prev() {
    if (this.currentIndex > 0) {
      this.currentIndex--;
      this.goToSlide(this.currentIndex);
      this.triggerHaptic('medium');
    }
  }
  
  goToSlide(index) {
    this.currentIndex = Math.max(0, Math.min(index, this.cards.length - 1));
    
    const cardWidth = this.cards[0].offsetWidth;
    const gap = 24; // Match CSS gap
    const scrollPosition = (cardWidth + gap) * this.currentIndex;
    
    this.track.scrollTo({
      left: scrollPosition,
      behavior: 'smooth'
    });
    
    this.updateIndicators();
  }
  
  updateIndicators() {
    this.indicators.forEach((dot, index) => {
      if (index === this.currentIndex) {
        dot.classList.add('active');
        dot.setAttribute('aria-current', 'true');
      } else {
        dot.classList.remove('active');
        dot.removeAttribute('aria-current');
      }
    });
  }
  
  triggerHaptic(intensity = 'light') {
    if ('vibrate' in navigator) {
      const patterns = {
        light: 10,
        medium: 20,
        heavy: 30
      };
      navigator.vibrate(patterns[intensity] || 10);
    }
  }
}

/* ============================================
   PULL-TO-REFRESH
   ============================================ */

class PullToRefresh {
  constructor() {
    this.startY = 0;
    this.currentY = 0;
    this.isDragging = false;
    this.threshold = 100; // Pull distance to trigger refresh
    this.hint = null;
    
    this.init();
  }
  
  init() {
    this.createHint();
    this.setupListeners();
  }
  
  createHint() {
    this.hint = document.createElement('div');
    this.hint.className = 'pull-refresh-hint';
    this.hint.innerHTML = '<i class="ri-refresh-line"></i> Pull to refresh';
    document.body.appendChild(this.hint);
  }
  
  setupListeners() {
    document.addEventListener('touchstart', (e) => {
      if (window.scrollY === 0) {
        this.startY = e.touches[0].clientY;
        this.isDragging = true;
      }
    }, { passive: true });
    
    document.addEventListener('touchmove', (e) => {
      if (!this.isDragging) return;
      
      this.currentY = e.touches[0].clientY;
      const diff = this.currentY - this.startY;
      
      if (diff > 0 && window.scrollY === 0) {
        const pullDistance = Math.min(diff, this.threshold);
        const progress = pullDistance / this.threshold;
        
        this.hint.style.top = `${60 + pullDistance}px`;
        this.hint.style.opacity = progress;
        
        if (pullDistance >= this.threshold) {
          this.hint.classList.add('visible');
          this.triggerHaptic('medium');
        } else {
          this.hint.classList.remove('visible');
        }
      }
    }, { passive: true });
    
    document.addEventListener('touchend', (e) => {
      if (!this.isDragging) return;
      
      const diff = this.currentY - this.startY;
      
      if (diff >= this.threshold) {
        this.refresh();
      }
      
      this.hint.classList.remove('visible');
      this.hint.style.top = '-60px';
      this.hint.style.opacity = '0';
      this.isDragging = false;
    });
  }
  
  async refresh() {
    this.triggerHaptic('heavy');
    
    // Simulate refresh - replace with actual refresh logic
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Show success feedback
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Page refreshed!');
    }
  }
  
  triggerHaptic(intensity = 'light') {
    if ('vibrate' in navigator) {
      const patterns = {
        light: 10,
        medium: 20,
        heavy: 30
      };
      navigator.vibrate(patterns[intensity] || 10);
    }
  }
}

/* ============================================
   MOBILE STICKY CTA
   ============================================ */

class MobileStickyCTA {
  constructor() {
    this.cta = null;
    this.lastScrollY = 0;
    this.threshold = 300; // Show after scrolling 300px
    
    if (window.innerWidth <= 768) {
      this.init();
    }
  }
  
  init() {
    this.createCTA();
    this.setupScrollListener();
  }
  
  createCTA() {
    this.cta = document.createElement('div');
    this.cta.className = 'mobile-sticky-cta';
    this.cta.innerHTML = `
      <button class="btn btn-primary btn-lg ripple" onclick="openCalendly()">
        Get Started Free <i class="ri-arrow-right-up-line"></i>
      </button>
    `;
    document.body.appendChild(this.cta);
    document.body.classList.add('has-sticky-cta');
  }
  
  setupScrollListener() {
    let ticking = false;
    
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          this.handleScroll();
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }
  
  handleScroll() {
    const scrollY = window.scrollY;
    
    if (scrollY > this.threshold && scrollY > this.lastScrollY) {
      // Scrolling down and past threshold
      this.cta.style.transform = 'translateY(0)';
    } else if (scrollY < this.threshold) {
      // Near top
      this.cta.style.transform = 'translateY(100px)';
    }
    
    this.lastScrollY = scrollY;
  }
}

/* ============================================
   RIPPLE EFFECT
   ============================================ */

class RippleEffect {
  constructor() {
    this.setupListeners();
  }
  
  setupListeners() {
    document.addEventListener('click', (e) => {
      const target = e.target.closest('.ripple');
      if (!target) return;
      
      this.createRipple(target, e);
      this.triggerHaptic('light');
    });
  }
  
  createRipple(element, event) {
    const rect = element.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    const ripple = document.createElement('span');
    ripple.style.cssText = `
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.5);
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      pointer-events: none;
      animation: ripple-animation 0.6s ease-out;
    `;
    
    // Add keyframes if not already present
    if (!document.getElementById('ripple-keyframes')) {
      const style = document.createElement('style');
      style.id = 'ripple-keyframes';
      style.textContent = `
        @keyframes ripple-animation {
          to {
            transform: scale(2);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
    
    element.appendChild(ripple);
    
    setTimeout(() => ripple.remove(), 600);
  }
  
  triggerHaptic(intensity = 'light') {
    if ('vibrate' in navigator) {
      navigator.vibrate(10);
    }
  }
}

/* ============================================
   TOUCH-FRIENDLY CARD INTERACTIONS
   ============================================ */

class TouchCards {
  constructor() {
    this.cards = document.querySelectorAll('.card-interactive, .card[onclick]');
    this.setupListeners();
  }
  
  setupListeners() {
    this.cards.forEach(card => {
      let pressTimer;
      
      card.addEventListener('touchstart', (e) => {
        card.classList.add('card-pressed');
        this.triggerHaptic('light');
        
        // Long press detection
        pressTimer = setTimeout(() => {
          this.handleLongPress(card);
        }, 500);
      }, { passive: true });
      
      card.addEventListener('touchend', (e) => {
        card.classList.remove('card-pressed');
        clearTimeout(pressTimer);
      });
      
      card.addEventListener('touchmove', (e) => {
        card.classList.remove('card-pressed');
        clearTimeout(pressTimer);
      });
    });
  }
  
  handleLongPress(card) {
    this.triggerHaptic('heavy');
    
    // Show context menu or additional options
    const rect = card.getBoundingClientRect();
    console.log('Long press detected on card:', card);
    
    // Could trigger a native share dialog
    if (navigator.share) {
      const title = card.querySelector('h3')?.textContent || 'Check this out';
      navigator.share({
        title: title,
        url: window.location.href
      }).catch(err => console.log('Share cancelled'));
    }
  }
  
  triggerHaptic(intensity = 'light') {
    if ('vibrate' in navigator) {
      const patterns = {
        light: 10,
        medium: 20,
        heavy: [30, 10, 30]
      };
      navigator.vibrate(patterns[intensity] || 10);
    }
  }
}

/* ============================================
   MOBILE FAB (Floating Action Button)
   ============================================ */

class FloatingActionButton {
  constructor() {
    if (window.innerWidth <= 768) {
      this.init();
    }
  }
  
  init() {
    const fab = document.createElement('button');
    fab.className = 'fab';
    fab.setAttribute('aria-label', 'Schedule a call');
    fab.innerHTML = '<i class="ri-calendar-line"></i>';
    fab.onclick = () => {
      this.triggerHaptic('medium');
      if (typeof openCalendly === 'function') {
        openCalendly();
      }
    };
    
    document.body.appendChild(fab);
    
    // Auto-hide on scroll down, show on scroll up
    this.setupScrollBehavior(fab);
  }
  
  setupScrollBehavior(fab) {
    let lastScrollY = window.scrollY;
    let ticking = false;
    
    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(() => {
          const scrollY = window.scrollY;
          
          if (scrollY > lastScrollY && scrollY > 200) {
            // Scrolling down
            fab.style.transform = 'translateY(100px)';
          } else {
            // Scrolling up
            fab.style.transform = 'translateY(0)';
          }
          
          lastScrollY = scrollY;
          ticking = false;
        });
        ticking = true;
      }
    }, { passive: true });
  }
  
  triggerHaptic(intensity = 'medium') {
    if ('vibrate' in navigator) {
      navigator.vibrate(20);
    }
  }
}

/* ============================================
   INITIALIZE ALL TOUCH FEATURES
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
  // Only initialize touch features on touch devices
  const isTouch = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
  
  if (isTouch) {
    // Initialize swipeable testimonials
    const testimonialsContainer = document.querySelector('.testimonials-section');
    if (testimonialsContainer) {
      new SwipeableTestimonials(testimonialsContainer);
    }
    
    // Initialize pull-to-refresh (optional - enable if needed)
    // new PullToRefresh();
    
    // Initialize mobile sticky CTA
    if (window.innerWidth <= 768) {
      new MobileStickyCTA();
    }
    
    // Initialize ripple effects
    new RippleEffect();
    
    // Initialize touch-friendly cards
    new TouchCards();
    
    // Initialize FAB (optional - enable if needed)
    // new FloatingActionButton();
  }
  
  // Add touch device class to body
  if (isTouch) {
    document.body.classList.add('touch-device');
  }
});

/* ============================================
   UTILITY: HAPTIC FEEDBACK
   ============================================ */

window.triggerHaptic = function(intensity = 'light') {
  if ('vibrate' in navigator) {
    const patterns = {
      light: 10,
      medium: 20,
      heavy: [30, 10, 30],
      success: [10, 50, 10],
      error: [50, 50, 50]
    };
    navigator.vibrate(patterns[intensity] || 10);
  }
};

/* ============================================
   EXPORT FOR MODULE USE
   ============================================ */

if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    SwipeableTestimonials,
    PullToRefresh,
    MobileStickyCTA,
    RippleEffect,
    TouchCards,
    FloatingActionButton
  };
}
