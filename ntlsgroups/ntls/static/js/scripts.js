document.addEventListener('DOMContentLoaded', function() {
    // GSAP Loading Animation
    gsap.to("#loading", { opacity: 0, duration: 1, delay: 1.5, onComplete: function() {
        document.getElementById("loading").style.display = "none";
    }});

    // Particles.js Hero Section
    particlesJS("particles-js", {
        particles: {
            number: { value: 100, density: { enable: true, value_area: 800 } },
            color: { value: "#ffffff" },
            shape: { type: "circle" },
            opacity: { value: 0.6, random: true },
            size: { value: 4, random: true },
            move: { enable: true, speed: 20, direction: "none", random: false }
        },
        interactivity: {
            detect_on: "canvas",
            events: { onhover: { enable: true, mode: "repulse" }, onclick: { enable: true, mode: "push" } },
            modes: { repulse: { distance: 120 }, push: { particles_nb: 4 } }
        }
    });

    // GSAP Animations
    gsap.to(".hero-text", { opacity: 1, y: 0, duration: 1.2, stagger: 0.3, ease: "power3.out" });
    gsap.from(".card", { y: 50, opacity: 0, duration: 1, stagger: 0.2, ease: "power3.out" });
    gsap.from(".btn-custom", { scale: 0.8, opacity: 0, duration: 0.8, stagger: 0.2, ease: "bounce.out" });

    // AOS Initialization
    AOS.init({
        duration: 1000,
        once: true,
        easing: 'ease-in-out'
    });

    // Button Hover Animation
    document.querySelectorAll('.btn-custom').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            if (!btn.disabled) {
                gsap.to(btn, { scale: 1.15, duration: 0.3, ease: "power3.out" });
            }
        });
        btn.addEventListener('mouseleave', () => {
            if (!btn.disabled) {
                gsap.to(btn, { scale: 1, duration: 0.3, ease: "power3.out" });
            }
        });
    });

    // Sticky Navbar
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('sticky');
        } else {
            navbar.classList.remove('sticky');
        }
    });

    // Initialize Tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Multi-Step Form Handling
    document.querySelectorAll('.next-step').forEach(button => {
        button.addEventListener('click', () => {
            const form = button.closest('form');
            const currentStep = button.closest('.form-step');
            const stepNumber = parseInt(currentStep.dataset.step);
            const nextStep = form.querySelector(`.form-step[data-step="${stepNumber + 1}"]`);
            const progressBar = form.querySelector('.progress-bar');
            const totalSteps = form.querySelectorAll('.form-step').length;

            if (nextStep) {
                currentStep.classList.remove('active');
                nextStep.classList.add('active');
                progressBar.style.width = `${((stepNumber + 1) / totalSteps) * 100}%`;
                progressBar.setAttribute('aria-valuenow', ((stepNumber + 1) / totalSteps) * 100);
                progressBar.textContent = `Step ${stepNumber + 1} of ${totalSteps}`;
                gsap.from(nextStep, { opacity: 0, x: 30, duration: 0.4, ease: "power2.out" });
            }
        });
    });

    document.querySelectorAll('.prev-step').forEach(button => {
        button.addEventListener('click', () => {
            const form = button.closest('form');
            const currentStep = button.closest('.form-step');
            const stepNumber = parseInt(currentStep.dataset.step);
            const prevStep = form.querySelector(`.form-step[data-step="${stepNumber - 1}"]`);
            const progressBar = form.querySelector('.progress-bar');
            const totalSteps = form.querySelectorAll('.form-step').length;

            if (prevStep) {
                currentStep.classList.remove('active');
                prevStep.classList.add('active');
                progressBar.style.width = `${((stepNumber - 1) / totalSteps) * 100}%`;
                progressBar.setAttribute('aria-valuenow', ((stepNumber - 1) / totalSteps) * 100);
                progressBar.textContent = `Step ${stepNumber - 1} of ${totalSteps}`;
                gsap.from(prevStep, { opacity: 0, x: -30, duration: 0.4, ease: "power2.out" });
            }
        });
    });

    // Form Submission Handling
    const forms = document.querySelectorAll('#consumerForm, #businessForm, #feedbackForm');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            let isValid = true;
            const submitBtn = form.querySelector('button[type="submit"]');
            const formStatus = form.parentElement.querySelector('.form-status');

            // Client-side validation
            const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.classList.add('is-invalid');
                } else {
                    input.classList.remove('is-invalid');
                }
            });

            // Email validation
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

            // File validation for business form
            const fileInput = form.querySelector('#id_file_upload');
            if (fileInput) {
                const file = fileInput.files[0];
                if (file && !file.name.endsWith('.pdf')) {
                    isValid = false;
                    fileInput.classList.add('is-invalid');
                    const feedback = fileInput.nextElementSibling;
                    if (feedback && feedback.classList.contains('invalid-feedback')) {
                        feedback.textContent = 'Please upload a PDF file.';
                    }
                }
            }

            const logoInput = form.querySelector('#id_logo');
            if (logoInput && logoInput.files[0]) {
                const file = logoInput.files[0];
                const validExtensions = ['.jpg', '.jpeg', '.png'];
                if (!validExtensions.some(ext => file.name.toLowerCase().endsWith(ext))) {
                    isValid = false;
                    logoInput.classList.add('is-invalid');
                    const feedback = logoInput.nextElementSibling;
                    if (feedback && feedback.classList.contains('invalid-feedback')) {
                        feedback.textContent = 'Please upload a JPG or PNG file.';
                    }
                }
                if (file.size > 5 * 1024 * 1024) {
                    isValid = false;
                    logoInput.classList.add('is-invalid');
                    const feedback = logoInput.nextElementSibling;
                    if (feedback && feedback.classList.contains('invalid-feedback')) {
                        feedback.textContent = 'File size must be under 5MB.';
                    }
                }
            }

            if (!isValid) {
                formStatus.innerHTML = '<div class="alert alert-danger">Please correct the errors in the form.</div>';
                return;
            }

            // Disable button without spinner
            submitBtn.disabled = true;
            submitBtn.innerHTML = submitBtn.id === 'consumerSubmitBtn' ? 'Submitting...' : submitBtn.id === 'businessSubmitBtn' ? 'Applying...' : 'Submitting Feedback...';
            formStatus.innerHTML = '';

            // Submit form via fetch
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.id === 'consumerSubmitBtn' ? 'Submit Now' : submitBtn.id === 'businessSubmitBtn' ? 'Apply Now' : 'Submit Feedback';
                if (data.success) {
                    formStatus.innerHTML = '<div class="alert alert-success">' + data.message + '</div>';
                    form.reset();
                    setTimeout(() => {
                        const modal = bootstrap.Modal.getInstance(form.closest('.modal'));
                        if (modal) modal.hide();
                        formStatus.innerHTML = '';
                        inputs.forEach(input => input.classList.remove('is-invalid'));
                        form.querySelectorAll('.form-step').forEach(step => step.classList.remove('active'));
                        form.querySelector('.form-step[data-step="1"]').classList.add('active');
                        const progressBar = form.querySelector('.progress-bar');
                        progressBar.style.width = `${(1 / form.querySelectorAll('.form-step').length) * 100}%`;
                        progressBar.setAttribute('aria-valuenow', (1 / form.querySelectorAll('.form-step').length) * 100);
                        progressBar.textContent = `Step 1 of ${form.querySelectorAll('.form-step').length}`;
                    }, 2000);
                } else {
                    formStatus.innerHTML = '<div class="alert alert-danger">' + data.message + '<ul>' + Object.entries(data.errors || {}).map(([field, error]) => `<li>${field}: ${error}</li>`).join('') + '</ul></div>';
                }
            })
            .catch(error => {
                submitBtn.disabled = false;
                submitBtn.innerHTML = submitBtn.id === 'consumerSubmitBtn' ? 'Submit Now' : submitBtn.id === 'businessSubmitBtn' ? 'Apply Now' : 'Submit Feedback';
                formStatus.innerHTML = '<div class="alert alert-danger">An error occurred. Please try again.</div>';
            });
        });
    });

    // Category Filter Handling
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.addEventListener('change', function() {
            const category = this.value;
            const partnersContainer = document.getElementById('partnersContainer');
            partnersContainer.style.opacity = '0.3';
            fetch(`/?category=${encodeURIComponent(category)}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newPartnersContainer = doc.getElementById('partnersContainer');
                partnersContainer.innerHTML = newPartnersContainer.innerHTML;
                gsap.fromTo(partnersContainer, { opacity: 0.3 }, { opacity: 1, duration: 0.6 });
                AOS.refresh();
            })
            .catch(error => {
                console.error('Error filtering partners:', error);
                partnersContainer.style.opacity = '1';
            });
        });
    }
});