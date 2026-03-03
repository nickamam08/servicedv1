/**
 * Admin Dashboard Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
});

async function loadDashboardStats() {
    try {
        // Wait a small moment to ensure auth is checked/processed
        const token = sessionStorage.getItem('serviced_token');
        if (!token) {
            console.warn('Waiting for token...');
            return;
        }

        console.log('Fetching Dashboard Overview...');
        const stats = await apiFetch('/admin/dashboard/overview');
        if (stats) displayStats(stats);

        console.log('Fetching Recent Requests for Activity...');
        const requests = await apiFetch('/admin/dashboard/requests');
        if (requests) displayActivity(requests);

    } catch (error) {
        console.error('Error loading dashboard stats:', error);
    }
}

function displayStats(stats) {
    console.log('Rendering Dashboard Stats:', stats);

    document.getElementById('total-users').textContent = (stats.total_users || 0).toLocaleString();
    document.getElementById('total-providers').textContent = (stats.total_providers || 0).toLocaleString();
    document.getElementById('total-services').textContent = (stats.total_services || 0).toLocaleString();
    document.getElementById('total-requests').textContent = (stats.total_requests || 0).toLocaleString();

    document.getElementById('users-growth').textContent = `+${stats.new_users_last_30_days || 0} nuevos`;
    document.getElementById('requests-growth').textContent = `+${stats.new_requests_last_30_days || 0} nuevos`;
}

function displayActivity(requests) {
    console.log('Rendering Recent Activity:', requests);
    const tbody = document.getElementById('recent-activity-body');
    if (!tbody) {
        console.error('Element recent-activity-body not found');
        return;
    }

    tbody.innerHTML = '';

    if (!requests || requests.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="padding: 16px 24px; text-align: center;">No hay actividad reciente.</td></tr>';
        return;
    }

    // Show last 5 requests as "activity"
    const displayItems = Array.isArray(requests) ? requests.slice(0, 5) : [];

    displayItems.forEach(req => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid var(--border)';
        tr.innerHTML = `
            <td style="padding: 16px 24px; font-weight: 500;">Solicitud #${req.id}</td>
            <td style="padding: 16px 24px;">
                <span class="badge ${getStatusBadge(req.status)}">${(req.status || 'unknown').toUpperCase()}</span>
            </td>
            <td style="padding: 16px 24px; color: var(--text-secondary);">
                ${req.client_name || 'Desconocido'} contrató a <strong>${req.provider_name || 'N/A'}</strong>
            </td>
            <td style="padding: 16px 24px; text-align: right; color: var(--text-tertiary);">
                ${req.created_at ? new Date(req.created_at).toLocaleDateString() : 'N/D'}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function getStatusBadge(status) {
    if (status === 'completed') return 'badge-success';
    if (status === 'cancelled') return 'badge-danger';
    if (status === 'active' || status === 'in_progress') return 'badge-primary';
    return 'badge-warning';
}
