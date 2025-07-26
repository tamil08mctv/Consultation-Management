document.addEventListener('DOMContentLoaded', function() {
    // GSAP Loading Animation
    gsap.to("#loading", { opacity: 0, duration: 1, delay: 2, onComplete: function() {
        document.getElementById("loading").style.display = "none";
    }});

    // Particles.js Hero Section
    particlesJS("particles-js", {
        particles: {
            number: { value: 80, density: { enable: true, value_area: 800 } },
            color: { value: "#ffffff" },
            shape: { type: "circle" },
            opacity: { value: 0.5, random: true },
            size: { value: 3, random: true },
            move: { enable: true, speed: 6, direction: "none", random: false }
        },
        interactivity: {
            detect_on: "canvas",
            events: { onhover: { enable: true, mode: "repulse" }, onclick: { enable: true, mode: "push" } },
            modes: { repulse: { distance: 100 }, push: { particles_nb: 4 } }
        }
    });

    // GSAP Animations
    gsap.to(".hero-text", { opacity: 1, y: 0, duration: 1, stagger: 0.3 });
    gsap.from(".card", { y: 50, opacity: 0, duration: 1, stagger: 0.2, ease: "power2.out" });

    // AOS Initialization
    AOS.init({
        duration: 800,
        once: true,
        easing: 'ease-in-out'
    });

    // Button Hover Animation
    document.querySelectorAll('.btn-custom').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            if (!btn.disabled) {
                gsap.to(btn, { scale: 1.1, duration: 0.3, ease: "power2.out" });
            }
        });
        btn.addEventListener('mouseleave', () => {
            if (!btn.disabled) {
                gsap.to(btn, { scale: 1, duration: 0.3, ease: "power2.out" });
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

            // Show loading state
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Submitting...';
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
});