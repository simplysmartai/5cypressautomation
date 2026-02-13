// Enhanced Dynamic Interactions for 5 Cypress Labs
document.addEventListener('DOMContentLoaded', function() {
    
    // Smooth parallax scrolling for background elements
    let ticking = false;
    
    function updateParallax() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.glow-blob');
        
        parallaxElements.forEach((el, index) => {
            const speed = (index + 1) * 0.2;
            el.style.transform = `translateY(${scrolled * speed}px)`;
        });
        
        // Tech grid parallax
        const grid = document.querySelector('body::before');
        if (grid) {
            document.documentElement.style.setProperty('--grid-offset', `${scrolled * 0.1}px`);
        }
        
        ticking = false;
    }
    
    function requestParallax() {
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', requestParallax);
    
    // Enhanced hover effects for service cards
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.addEventListener('mouseenter', function(e) {
            // Add subtle tilt based on mouse position
            const rect = this.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const mouseX = e.clientX - centerX;
            const mouseY = e.clientY - centerY;
            
            const tiltX = (mouseY / rect.height) * 10;
            const tiltY = -(mouseX / rect.width) * 10;
            
            this.style.transform = `translateY(-20px) rotateX(${5 + tiltX}deg) rotateY(${tiltY}deg) scale(1.02)`;
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
        
        card.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const mouseX = e.clientX - centerX;
            const mouseY = e.clientY - centerY;
            
            const tiltX = (mouseY / rect.height) * 5;
            const tiltY = -(mouseX / rect.width) * 5;
            
            this.style.transform = `translateY(-20px) rotateX(${5 + tiltX}deg) rotateY(${tiltY}deg) scale(1.02)`;
        });
    });
    
    // Magnetic effect for buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mousemove', function(e) {
            const rect = this.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            const mouseX = e.clientX - centerX;
            const mouseY = e.clientY - centerY;
            
            const moveX = mouseX * 0.3;
            const moveY = mouseY * 0.3;
            
            this.style.transform = `translateY(-8px) translate(${moveX}px, ${moveY}px) scale(1.05)`;
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
        });
    });
    
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
            }
        });
    }, observerOptions);
    
    // Observe all sections and cards
    document.querySelectorAll('section, .service-card, .approach-item').forEach(el => {
        observer.observe(el);
    });
    
    // Enhanced blob animation based on scroll position
    window.addEventListener('scroll', () => {
        const scrollPercent = window.scrollY / (document.body.scrollHeight - window.innerHeight);
        const blobs = document.querySelectorAll('.glow-blob');
        
        blobs.forEach((blob, index) => {
            const rotation = scrollPercent * 360 * (index + 1);
            const scale = 1 + Math.sin(scrollPercent * Math.PI * 2) * 0.1;
            blob.style.transform += ` rotate(${rotation}deg) scale(${scale})`;
        });
    });
    
    // Enhanced navbar scroll effect
    const navbar = document.querySelector('.navbar');
    let lastScrollY = window.scrollY;
    
    window.addEventListener('scroll', () => {
        if (window.scrollY > lastScrollY && window.scrollY > 100) {
            navbar.style.transform = 'translateY(-100%)';
        } else {
            navbar.style.transform = 'translateY(0)';
        }
        lastScrollY = window.scrollY;
        
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
});

// Global Mobile Menu Toggle
function toggleMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    const toggleIcon = document.querySelector('.mobile-toggle i');
    
    if (mobileMenu) {
        mobileMenu.classList.toggle('active');
        const isActive = mobileMenu.classList.contains('active');
        document.body.style.overflow = isActive ? 'hidden' : '';
        
        // Update icon if it exists (using Remix Icon as in index.html)
        if (toggleIcon) {
            toggleIcon.className = isActive ? 'ri-close-line' : 'ri-menu-line';
        }
    }
}

function closeMobileMenu() {
    const mobileMenu = document.getElementById('mobileMenu');
    const toggleIcon = document.querySelector('.mobile-toggle i');
    
    if (mobileMenu) {
        mobileMenu.classList.remove('active');
        document.body.style.overflow = '';
        if (toggleIcon) {
            toggleIcon.className = 'ri-menu-line';
        }
    }
}