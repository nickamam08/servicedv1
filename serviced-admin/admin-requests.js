/**
 * Admin Requests Supervision Logic - Enhanced
 */

let allRequests = [];

document.addEventListener('DOMContentLoaded', () => {
    loadRequests();
    setupFilters();
});

async function loadRequests() {
    try {
        const idFilter = document.getElementById('id-filter')?.value || '';
        const status = document.getElementById('status-filter')?.value || 'all';
        const dateFrom = document.getElementById('date-from')?.value || '';
        const dateTo = document.getElementById('date-to')?.value || '';

        console.log('Loading requests with filters:', { idFilter, status, dateFrom, dateTo });

        let queryParams = [];
        if (status !== 'all') queryParams.push(`status=${status}`);
        if (dateFrom) queryParams.push(`date_from=${dateFrom}T00:00:00`);
        if (dateTo) queryParams.push(`date_to=${dateTo}T23:59:59`);

        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
        let requests = await apiFetch(`/admin/dashboard/requests${queryString}`);

        if (!requests) return;

        // Local ID filtering if provided (since backend ID search isn't explicit yet)
        if (idFilter) {
            const cleanId = idFilter.replace('#REQ-', '').trim();
            requests = requests.filter(r => r.id.toString().includes(cleanId));
        }

        allRequests = requests;
        displayRequests(allRequests);
        updateStats(allRequests);
    } catch (error) {
        console.error('Error loading requests:', error);
    }
}

function displayRequests(requests) {
    const tbody = document.getElementById('requests-table-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (requests.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 40px; color: var(--text-secondary);">No se encontraron solicitudes.</td></tr>';
        return;
    }

    requests.forEach(req => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid var(--border)';
        tr.innerHTML = `
            <td class="text-sm" style="padding: 16px 24px; font-weight: 600;">#REQ-${req.id}</td>
            <td style="padding: 16px 24px;">
                <div style="font-weight: 500;">${req.client_name || 'Desconocido'}</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">ID: #${req.client_id}</div>
            </td>
            <td style="padding: 16px 24px;">
                 <div style="font-weight: 500;">${req.provider_name || 'N/A'}</div>
            </td>
            <td style="padding: 16px 24px;">
                <div style="font-weight: 500; max-width: 200px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${req.service_title}">
                    ${req.service_title || 'Servicio eliminado'}
                </div>
            </td>
            <td style="padding: 16px 24px; color: var(--text-secondary); font-size: 0.85rem;">
                ${new Date(req.created_at).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })}
            </td>
            <td style="padding: 16px 24px;">
                <span class="badge ${getStatusBadgeClass(req.status)}">${capitalize(req.status)}</span>
            </td>
            <td style="padding: 16px 24px;">
                <button class="btn btn-outline" style="padding: 6px 12px; font-size: 0.8rem;" onclick="viewRequestDetails(${req.id})">
                    Ver Detalles
                </button>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

async function viewRequestDetails(id) {
    const req = allRequests.find(r => r.id === id);
    if (!req) return;

    const modal = document.getElementById('request-modal');
    const content = document.getElementById('modal-content');

    content.innerHTML = `
        <div style="padding: 40px;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px;">
                <div>
                    <h2 class="text-h2" style="margin-bottom: 4px;">Detalle de Solicitud #REQ-${req.id}</h2>
                    <p class="text-sm" style="color: var(--text-secondary);">Creada el ${new Date(req.created_at).toLocaleString()}</p>
                </div>
                <span class="badge ${getStatusBadgeClass(req.status)}" style="font-size: 1rem; padding: 8px 16px;">
                    ${capitalize(req.status)}
                </span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 32px;">
                <div style="padding: 16px; background: #f9fafb; border-radius: 12px; border: 1px solid var(--border);">
                    <h4 style="margin-bottom: 12px; font-size: 0.9rem; color: var(--text-secondary); text-transform: uppercase;">Información del Cliente</h4>
                    <p style="font-weight: 600;">${req.client_name || 'Desconocido'}</p>
                    <p class="text-sm">ID Usuario: #${req.client_id}</p>
                </div>
                <div style="padding: 16px; background: #f9fafb; border-radius: 12px; border: 1px solid var(--border);">
                    <h4 style="margin-bottom: 12px; font-size: 0.9rem; color: var(--text-secondary); text-transform: uppercase;">Información del Proveedor</h4>
                    <p style="font-weight: 600;">${req.provider_name || 'No asignado'}</p>
                    <p class="text-sm">ID Profesional: #${req.provider_id || 'N/A'}</p>
                </div>
            </div>

            <div style="margin-bottom: 32px; padding: 20px; border: 1px solid var(--border); border-radius: 12px;">
                <h4 style="margin-bottom: 16px; font-size: 1rem;">Servicio Contratado</h4>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <p style="font-weight: 700; font-size: 1.1rem;">${req.service_title || 'Servicio eliminado'}</p>
                        <p class="text-sm" style="color: var(--text-secondary);">ID Servicio: #${req.service_id}</p>
                    </div>
                </div>
            </div>

            <div style="display: flex; gap: 12px;">
                <button class="btn btn-outline" style="flex: 1;" onclick="closeModal()">Cerrar</button>
                ${req.status !== 'CANCELLED' && req.status !== 'COMPLETED' ? `
                    <button class="btn btn-danger" style="flex: 1;" onclick="cancelRequest(${req.id})">
                        Cancelar Solicitud (Admin)
                    </button>
                ` : ''}
            </div>
        </div>
    `;

    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('request-modal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('request-modal');
    if (event.target == modal) {
        closeModal();
    }
}

async function cancelRequest(id) {
    try {
        const confirmCancel = confirm('¿Estás seguro de que deseas cancelar forzosamente esta solicitud? Esta acción es irreversible.');
        if (!confirmCancel) return;

        await apiFetch(`/admin/dashboard/requests/${id}/cancel`, { method: 'PUT' });
        closeModal();
        loadRequests();
        alert('Solicitud cancelada correctamente.');
    } catch (error) {
        alert('Error al cancelar: ' + error.message);
    }
}

function updateStats(requests) {
    const totalCount = document.getElementById('stats-total');
    const completedCount = document.getElementById('stats-completed');
    const problemCount = document.getElementById('stats-problem');

    if (totalCount) totalCount.textContent = requests.length.toLocaleString();
    if (completedCount) completedCount.textContent = requests.filter(r => r.status === 'COMPLETED').length.toLocaleString();
    if (problemCount) problemCount.textContent = requests.filter(r => r.status === 'CANCELLED').length.toLocaleString();
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'COMPLETED': return 'badge-success';
        case 'CANCELLED': return 'badge-danger';
        case 'ACTIVE': return 'badge-primary';
        case 'PENDING': return 'badge-warning';
        default: return 'badge-neutral';
    }
}

function capitalize(s) {
    if (!s) return '';
    return s.charAt(0).toUpperCase() + s.slice(1).toLowerCase().replace('_', ' ');
}

function setupFilters() {
    const idFilter = document.getElementById('id-filter');
    const statusFilter = document.getElementById('status-filter');
    const dateFrom = document.getElementById('date-from');
    const dateTo = document.getElementById('date-to');

    if (idFilter) idFilter.addEventListener('input', debounce(() => loadRequests(), 300));
    if (statusFilter) statusFilter.addEventListener('change', () => loadRequests());
    if (dateFrom) dateFrom.addEventListener('change', () => loadRequests());
    if (dateTo) dateTo.addEventListener('change', () => loadRequests());
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
