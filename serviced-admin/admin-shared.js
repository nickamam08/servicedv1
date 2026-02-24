/**
 * Shared logic for Admin Panel
 */

const API_BASE_URL = "/api/v1";

document.addEventListener('DOMContentLoaded', () => {
    checkAdminAuth();
    setupAdminUI();
});

function checkAdminAuth() {
    const token = sessionStorage.getItem('serviced_token');
    if (!token) {
        console.warn('No admin token found. Redirecting to login.');
        window.location.replace('/users/login.html');
        return;
    }

    // Optional: Decode token to check role without API call first
    // For now, we'll rely on API returning 403/401
}

function getAuthHeaders() {
    const token = sessionStorage.getItem('serviced_token');
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
}

async function apiFetch(endpoint, options = {}) {
    const headers = getAuthHeaders();
    const url = `${API_BASE_URL}${endpoint}`;
    console.log(`Admin API Request: ${url}`, options);

    try {
        const response = await fetch(url, {
            ...options,
            headers: {
                ...headers,
                ...options.headers
            }
        });

        console.log(`Admin API Response (${response.status}): ${url}`);

        if (response.status === 401 || response.status === 403) {
            console.warn('Authentication error or unauthorized. Redirecting to login.');
            sessionStorage.removeItem('serviced_token');
            window.location.replace('/users/login.html');
            return null;
        }

        if (!response.ok) {
            let errorMessage = 'API Error';
            try {
                const error = await response.json();
                errorMessage = error.detail || errorMessage;
            } catch (e) {
                errorMessage = response.statusText;
            }
            console.error('API Error Response:', errorMessage);
            alert(`Error: ${errorMessage}`);
            throw new Error(errorMessage);
        }

        if (response.status === 204) return null;
        return await response.json();
    } catch (err) {
        console.error(`Fetch error for ${url}:`, err);
        throw err;
    }
}

function setupAdminUI() {
    // Setup Logout
    const logoutBtn = document.querySelector('.logout-link');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log('Logging out admin...');
            sessionStorage.removeItem('serviced_token');
            sessionStorage.removeItem('serviced_user');
            window.location.replace('/users/login.html');
        });
    }

    // Set Admin Initial
    const user = JSON.parse(sessionStorage.getItem('serviced_user') || '{}');
    const avatar = document.querySelector('.user-avatar');
    if (avatar && user.full_name) {
        avatar.textContent = user.full_name.substring(0, 2).toUpperCase();
    }
}
