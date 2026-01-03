// static/js/scripts.js — FINAL VERSION (NO SPINNER ON NAVIGATION)
document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded');

    // =================================================================
    // SPINNER FIX — ONLY SHOWS ON FIRST VISIT, MAX 600ms
    // =================================================================
    const loadingElement = document.getElementById('loading');

    if (loadingElement) {
        // Only show spinner on FIRST visit
        if (!sessionStorage.getItem('siteVisited')) {
            console.log('First visit — showing spinner (max 600ms)');

            // Show spinner
            loadingElement.style.display = 'flex';

            const hideSpinner = () => {
                loadingElement.style.opacity = '0';
                setTimeout(() => {
                    loadingElement.style.display = 'none';
                    console.log('Spinner hidden');
                }, 300);
            };

            // Hide after max 600ms (even on slow internet)
            const maxTimer = setTimeout(hideSpinner, 600);

            // Or hide when everything loads (whichever comes first)
            window.addEventListener('load', () => {
                clearTimeout(maxTimer);
                hideSpinner();
            });

            // Remember user visited
            sessionStorage.setItem('siteVisited', 'true');
        } else {
            // Returning user — NO SPINNER
            loadingElement.style.display = 'none';
            console.log('Returning visitor — no spinner');
        }
    } else {
        console.error('Loading element not found');
    }

    // =================================================================
    // ALL YOUR ORIGINAL CODE — UNCHANGED & WORKING
    // =================================================================

    // Initialize AOS with error handling
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 1000, once: true, easing: 'ease-out' });
        console.log('AOS initialized');
    } else {
        console.warn('AOS library not loaded. Animations disabled.');
    }

    // Initialize Particles.js with more particles and interactivity
    if (typeof particlesJS !== 'undefined') {
        particlesJS("particles-js", {
            particles: {
                number: { value: 150, density: { enable: true, value_area: 600 } },
                color: { value: ["#ffffff", "#90caf9", "#3f51b5"] },
                shape: { type: "circle", stroke: { width: 0 } },
                opacity: { value: 0.7, random: true },
                size: { value: 6, random: true },
                move: { enable: true, speed: 3, direction: "none", random: true }
            },
            interactivity: {
                detect_on: "canvas",
                events: { onhover: { enable: true, mode: "repulse" }, onclick: { enable: true, mode: "push" } },
                modes: { repulse: { distance: 200, duration: 0.4 }, push: { particles_nb: 6 } }
            }
        });
        console.log('Particles.js initialized');
    } else {
        console.warn('Particles.js library not loaded.');
    }

    // GSAP Animations with Fallback
    if (typeof gsap !== 'undefined') {
        gsap.from(".hero-content .display-4", { opacity: 0, y: 50, duration: 1.2, ease: "power3.out" });
        gsap.from(".hero-content .lead", { opacity: 0, y: 30, duration: 1.2, delay: 0.3, ease: "power3.out" });
        gsap.from(".hero-content .btn-custom", { opacity: 0, scale: 0.8, duration: 1, delay: 0.6, stagger: 0.2, ease: "elastic.out(1, 0.5)" });
        gsap.from(".social-icons a", { opacity: 0, y: 20, duration: 1, delay: 0.8, stagger: 0.1, ease: "power3.out" });
        gsap.from(".card", { y: 60, opacity: 0, duration: 1.2, stagger: 0.3, ease: "power3.out" });
        console.log('GSAP animations applied');
    } else {
        console.warn('GSAP library not loaded. Animations disabled.');
    }

    // Button Hover Animation
    document.querySelectorAll('.btn-custom').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            if (!btn.disabled && typeof gsap !== 'undefined') {
                gsap.to(btn, { scale: 1.05, duration: 0.3, ease: "power2.out" });
            }
        });
        btn.addEventListener('mouseleave', () => {
            if (!btn.disabled && typeof gsap !== 'undefined') {
                gsap.to(btn, { scale: 1, duration: 0.3, ease: "power2.out" });
            }
        });
    });

    // Sticky Navbar
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 50) navbar.classList.add('sticky');
            else navbar.classList.remove('sticky');
        }
    });

    // Form Submission Handling (excluding businessForm, handled in template)
    const forms = document.querySelectorAll('#consumerForm, #feedbackForm');
    forms.forEach(form => {
        // Reset form on page load or modal close
        window.addEventListener('load', function () {
            form.reset();
            form.classList.remove('was-validated');
        });
        const modal = form.closest('.modal');
        if (modal) {
            modal.addEventListener('hidden.bs.modal', function () {
                form.reset();
                form.classList.remove('was-validated');
            });
        }

        form.addEventListener('submit', function(event) {
            event.preventDefault();
            let isValid = true;
            const submitBtn = form.querySelector('button[type="submit"]');
            let formStatus;

            if (form.id === 'consumerForm') formStatus = document.getElementById('consumerFormStatus');
            else if (form.id === 'feedbackForm') formStatus = document.getElementById('feedbackFormStatus');
            else formStatus = form.parentElement.querySelector('.form-status');

            if (!formStatus) {
                console.error('Form status element not found for form:', form.id);
                formStatus = document.createElement('div');
                form.parentElement.appendChild(formStatus);
            }

            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;

            if (!csrfToken) {
                formStatus.innerHTML = '<div class="alert alert-danger">CSRF token missing. Please refresh the page.</div>';
                return;
            }

            const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            const emailInputs = form.querySelectorAll('input[type="email"]');
            emailInputs.forEach(email => {
                const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (email.value && !emailPattern.test(email.value)) {
                    isValid = false;
                    email.classList.add('is-invalid');
                    const feedback = email.nextElementSibling;
                    if (feedback && feedback.classList.contains('invalid-feedback')) {
                        feedback.textContent = 'Please enter a valid email address.';
                    }
                }
            });

            if (!isValid) {
                formStatus.innerHTML = '<div class="alert alert-danger">Please correct the errors in the form.</div>';
                return;
            }

            submitBtn.disabled = true;
            submitBtn.innerHTML = form.id === 'consumerForm' ? 'Submitting...' : 'Submitting Feedback...';
            formStatus.innerHTML = '';

            const formData = new FormData(form);
            formData.append('csrfmiddlewaretoken', csrfToken);

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 30000);

            fetch(form.action || '/', {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
                signal: controller.signal
            })
            .then(response => {
                clearTimeout(timeoutId);
                if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = form.id === 'consumerForm' ? 'Submit' : 'Submit Feedback';
                if (data.success) {
                    formStatus.innerHTML = '<div class="alert alert-success">' + data.message + '</div>';
                    form.reset();
                    form.classList.remove('was-validated');
                    setTimeout(() => {
                        const modal = bootstrap.Modal.getInstance(form.closest('.modal'));
                        if (modal) modal.hide();
                        formStatus.innerHTML = '';
                    }, 2000);
                } else {
                    formStatus.innerHTML = '<div class="alert alert-danger">' + data.message + (data.errors ? '<ul>' + Object.entries(data.errors).map(([field, error]) => `<li>${field}: ${error}</li>`).join('') + '</ul>' : '') + '</div>';
                    console.log('Server response errors:', data.errors);
                }
            })
            .catch(error => {
                clearTimeout(timeoutId);
                submitBtn.disabled = false;
                submitBtn.innerHTML = form.id === 'consumerForm' ? 'Submit' : 'Submit Feedback';
                formStatus.innerHTML = '<div class="alert alert-danger">An error occurred: ' + (error.name === 'AbortError' ? 'Request timed out after 30 seconds.' : error.message) + ' Check console for details.</div>';
                console.error('Fetch error:', error);
            });
        });
    });

    // Blog Modals
    document.querySelectorAll('.blog-image').forEach(image => {
        image.addEventListener('click', () => {
            const blogId = image.closest('.card')?.getAttribute('data-bs-target')?.replace('#blogModal-', '');
            if (blogId) {
                const modal = new bootstrap.Modal(document.getElementById(`blogModal-${blogId}`));
                modal.show();
                const carousel = document.querySelector(`#blogCarousel-${blogId}`);
                if (carousel && carousel.querySelectorAll('.carousel-item').length > 1) {
                    new bootstrap.Carousel(carousel, { interval: 4000, ride: 'carousel' });
                }
            }
        });
    });

    // Image Hover Effect for Modal
    document.querySelectorAll('.blog-modal-image').forEach(image => {
        image.addEventListener('mouseenter', () => {
            image.style.transform = 'scale(1.5)';
            image.style.zIndex = '1';
        });
        image.addEventListener('mouseleave', () => {
            image.style.transform = 'scale(1)';
            image.style.zIndex = '0';
        });
    });
});