/**
 * Admin Reports Moderation Logic
 */

let allReports = [];

document.addEventListener('DOMContentLoaded', () => {
    loadReports();
    setupFilters();
});

async function loadReports() {
    try {
        const priority = document.getElementById('priority-filter')?.value || 'all';
        const status = document.getElementById('status-filter')?.value || 'all';

        let queryParams = [];
        if (priority !== 'all') queryParams.push(`priority=${priority}`);
        if (status !== 'all') queryParams.push(`status=${status}`);

        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
        const reports = await apiFetch(`/admin/dashboard/reports${queryString}`);

        if (!reports) return;

        allReports = reports;
        displayReports(allReports);
        updateUrgentCount(allReports);
    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

function displayReports(reports) {
    const activeContainer = document.getElementById('active-reports-container');
    const resolvedTbody = document.getElementById('resolved-reports-tbody');

    if (activeContainer) activeContainer.innerHTML = '';
    if (resolvedTbody) resolvedTbody.innerHTML = '';

    const activeReports = reports.filter(r => r.status !== 'RESOLVED' && r.status !== 'DISMISSED');
    const historyReports = reports.filter(r => r.status === 'RESOLVED' || r.status === 'DISMISSED');

    // Display Active Reports as Cards
    if (activeReports.length === 0 && activeContainer) {
        activeContainer.innerHTML = '<div class="bento-card" style="grid-column: span 12; text-align: center; padding: 40px; color: var(--text-secondary);">No hay reportes pendientes.</div>';
    } else if (activeContainer) {
        activeReports.forEach(req => {
            const card = document.createElement('div');
            card.className = 'bento-card';
            card.style.gridColumn = 'span 12';
            card.style.borderLeft = `4px solid ${getPriorityColor(req.priority)}`;

            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                            <span class="badge ${getPriorityBadgeClass(req.priority)}">${req.priority}</span>
                            <span class="badge ${getStatusBadgeClass(req.status)}">${req.status}</span>
                            <span class="text-sm" style="color: var(--text-secondary);">${new Date(req.created_at).toLocaleString()}</span>
                        </div>
                        <h3 class="text-h3" style="margin-bottom: 4px;">${req.title} <span style="font-weight: 400; color: var(--text-secondary); font-size: 0.9rem;">#REP-${req.id}</span></h3>
                        <p class="text-body" style="margin-bottom: 8px;">
                            <strong>Denunciante:</strong> ${req.reporter_name} 
                            ${req.reported_user_name !== 'N/A' ? `| <strong>Acusado:</strong> ${req.reported_user_name}` : ''}
                            ${req.service_title !== 'N/A' ? `| <strong>Servicio:</strong> ${req.service_title}` : ''}
                        </p>
                        <p class="text-body" style="background: var(--bg-surface-alt); padding: 12px; border-radius: 8px; font-size: 0.9rem; margin-bottom: 16px; white-space: pre-wrap;">${req.description}</p>
                        
                        ${req.admin_notes ? `
                            <div style="margin-bottom: 16px; padding: 12px; border: 1px dashed var(--border); border-radius: 8px; font-size: 0.85rem;">
                                <strong>Notas Admin:</strong> ${req.admin_notes}
                            </div>
                        ` : ''}
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 8px; margin-left: 20px;">
                        <button class="btn btn-primary" onclick="openResolveModal(${req.id})">Gestionar</button>
                        <button class="btn btn-outline" onclick="contactReporter(${req.reporter_id})">Contactar</button>
                    </div>
                </div>
            `;
            activeContainer.appendChild(card);
        });
    }

    // Display History in Table
    if (historyReports.length === 0 && resolvedTbody) {
        resolvedTbody.innerHTML = '<tr><td colspan="5" style="text-align: center; padding: 20px; color: var(--text-secondary);">No hay historial.</td></tr>';
    } else if (resolvedTbody) {
        historyReports.forEach(req => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>#REP-${req.id}</td>
                <td>${req.type}</td>
                <td><span class="badge ${getStatusBadgeClass(req.status)}">${req.status}</span></td>
                <td title="${req.resolution || ''}">${req.resolution || 'N/A'}</td>
                <td>${new Date(req.created_at).toLocaleDateString()}</td>
            `;
            resolvedTbody.appendChild(tr);
        });
    }
}

function updateUrgentCount(reports) {
    const urgentCount = reports.filter(r => r.priority === 'URGENT' && r.status !== 'RESOLVED').length;
    const urgentBadge = document.getElementById('urgent-badge');
    if (urgentBadge) {
        urgentBadge.textContent = `${urgentCount} Casos Urgentes`;
        urgentBadge.style.display = urgentCount > 0 ? 'block' : 'none';
    }
}

function getPriorityColor(priority) {
    switch (priority) {
        case 'URGENT': return '#ef4444';
        case 'HIGH': return '#f97316';
        case 'MEDIUM': return '#eab308';
        default: return '#3b82f6';
    }
}

function getPriorityBadgeClass(priority) {
    switch (priority) {
        case 'URGENT': return 'badge-danger';
        case 'HIGH': return 'badge-warning';
        case 'MEDIUM': return 'badge-primary';
        default: return 'badge-neutral';
    }
}

function getStatusBadgeClass(status) {
    switch (status) {
        case 'RESOLVED': return 'badge-success';
        case 'PENDING': return 'badge-warning';
        case 'INVESTIGATING': return 'badge-primary';
        case 'DISMISSED': return 'badge-neutral';
        default: return 'badge-neutral';
    }
}

function setupFilters() {
    const priority = document.getElementById('priority-filter');
    const status = document.getElementById('status-filter');
    if (priority) priority.addEventListener('change', loadReports);
    if (status) status.addEventListener('change', loadReports);
}

// Modal logic
function openManageModal(id) {
    const req = allReports.find(r => r.id === parseInt(id));
    if (!req) return;

    document.getElementById('modal-report-id').textContent = `Gestionar Reporte #REP-${req.id}`;
    document.getElementById('modal-report-id-input').value = req.id;
    document.getElementById('modal-status').value = req.status;
    document.getElementById('modal-priority').value = req.priority;
    document.getElementById('modal-admin-notes').value = req.admin_notes || '';
    document.getElementById('modal-resolution').value = req.resolution || '';

    document.getElementById('manage-report-modal').style.display = 'flex';
}

function closeManageModal() {
    document.getElementById('manage-report-modal').style.display = 'none';
}

// Handle Form Submission
document.getElementById('manage-report-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const id = document.getElementById('modal-report-id-input').value;

    const payload = {
        status: document.getElementById('modal-status').value,
        priority: document.getElementById('modal-priority').value,
        admin_notes: document.getElementById('modal-admin-notes').value,
        resolution: document.getElementById('modal-resolution').value
    };

    try {
        await apiFetch(`/admin/dashboard/reports/${id}`, {
            method: 'PUT',
            body: JSON.stringify(payload)
        });

        closeManageModal();
        loadReports();
    } catch (error) {
        console.error('Error updating report:', error);
        alert('Error al actualizar el reporte');
    }
});

function contactReporter(id) {
    // In a real app, this would open a chat or email form
    alert(`Redirigiendo a chat con usuario ID #${id}... (Simulado)`);
}

// Ensure openResolveModal (old name) also works or is replaced in template
window.openResolveModal = openManageModal; // Backward compatibility with previous template render
window.closeManageModal = closeManageModal;
