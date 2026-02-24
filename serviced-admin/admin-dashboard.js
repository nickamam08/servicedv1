/**
 * Admin Dashboard Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    loadDashboardStats();
});

async function loadDashboardStats() {
    try {
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
    const tbody = document.getElementById('recent-activity-body');
    if (!tbody) return;

    tbody.innerHTML = '';
    // Show last 5 requests as "activity"
    requests.slice(0, 5).forEach(req => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid var(--border)';
        tr.innerHTML = `
            <td style="padding: 16px 24px; font-weight: 500;">Solicitud #${req.id}</td>
            <td style="padding: 16px 24px;">
                <span class="badge ${getStatusBadge(req.status)}">${req.status.toUpperCase()}</span>
            </td>
            <td style="padding: 16px 24px; color: var(--text-secondary);">
                ${req.client_name} contrató a <strong>${req.provider_name}</strong>
            </td>
            <td style="padding: 16px 24px; text-align: right; color: var(--text-tertiary);">
                ${new Date(req.created_at).toLocaleDateString()}
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
