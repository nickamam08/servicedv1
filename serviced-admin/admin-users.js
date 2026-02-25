/**
 * Admin Users Management Logic
 */

let allUsers = [];

document.addEventListener('DOMContentLoaded', () => {
    console.log('Admin Users JS Loaded - V2 (With Delete Button)');
    // alert('¡Sistema de administración V2 cargado!');
    loadUsers();
    setupFilters();
});

async function loadUsers() {
    try {
        const role = document.getElementById('role-filter')?.value || 'all';
        const status = document.getElementById('status-filter')?.value || 'all';
        const search = document.getElementById('search-input')?.value || '';

        console.log('Loading users with filters:', { role, status, search });

        let queryParams = [];
        if (role && role !== 'all') queryParams.push(`role=${role}`);
        if (status && status !== 'all') queryParams.push(`is_active=${status === 'active'}`);
        if (search) queryParams.push(`search=${encodeURIComponent(search)}`);

        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
        const users = await apiFetch(`/admin/dashboard/users${queryString}`);

        if (!users) return;

        allUsers = users;
        displayUsers(users);
        updateStats(users);
    } catch (error) {
        console.error('Error loading users:', error);
    }
}

function displayUsers(users) {
    const tbody = document.getElementById('users-table-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (users.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 24px;">No se encontraron usuarios.</td></tr>';
        return;
    }

    users.forEach(user => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid var(--border)';
        tr.innerHTML = `
            <td style="padding: 16px 24px;">
                <div style="font-weight: 600;">${user.full_name}</div>
                <div style="font-size: 0.8rem; color: var(--text-secondary);">${user.email}</div>
            </td>
            <td style="padding: 16px 24px;"><span class="badge ${getRoleBadgeClass(user.role)}">${capitalize(user.role)}</span></td>
            <td style="padding: 16px 24px;"><span class="badge ${user.is_active ? 'badge-success' : 'badge-danger'}">${user.is_active ? 'Activo' : 'Inactivo'}</span></td>
            <td style="padding: 16px 24px; color: var(--text-secondary);">${new Date(user.created_at).toLocaleDateString('es-ES')}</td>
            <td style="padding: 16px 24px;">
                <div style="display: flex; gap: 8px;">
                    <button class="btn ${user.is_active ? 'btn-outline' : 'btn-primary'}" 
                            style="padding: 4px 12px; font-size: 0.8rem;"
                            onclick="toggleUserStatus(${user.id}, ${user.is_active})">
                        ${user.is_active ? 'Desactivar' : 'Activar'}
                    </button>
                    <button class="btn btn-danger" 
                            style="padding: 4px 12px; font-size: 0.8rem; background-color: #ef4444; color: white; border: none;"
                            onclick="deleteUser(${user.id}, '${user.full_name}')">
                        Eliminar
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function deleteUser(userId, userName) {
    if (!confirm(`¿Estás seguro de que deseas eliminar permanentemente al usuario ${userName}? Esta acción no se puede deshacer y eliminará todos sus datos asociados.`)) {
        return;
    }

    try {
        await apiFetch(`/admin/dashboard/users/${userId}`, { method: 'DELETE' });
        loadUsers();
    } catch (error) {
        alert('Error al eliminar usuario: ' + error.message);
    }
}

function updateStats(users) {
    const totalStat = document.getElementById('users-total-stat');
    const activeStat = document.getElementById('users-active-stat');
    const providersStat = document.getElementById('users-providers-stat');

    if (totalStat) totalStat.textContent = users.length.toLocaleString();
    if (activeStat) activeStat.textContent = users.filter(u => u.is_active).length.toLocaleString();
    if (providersStat) providersStat.textContent = users.filter(u => u.role === 'provider').length.toLocaleString();
}

function setupFilters() {
    const searchInput = document.getElementById('search-input');
    const roleFilter = document.getElementById('role-filter');
    const statusFilter = document.getElementById('status-filter');

    const debouncedLoad = debounce(() => loadUsers(), 300);

    if (searchInput) searchInput.addEventListener('input', debouncedLoad);
    if (roleFilter) roleFilter.addEventListener('change', () => loadUsers());
    if (statusFilter) statusFilter.addEventListener('change', () => loadUsers());
}

async function toggleUserStatus(userId, currentStatus) {
    try {
        const action = currentStatus ? 'deactivate' : 'activate';
        await apiFetch(`/admin/dashboard/users/${userId}/${action}`, { method: 'PUT' });
        loadUsers();
    } catch (error) {
        alert('Error al cambiar estado del usuario: ' + error.message);
    }
}

function getRoleBadgeClass(role) {
    switch (role) {
        case 'provider': return 'badge-purple';
        case 'admin': return 'badge-neutral';
        default: return 'badge-primary';
    }
}

function capitalize(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
