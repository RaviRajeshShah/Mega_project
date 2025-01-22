// Handle login and registration toggle
document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const loginForm = document.getElementById('loginForm');
    const registerLink = document.getElementById('registerLink');
    const loginLink = document.getElementById('loginLink');

    if (registerLink) {
        registerLink.addEventListener('click', (e) => {
            e.preventDefault();
            loginForm.style.display = 'none';
            registerForm.style.display = 'block';
        });
    }

    if (loginLink) {
        loginLink.addEventListener('click', (e) => {
            e.preventDefault();
            registerForm.style.display = 'none';
            loginForm.style.display = 'block';
        });
    }

    // Set dynamic title for upload page
    const urlParams = new URLSearchParams(window.location.search);
    const type = urlParams.get('type');
    if (type && document.getElementById('pageTitle')) {
        document.getElementById('pageTitle').textContent = `Upload Your ${type === 'image' ? 'Image' : 'Video'}`;
    }
});
