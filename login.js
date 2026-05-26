/* ==========================================================================
   PRODUCT MANAGEMENT SYSTEM - LOGIN SCRIPT
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('emailInput');
    const passwordInput = document.getElementById('passwordInput');
    const emailError = document.getElementById('emailError');
    const passwordError = document.getElementById('passwordError');
    const passwordToggle = document.getElementById('passwordToggle');
    const toggleIcon = document.getElementById('toggleIcon');
    const loadingOverlay = document.getElementById('loadingOverlay');

    // --- 1. Toast Notification Utility ---
    window.showToast = function(message, type = 'success') {
        const toast = document.getElementById('toastNotification');
        const toastIcon = document.getElementById('toastIcon');
        const toastMessage = document.getElementById('toastMessage');

        // Clear previous alert classes
        toast.className = 'alert-toast';
        toastIcon.className = 'bi alert-toast-icon';

        // Map icons and colors
        if (type === 'success') {
            toast.classList.add('success');
            toastIcon.classList.add('bi-check-circle-fill');
        } else if (type === 'danger') {
            toast.classList.add('danger');
            toastIcon.classList.add('bi-exclamation-triangle-fill');
        } else if (type === 'warning') {
            toast.classList.add('warning');
            toastIcon.classList.add('bi-exclamation-circle-fill');
        } else {
            toast.classList.add('info');
            toastIcon.classList.add('bi-info-circle-fill');
        }

        toastMessage.textContent = message;
        toast.classList.add('show');

        // Auto hide after 4 seconds
        setTimeout(() => {
            toast.classList.remove('show');
        }, 4000);
    };

    // --- 2. Password Visibility Toggle ---
    if (passwordToggle) {
        passwordToggle.addEventListener('click', () => {
            const isPassword = passwordInput.getAttribute('type') === 'password';
            passwordInput.setAttribute('type', isPassword ? 'text' : 'password');
            
            // Update icons
            toggleIcon.className = isPassword ? 'bi bi-eye-slash' : 'bi bi-eye';
        });
    }

    // --- 3. Input Validation Functions ---
    const validateEmail = (email) => {
        const regex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return regex.test(String(email).toLowerCase());
    };

    const clearErrors = () => {
        emailInput.classList.remove('is-invalid');
        passwordInput.classList.remove('is-invalid');
        emailError.textContent = '';
        passwordError.textContent = '';
    };

    // --- 4. Form Submission and API Integration ---
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        clearErrors();

        const email = emailInput.value.trim();
        const password = passwordInput.value;
        let isValid = true;

        // Validation checks
        if (!email) {
            emailInput.classList.add('is-invalid');
            emailError.textContent = 'Email address is required.';
            isValid = false;
        } else if (!validateEmail(email)) {
            emailInput.classList.add('is-invalid');
            emailError.textContent = 'Please enter a valid email address.';
            isValid = false;
        }

        if (!password) {
            passwordInput.classList.add('is-invalid');
            passwordError.textContent = 'Password is required.';
            isValid = false;
        } else if (password.length < 6) {
            passwordInput.classList.add('is-invalid');
            passwordError.textContent = 'Password must be at least 6 characters.';
            isValid = false;
        }

        // Stop if client validation fails
        if (!isValid) return;

        // Show spinner loader
        loadingOverlay.classList.add('active');

        try {
            // Trigger REST API call
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            const result = await response.json();
            
            if (response.ok && result.success) {
                // Success path
                showToast(result.message || 'Login successful! Redirecting...', 'success');
                
                // Store user session state on client side if needed
                localStorage.setItem('userEmail', email);

                // Small delay for smooth toast transition before page swap
                setTimeout(() => {
                    window.location.href = '/products';
                }, 1500);
            } else {
                // Failure path
                loadingOverlay.classList.remove('active');
                showToast(result.message || 'Authentication failed.', 'danger');
                passwordInput.value = ''; // Reset password field on error
            }
        } catch (error) {
            loadingOverlay.classList.remove('active');
            console.error('Login error:', error);
            showToast('Unable to connect to the server. Please check XAMPP and try again.', 'danger');
        }
    });

    // --- 5. Flash Message Handler ---
    // If redirected from logout or authorization checkpoints with messages
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('unauthorized')) {
        showToast('Session expired. Please sign in again.', 'warning');
    }
});
