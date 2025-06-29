// Main JavaScript for Telehealth Diabetes Care

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scrolling for anchor links
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

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('.needs-validation');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Loading spinner for forms
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                this.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status"></span>Processing...';
                this.disabled = true;
            }
        });
    });

    // Navbar scroll effect
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('navbar-scrolled');
        } else {
            navbar.classList.remove('navbar-scrolled');
        }
    });

    // Counter animation for statistics
    const counters = document.querySelectorAll('.stat-item h3');
    const animateCounters = () => {
        counters.forEach(counter => {
            const target = parseInt(counter.textContent.replace(/[^\d]/g, ''));
            const increment = target / 100;
            let current = 0;
            
            const updateCounter = () => {
                if (current < target) {
                    current += increment;
                    counter.textContent = Math.ceil(current) + counter.textContent.replace(/\d/g, '').replace(/^\d+/, '');
                    setTimeout(updateCounter, 20);
                } else {
                    counter.textContent = counter.textContent.replace(/^\d+/, target);
                }
            };
            
            updateCounter();
        });
    };

    // Intersection Observer for counter animation
    const observerOptions = {
        threshold: 0.5,
        rootMargin: '0px 0px -100px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounters();
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const statsSection = document.querySelector('.bg-light');
    if (statsSection) {
        observer.observe(statsSection);
    }

    // Glucose level input validation
    const glucoseInputs = document.querySelectorAll('input[name*="glucose"]');
    glucoseInputs.forEach(input => {
        input.addEventListener('input', function() {
            const value = parseFloat(this.value);
            const feedback = this.nextElementSibling;
            
            if (value < 70) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (feedback) feedback.textContent = 'Low glucose level - consult your doctor';
            } else if (value > 180) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (feedback) feedback.textContent = 'High glucose level - consult your doctor';
            } else {
                this.classList.add('is-valid');
                this.classList.remove('is-invalid');
                if (feedback) feedback.textContent = 'Normal range';
            }
        });
    });

    // Date picker restrictions (no future dates for glucose readings)
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        if (input.name.includes('reading_date') || input.name.includes('glucose_date')) {
            const today = new Date().toISOString().split('T')[0];
            input.setAttribute('max', today);
        }
    });

    // Appointment time validation
    const timeInputs = document.querySelectorAll('input[type="time"]');
    timeInputs.forEach(input => {
        input.addEventListener('change', function() {
            const selectedTime = this.value;
            const [hours, minutes] = selectedTime.split(':').map(Number);
            const totalMinutes = hours * 60 + minutes;
            
            // Business hours: 8 AM to 6 PM
            const startTime = 8 * 60; // 8 AM
            const endTime = 18 * 60;  // 6 PM
            
            if (totalMinutes < startTime || totalMinutes > endTime) {
                this.setCustomValidity('Please select a time between 8:00 AM and 6:00 PM');
            } else {
                this.setCustomValidity('');
            }
        });
    });

    // Password strength indicator
    const passwordInputs = document.querySelectorAll('input[type="password"]');
    passwordInputs.forEach(input => {
        if (input.name === 'password1' || input.name === 'new_password1') {
            input.addEventListener('input', function() {
                const password = this.value;
                const strengthIndicator = document.getElementById('password-strength');
                
                if (strengthIndicator) {
                    const strength = calculatePasswordStrength(password);
                    updatePasswordStrengthIndicator(strengthIndicator, strength);
                }
            });
        }
    });

    // Utility Functions
    function calculatePasswordStrength(password) {
        let score = 0;
        
        if (password.length >= 8) score++;
        if (/[a-z]/.test(password)) score++;
        if (/[A-Z]/.test(password)) score++;
        if (/\d/.test(password)) score++;
        if (/[^a-zA-Z\d]/.test(password)) score++;
        
        return score;
    }

    function updatePasswordStrengthIndicator(indicator, strength) {
        const levels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const colors = ['danger', 'warning', 'info', 'success', 'success'];
        
        indicator.textContent = levels[strength] || 'Very Weak';
        indicator.className = `text-${colors[strength] || 'danger'}`;
    }

    // CSRF Token for AJAX requests
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Set CSRF token for all AJAX requests
    const csrftoken = getCookie('csrftoken');
    if (csrftoken) {
        // For jQuery AJAX (if used)
        if (typeof $ !== 'undefined') {
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                }
            });
        }
        
        // For fetch API
        window.csrftoken = csrftoken;
    }

    // Print functionality
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(button => {
        button.addEventListener('click', function() {
            window.print();
        });
    });

    // Back to top button
    const backToTopButton = document.createElement('button');
    backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
    backToTopButton.className = 'btn btn-primary position-fixed';
    backToTopButton.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000; border-radius: 50%; width: 50px; height: 50px; display: none;';
    backToTopButton.setAttribute('aria-label', 'Back to top');
    document.body.appendChild(backToTopButton);

    window.addEventListener('scroll', function() {
        if (window.scrollY > 300) {
            backToTopButton.style.display = 'block';
        } else {
            backToTopButton.style.display = 'none';
        }
    });

    backToTopButton.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
});

// Global utility functions
window.showAlert = function(message, type = 'info') {
    const alertContainer = document.querySelector('.container-fluid');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show mt-3`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.insertBefore(alert, alertContainer.firstChild);
    
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    }, 5000);
};

window.formatDate = function(dateString) {
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
};

window.formatTime = function(timeString) {
    const options = { hour: '2-digit', minute: '2-digit' };
    return new Date(`2000-01-01T${timeString}`).toLocaleTimeString(undefined, options);
};
