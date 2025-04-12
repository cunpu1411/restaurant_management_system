// Handle login form submission
const loginForm = document.getElementById('login-form');
if (loginForm) {
    console.log('Login form found, attaching event listener');
    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        
        console.log('Attempting login for user:', username);
        
        // Show the error div for debugging
        const errorElement = document.getElementById('login-error');
        if (errorElement) {
            errorElement.textContent = 'Đang thực hiện đăng nhập...';
            errorElement.classList.remove('d-none');
        }
        
        fetch('/api/v1/auth/login/json', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password }),
            credentials: 'include'
        })
        .then(response => {
            console.log('Login response status:', response.status);
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.detail || 'Đăng nhập thất bại');
                });
            }
            return response.json();
        })
        .then(data => {
            console.log('Login successful');
            // Trực tiếp chuyển hướng đến dashboard
            window.location.href = '/dashboard';
        })
        .catch(error => {
            console.error('Login error:', error);
            if (errorElement) {
                errorElement.textContent = error.message || 'Đăng nhập thất bại';
                errorElement.classList.remove('d-none');
            }
        });
    });
} else {
    console.warn('Login form not found');
}