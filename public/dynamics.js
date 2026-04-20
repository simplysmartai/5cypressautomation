// Improved dynamics.js with explicit global registration for Vetting Form
// ===================================

// Global Booking Handler (attached immediately)
window.openCalendly = function() {
    console.log("Opening Vetting Form Modal...");
    const modal = document.getElementById("bookingModal");
    
    if (modal) {
        modal.classList.add("active");
        document.body.style.overflow = "hidden";
        // Ensure form is reset if needed
        const form = document.getElementById("vettingForm");
        if(form) form.reset();
        const status = document.getElementById("formStatus");
        if(status) status.innerHTML = "";
    } else {
        console.warn("Booking modal not found, redirecting...");
        window.location.href = "/booking.html";
    }
    return false;
};

window.closeBookingModal = function() {
    const modal = document.getElementById("bookingModal");
    if (modal) {
        modal.classList.remove("active");
        document.body.style.overflow = "";
    }
};

window.handleVettingSubmit = async function(event) {
    event.preventDefault();
    const form = event.target;
    const status = document.getElementById("formStatus");
    const submitBtn = form.querySelector("button[type='submit']");
    
    // Collect data
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // UI Loading State
    submitBtn.disabled = true;
    submitBtn.innerHTML = "<span>Analyzing...</span>";
    status.style.color = "var(--text-secondary)";
    status.innerText = "Processing application...";
    
    try {
        // Send to Cloudflare Function (or backend endpoint)
        const response = await fetch("/submit-inquiry", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (response.ok) {
            status.style.color = "var(--brand-primary)";
            status.innerText = "Application Received. We'll be in touch shortly.";
            form.reset();
            setTimeout(() => {
                closeBookingModal();
                submitBtn.disabled = false;
                submitBtn.innerHTML = "<span>Submit Application</span> <i class='ri-arrow-right-line'></i>";
                status.innerText = "";
            }, 3000);
        } else {
            throw new Error(result.error || "Submission failed");
        }
    } catch (error) {
        console.error("Submission Error:", error);
        status.style.color = "#ff4d4d";
        status.innerText = "Error submitting form. Please email info@5cypress.com directly.";
        submitBtn.disabled = false;
        submitBtn.innerHTML = "<span>Try Again</span> <i class='ri-refresh-line'></i>";
    }
};

window.toggleMobileMenu = function() {
    const mobileMenu = document.getElementById("mobileMenu");
    const toggleIcon = document.querySelector(".mobile-toggle i");
    
    if (mobileMenu) {
        mobileMenu.classList.toggle("active");
        const isActive = mobileMenu.classList.contains("active");
        document.body.style.overflow = isActive ? "hidden" : "";
        
        if (toggleIcon) {
            toggleIcon.className = isActive ? "ri-close-line" : "ri-menu-line";
        }
    }
};

window.closeMobileMenu = function() {
    const mobileMenu = document.getElementById("mobileMenu");
    const toggleIcon = document.querySelector(".mobile-toggle i");
    
    if (mobileMenu) {
        mobileMenu.classList.remove("active");
        document.body.style.overflow = "";
        if (toggleIcon) {
            toggleIcon.className = "ri-menu-line";
        }
    }
};

// Animation Loop to replace all others
document.addEventListener("DOMContentLoaded", function() {
    console.log("DOM Loaded - Initializing 5 Cypress Dynamics");

    // Unified Scroll Animation Handler
    let ticking = false;
    const observerOptions = {
        threshold: 0.1,
        rootMargin: "0px 0px -50px 0px"
    };

    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("animate-in");
                scrollObserver.unobserve(entry.target); // Stop observing once animated
            }
        });
    }, observerOptions);

    function handleScrollAnimations() {
        const scrolled = window.scrollY;
        
        // Optimally calculate scroll percent
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        const scrollPercent = docHeight > 0 ? scrolled / docHeight : 0;

        // Blob Parallax - Use translate3d for GPU acceleration
        const blobs = document.querySelectorAll(".glow-blob");
        blobs.forEach((blob, index) => {
            // Simplified math to reduce CPU load
            const yPos = scrolled * ((index + 1) * 0.15); 
            // Only rotate a bit based on scroll
            const rot = scrollPercent * 180;
            blob.style.transform = `translate3d(0, ${yPos}px, 0) rotate(${rot}deg)`;
        });

        // Navbar Effects
        const navbar = document.querySelector(".navbar");
        if (navbar) {
            if (scrolled > 50) {
                if (!navbar.classList.contains("scrolled")) navbar.classList.add("scrolled");
            } else {
                if (navbar.classList.contains("scrolled")) navbar.classList.remove("scrolled");
            }
        }

        ticking = false;
    }

    // Use passive listener for better scroll performance
    window.addEventListener("scroll", () => {
        if (!ticking) {
            window.requestAnimationFrame(handleScrollAnimations);
            ticking = true;
        }
    }, { passive: true });

    // Initialize Observers
    const elementsToObserve = [
        ".reveal", 
        ".service-detailed-card", 
        ".hero-content h1", 
        ".hero-description", 
        ".hero-cta", 
        ".hero-visual",
        "section",
        ".service-card",
        ".approach-item"
    ];
    
    elementsToObserve.forEach(selector => {
        document.querySelectorAll(selector).forEach(el => scrollObserver.observe(el));
    });

    // Close modal on outside click
    const modal = document.getElementById("bookingModal");
    if (modal) {
        modal.addEventListener("click", function(e) {
            if (e.target === modal) {
                closeBookingModal();
            }
        });
    }
});
