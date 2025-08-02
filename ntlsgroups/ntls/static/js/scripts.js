document.addEventListener('DOMContentLoaded', function() {
    // GSAP Loading Animation
    gsap.to("#loading", { opacity: 0, duration: 1.5, delay: 2, onComplete: function() {
        document.getElementById("loading").style.display = "none";
    }});

    // Particles.js Hero Section
    particlesJS("particles-js", {
        particles: {
            number: { value: 80, density: { enable: true, value_area: 800 } },
            color: { value: ["#ffffff", "#90caf9", "#3f51b5"] },
            shape: { type: "circle", stroke: { width: 0 } },
            opacity: { value: 0.6, random: true },
            size: { value: 5, random: true },
            move: { enable: true, speed: 2, direction: "none", random: true }
        },
        interactivity: {
            detect_on: "canvas",
            events: { onhover: { enable: true, mode: "repulse" }, onclick: { enable: true, mode: "push" } },
            modes: { repulse: { distance: 150, duration: 0.4 }, push: { particles_nb: 4 } }
        }
    });

    // GSAP Animations
    gsap.from(".hero-content .display-4", { opacity: 0, y: 50, duration: 1.2, ease: "power3.out" });
    gsap.from(".hero-content .lead", { opacity: 0, y: 30, duration: 1.2, delay: 0.3, ease: "power3.out" });
    gsap.from(".hero-content .btn-custom", { opacity: 0, scale: 0.8, duration: 1, delay: 0.6, stagger: 0.2, ease: "elastic.out(1, 0.5)" });
    gsap.from(".social-icons a", { opacity: 0, y: 20, duration: 1, delay: 0.8, stagger: 0.1, ease: "power3.out" });
    gsap.from(".card", { y: 60, opacity: 0, duration: 1.2, stagger: 0.3, ease: "power3.out" });

    // AOS Initialization
    AOS.init({
        duration: 1000,
        once: true,
        easing: 'ease-out'
    });

    // Button Hover Animation
    document.querySelectorAll('.btn-custom').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            if (!btn.disabled) {
                gsap.to(btn, { scale: 1.05, duration: 0.3, ease: "power2.out" });
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

    // Form Submission Handling
    const forms = document.querySelectorAll('#consumerForm, #businessForm, #feedbackForm');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            event.preventDefault();
            let isValid = true;
            const submitBtn = form.querySelector('button[type="submit"]');
            const formStatus = form.parentElement.querySelector('.form-status');

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

            submitBtn.disabled = true;
            submitBtn.innerHTML = submitBtn.id === 'consumerSubmitBtn' ? 'Submitting...' : submitBtn.id === 'businessSubmitBtn' ? 'Applying...' : 'Submitting Feedback...';
            formStatus.innerHTML = '';

            fetch(form.action, {
                method: 'POST',
                body: new FormData(form),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
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

    // Blog Modals
    document.querySelectorAll('.blog-image').forEach(image => {
        image.addEventListener('click', () => {
            const blogId = image.closest('.card').getAttribute('data-bs-target').replace('#blogModal-', '');
            const modal = new bootstrap.Modal(document.getElementById(`blogModal-${blogId}`));
            modal.show();
            const carousel = document.querySelector(`#blogCarousel-${blogId}`);
            if (carousel && carousel.querySelectorAll('.carousel-item').length > 1) {
                new bootstrap.Carousel(carousel, { interval: 4000, ride: 'carousel' });
            }
        });
    });
});