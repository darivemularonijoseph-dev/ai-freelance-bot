/* ============================================
   AutomateHyd — Interactive JavaScript
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

    // === Navbar Scroll Effect ===
    const navbar = document.getElementById('navbar');
    let lastScroll = 0;

    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        if (currentScroll > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
        lastScroll = currentScroll;
    });

    // === Mobile Menu Toggle ===
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const navLinks = document.getElementById('navLinks');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            mobileMenuBtn.classList.toggle('active');
        });

        // Close menu when clicking a link
        navLinks.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', () => {
                navLinks.classList.remove('active');
                mobileMenuBtn.classList.remove('active');
            });
        });
    }

    // === Scroll Animations (Intersection Observer) ===
    const animateElements = document.querySelectorAll('.animate-in');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, index * 100);
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    animateElements.forEach(el => observer.observe(el));

    // === Animated Counters ===
    const statNumbers = document.querySelectorAll('.stat-number');

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.getAttribute('data-target'));
                animateCounter(entry.target, target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(el => counterObserver.observe(el));

    function animateCounter(element, target) {
        let current = 0;
        const duration = 1500;
        const stepTime = 30;
        const steps = duration / stepTime;
        const increment = target / steps;

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            element.textContent = Math.round(current);
        }, stepTime);
    }

    // === Chat Demo Animation ===
    const typingIndicator = document.getElementById('typingIndicator');
    const finalMsg = document.getElementById('finalMsg');
    const chatAlert = document.getElementById('chatAlert');

    // Simulate typing → response → alert after delay
    setTimeout(() => {
        if (typingIndicator && finalMsg) {
            typingIndicator.style.display = 'none';
            finalMsg.style.display = 'block';

            setTimeout(() => {
                if (chatAlert) {
                    chatAlert.classList.add('visible');
                }
            }, 800);
        }
    }, 3000);

    // === FAQ Accordion ===
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');

        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');

            // Close all others
            faqItems.forEach(otherItem => {
                otherItem.classList.remove('active');
                const otherQuestion = otherItem.querySelector('.faq-question');
                if (otherQuestion) otherQuestion.setAttribute('aria-expanded', 'false');
            });

            // Toggle current
            if (!isActive) {
                item.classList.add('active');
                question.setAttribute('aria-expanded', 'true');
            }
        });
    });

    // === Contact Form Handling ===
    const contactForm = document.getElementById('contactForm');
    const submitBtn = document.getElementById('submitBtn');

    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const formData = new FormData(contactForm);
            const data = Object.fromEntries(formData.entries());

            // Disable button
            submitBtn.disabled = true;
            submitBtn.textContent = 'Sending...';
            submitBtn.style.opacity = '0.7';

            // Simulate form submission (replace with actual endpoint)
            setTimeout(() => {
                submitBtn.textContent = '✓ Audit Request Sent!';
                submitBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                submitBtn.style.opacity = '1';

                // Build WhatsApp message
                const whatsappMsg = encodeURIComponent(
                    `Hi Roni! I'd like a free automation audit.\n\n` +
                    `Name: ${data.name}\n` +
                    `Phone: ${data.phone}\n` +
                    `Business: ${data.business}\n` +
                    `Bottleneck: ${data.message || 'Not specified'}`
                );

                // Open WhatsApp after a brief delay
                setTimeout(() => {
                    window.open(`https://wa.me/919XXXXXXXXX?text=${whatsappMsg}`, '_blank');
                }, 1000);

                // Reset after 3 seconds
                setTimeout(() => {
                    contactForm.reset();
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Get My Free Audit →';
                    submitBtn.style.background = '';
                }, 4000);
            }, 1500);
        });
    }

    // === Smooth Scroll for Nav Links ===
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
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

    // === Section Reveal Animations ===
    const sections = document.querySelectorAll('.problem-card, .service-card, .step, .result-card, .testimonial-card, .pricing-card, .faq-item');

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '0';
                entry.target.style.transform = 'translateY(20px)';
                entry.target.style.transition = `opacity 0.5s ease ${index * 0.08}s, transform 0.5s ease ${index * 0.08}s`;

                requestAnimationFrame(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                });

                sectionObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    sections.forEach(el => sectionObserver.observe(el));

    // === Parallax Effect on Hero Glow ===
    const glows = document.querySelectorAll('.bg-glow');

    window.addEventListener('mousemove', (e) => {
        const x = (e.clientX / window.innerWidth - 0.5) * 20;
        const y = (e.clientY / window.innerHeight - 0.5) * 20;

        glows.forEach((glow, i) => {
            const speed = (i + 1) * 0.5;
            glow.style.transform = `translate(${x * speed}px, ${y * speed}px)`;
        });
    });

});
