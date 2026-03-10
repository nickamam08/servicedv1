/**
 * Lógica del Dashboard del Proveedor
 * Refactorizado para usar el sistema de Bento Grid y mensajería estilo chat de usuario.
 */

console.log("SERVICED Provider Dashboard v1.1.8 - Fix Email/Cache");
const API_BASE = '/api/v1/provider/dashboard';
const CHAT_API_BASE = '/api/v1/conversations';
const AUTH_TOKEN_KEY = 'serviced_token';
const USER_KEY = 'serviced_user';

// --- Inicialización ---
document.addEventListener('DOMContentLoaded', () => {
    // Control de Versión: Forzar refresco si la versión cambia para evitar problemas de caché
    const APP_VERSION = '1.1.9';
    const storedVersion = localStorage.getItem('serviced_app_version');
    if (storedVersion !== APP_VERSION) {
        localStorage.setItem('serviced_app_version', APP_VERSION);
        if (storedVersion) {
            console.log("Versión desactualizada detectada, limpiando estado...");
            // Limpiar claves específicas que puedan estar obsoletas
            localStorage.removeItem('some_hypothetical_stale_key');
            window.location.reload(true);
            return;
        }
    }

    // Validar sesión y configurar eventos globales
    checkAuth();
    setupNavigation();
    setupForms();
    setupLogout();

    // Enrutamiento Inicial: Cargar la vista solicitada por URL o 'overview' por defecto
    const urlParams = new URLSearchParams(window.location.search);
    const view = urlParams.get('view') || 'overview';
    loadView(view);
});

/**
 * Configura el botón de cierre de sesión de forma segura.
 */
function setupLogout() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        console.log("Logout button detected and listener attached.");
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            console.log("Logging out...");
            sessionStorage.clear(); // Limpiar todo por seguridad
            localStorage.removeItem('serviced_token'); // Por si acaso
            localStorage.removeItem('serviced_user');
            window.location.href = '/users/login.html';
        });
    } else {
        console.error("Logout button (#logout-btn) not found in DOM.");
    }
}

/**
 * Verifica si el usuario tiene un token válido y el rol de proveedor.
 */
function checkAuth() {
    const token = sessionStorage.getItem(AUTH_TOKEN_KEY);
    const userStr = sessionStorage.getItem(USER_KEY);

    if (!token || !userStr) {
        window.location.href = '/users/login.html';
        return;
    }

    try {
        const user = JSON.parse(userStr);
        if (user.role !== 'provider') {
            console.warn("Rol incorrecto para este dashboard, redireccionando...");
            if (user.role === 'client') window.location.href = "/users/client-dashboard.html";
            else window.location.href = "/users/login.html";
        }
    } catch (e) {
        window.location.href = '/users/login.html';
    }
}

/**
 * Helper para obtener las cabeceras de autorización necesarias para la API.
 */
function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${sessionStorage.getItem(AUTH_TOKEN_KEY)}`
    };
}

// --- Navegación y Enrutamiento ---

/**
 * Configura los clics en los elementos de la barra lateral para cambiar de vista.
 */
function setupNavigation() {
    document.querySelectorAll('.nav-item[data-target]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.target;
            loadView(view);
            // Actualizar URL sin recargar la página para soportar botones atrás/adelante
            const newUrl = new URL(window.location);
            newUrl.searchParams.set('view', view);
            window.history.pushState({}, '', newUrl);
        });
    });
}

// --- Estado del Chat (dentro del dashboard) ---
const chatState = {
    pollingInterval: null,
    currentConversationId: null,
    conversations: [],
    user: JSON.parse(sessionStorage.getItem(USER_KEY) || '{}'),
    isSending: false
};

/**
 * Carga principal de contenido dinámico basado en la sección seleccionada.
 * @param {string} viewName - Nombre de la vista a cargar (overview, services, requests, etc.)
 */
function loadView(viewName) {
    // Limpieza de estados anteriores: polleo de chats y filtros
    if (chatState.pollingInterval) clearInterval(chatState.pollingInterval);
    chatState.pollingInterval = null;
    chatState.currentConversationId = null;

    // Resaltar ítem activo en el menú lateral
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const activeNav = document.querySelector(`.nav-item[data-target="${viewName}"]`);
    if (activeNav) activeNav.classList.add('active');

    // Actualización de títulos dinámicos
    const titles = {
        overview: 'Vista General',
        services: 'Mis Servicios',
        requests: 'Solicitudes',
        calendar: 'Calendario',
        reviews: 'Reseñas',
        notifications: 'Notificaciones',
        profile: 'Perfil',
        messages: 'Mensajes',
        reports: 'Reportes',
        statistics: 'Estadísticas'
    };
    const pageTitle = document.getElementById('page-title');
    if (pageTitle) pageTitle.textContent = titles[viewName] || 'Dashboard';

    // Preparar el contenedor principal con un spinner de carga
    const contentArea = document.getElementById('content-area');
    if (!contentArea) return;
    contentArea.innerHTML = '<div class="spinner"></div>';

    // Despacho de renderizado según la vista
    switch (viewName) {
        case 'overview': renderOverview(); break;
        case 'services': renderServices(); break;
        case 'requests': renderRequests(); break;
        case 'calendar': renderCalendar(); break;
        case 'reviews': renderReviews(); break;
        case 'notifications': renderNotifications(); break;
        case 'profile': renderProfile(); break;
        case 'messages': initChatModule(); break; // El chat se inicializa como un módulo aparte
        case 'reports': renderReports(); break;
        case 'statistics': renderStatistics(); break;
        default: renderOverview();
    }
}

/**
 * Renderiza la sección de estadísticas con gráficos de distribución y métricas de rendimiento.
 */
async function renderStatistics() {
    try {
        const res = await fetch(`${API_BASE}/overview`, { headers: getHeaders() });
        if (!res.ok) throw new Error(`Error de API: ${res.status}`);
        const data = await res.json();

        // Cálculo de porcentajes de distribución para la visualización visual
        const totalReq = data.total_requests || 1;
        const pendingPct = Math.round((data.pending_requests / totalReq) * 100);
        const acceptedPct = Math.round((data.accepted_requests / totalReq) * 100);
        const completedPct = Math.round((data.completed_requests / totalReq) * 100);
        const cancelledPct = Math.round((data.cancelled_requests / totalReq) * 100);

        document.getElementById('content-area').innerHTML = `
            <div class="bento-grid">
                <!-- Tarjetas de Resumen de Estadísticas -->
                <div class="bento-card stat-card" style="grid-column: span 3;">
                    <span class="text-sm">Ganancias Totales</span>
                    <div class="text-h2" style="margin-top: 8px; color: var(--success);">$${data.balance.toLocaleString('es-CO')}</div>
                    <p class="text-xs" style="margin-top: 4px; color: var(--text-tertiary);">Estimado de servicios completados</p>
                </div>
                <div class="bento-card stat-card" style="grid-column: span 3;">
                    <span class="text-sm">Rating General</span>
                    <div class="text-h2" style="margin-top: 8px; color: var(--warning);">${data.average_rating.toFixed(1)} <span style="font-size:1rem;">★</span></div>
                    <p class="text-xs" style="margin-top: 4px; color: var(--text-tertiary);">Basado en ${data.total_reviews} reseñas</p>
                </div>
                <div class="bento-card stat-card" style="grid-column: span 3;">
                    <span class="text-sm">Servicios Activos</span>
                    <div class="text-h2" style="margin-top: 8px;">${data.active_services}</div>
                    <p class="text-xs" style="margin-top: 4px; color: var(--text-tertiary);">De ${data.total_services} servicios totales</p>
                </div>
                <div class="bento-card stat-card" style="grid-column: span 3;">
                    <span class="text-sm">Solicitudes Totales</span>
                    <div class="text-h2" style="margin-top: 8px;">${data.total_requests}</div>
                    <p class="text-xs" style="margin-top: 4px; color: var(--text-tertiary);">Desde el inicio</p>
                </div>

                <!-- Gráfico de Distribución (Visualización de barras simple) -->
                <div class="bento-card" style="grid-column: span 7; grid-row: span 2;">
                    <h3 class="text-h3" style="margin-bottom: 24px;">Distribución de Solicitudes</h3>
                    <div style="display: flex; flex-direction: column; gap: 20px;">
                        <div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span class="text-sm" style="color: var(--text-main); font-weight:500;">Completadas</span>
                                <span class="text-sm">${data.completed_requests} (${completedPct}%)</span>
                            </div>
                            <div style="width: 100%; height: 8px; background: var(--bg-surface-alt); border-radius: 4px; overflow: hidden;">
                                <div style="width: ${completedPct}%; height: 100%; background: var(--success);"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span class="text-sm" style="color: var(--text-main); font-weight:500;">Aceptadas / En Proceso</span>
                                <span class="text-sm">${data.accepted_requests} (${acceptedPct}%)</span>
                            </div>
                            <div style="width: 100%; height: 8px; background: var(--bg-surface-alt); border-radius: 4px; overflow: hidden;">
                                <div style="width: ${acceptedPct}%; height: 100%; background: var(--primary);"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span class="text-sm" style="color: var(--text-main); font-weight:500;">Pendientes</span>
                                <span class="text-sm">${data.pending_requests} (${pendingPct}%)</span>
                            </div>
                            <div style="width: 100%; height: 8px; background: var(--bg-surface-alt); border-radius: 4px; overflow: hidden;">
                                <div style="width: ${pendingPct}%; height: 100%; background: var(--warning);"></div>
                            </div>
                        </div>
                        <div>
                            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                                <span class="text-sm" style="color: var(--text-main); font-weight:500;">Canceladas</span>
                                <span class="text-sm">${data.cancelled_requests} (${cancelledPct}%)</span>
                            </div>
                            <div style="width: 100%; height: 8px; background: var(--bg-surface-alt); border-radius: 4px; overflow: hidden;">
                                <div style="width: ${cancelledPct}%; height: 100%; background: var(--danger);"></div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Análisis de Rendimiento (Insights) -->
                <div class="bento-card" style="grid-column: span 5; grid-row: span 2;">
                    <h3 class="text-h3" style="margin-bottom: 24px;">Rendimiento</h3>
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        <div style="padding: 16px; background: #F0FDF4; border-radius: 12px; border: 1px solid #DCFCE7;">
                            <div style="color: #166534; font-weight: 600; font-size: 0.9rem;">Tasa de Conversión</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #166534; margin: 4px 0;">${Math.round(((data.accepted_requests + data.completed_requests) / totalReq) * 100)}%</div>
                            <div style="font-size: 0.75rem; color: #15803D;">Solicitudes aceptadas/finalizadas vs recibidas</div>
                        </div>
                        <div style="padding: 16px; background: #EFF6FF; border-radius: 12px; border: 1px solid #DBEAFE;">
                            <div style="color: #1E40AF; font-weight: 600; font-size: 0.9rem;">Eficiencia de Cierre</div>
                            <div style="font-size: 1.5rem; font-weight: 700; color: #1E40AF; margin: 4px 0;">${(data.completed_requests + data.accepted_requests) > 0 ? Math.round((data.completed_requests / (data.completed_requests + data.accepted_requests)) * 100) : 0}%</div>
                            <div style="font-size: 0.75rem; color: #1D4ED8;">Trabajos completados vs total aceptados</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    } catch (e) {
        console.error("Statistics Error:", e);
        document.getElementById('content-area').innerHTML = `<div class="bento-card" style="color:red;">Error cargando estadísticas: ${e.message}</div>`;
    }
}

/**
 * Renderiza la sección de reportes enviados por el proveedor y el formulario para nuevos reportes.
 */
async function renderReports() {
    try {
        // Obtener historial de reportes propios del proveedor
        const res = await fetch('/api/v1/reports/my-reports', { headers: getHeaders() });
        const reports = await res.json();

        // Generar HTML dinámico para cada reporte
        let reportsHtml = reports.map(r => `
            <div class="bento-card" style="grid-column: span 6; border-left: 4px solid ${r.status === 'RESOLVED' ? '#10B981' : '#F59E0B'};">
                <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                    <div>
                        <h4 style="font-weight:600; margin-bottom:4px;">${r.title}</h4>
                        <p class="text-sm" style="color:var(--text-secondary);">${new Date(r.created_at).toLocaleDateString()} - ${r.type}</p>
                        <p class="text-body" style="margin-top:12px; font-size:0.9rem;">${r.description}</p>
                    </div>
                    <span class="badge ${r.status === 'RESOLVED' ? 'badge-active' : 'badge-inactive'}">${r.status}</span>
                </div>
                <!-- Mostrar resolución si el reporte ya fue procesado por un administrador -->
                ${r.resolution ? `<div style="margin-top:16px; padding:12px; background:#f9fafb; border-radius:8px; font-size:0.85rem;"><strong>Resolución:</strong> ${r.resolution}</div>` : ''}
            </div>
        `).join('');

        if (reports.length === 0) {
            reportsHtml = '<div class="bento-card" style="grid-column: span 12; text-align:center; padding:40px;">No has enviado ningún reporte.</div>';
        }

        document.getElementById('content-area').innerHTML = `
            <div class="bento-grid">
                <!-- Formulario de creación de nuevos reportes -->
                <div class="bento-card" style="grid-column: span 12; margin-bottom: 24px;">
                    <h3 class="text-h3" style="margin-bottom: 16px;">Enviar Nuevo Reporte</h3>
                    <form id="new-report-form" style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                        <div class="form-group" style="grid-column: span 2;">
                            <label class="form-label">Asunto</label>
                            <input type="text" class="form-control" id="rep-title" required placeholder="Ej: Problema con el pago del servicio #123">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Categoría</label>
                            <select class="form-control" id="rep-type" required>
                                <option value="behavior">Comportamiento de cliente</option>
                                <option value="payment">Problemas de Pago</option>
                                <option value="technical">Error técnico / App</option>
                                <option value="other">Otro motivo</option>
                            </select>
                        </div>
                        <div class="form-group" style="grid-column: span 2;">
                            <label class="form-label">Descripción Detallada</label>
                            <textarea class="form-control" id="rep-desc" rows="3" required placeholder="Describe lo sucedido con el mayor detalle posible..."></textarea>
                        </div>
                        <div style="grid-column: span 2; text-align:right;">
                            <button type="submit" class="btn btn-primary">Enviar Reporte a Soporte</button>
                        </div>
                    </form>
                </div>
                ${reportsHtml}
            </div>
        `;

        // Lógica de envío del formulario
        document.getElementById('new-report-form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const body = {
                title: document.getElementById('rep-title').value,
                type: document.getElementById('rep-type').value,
                description: document.getElementById('rep-desc').value
            };
            try {
                const postRes = await fetch('/api/v1/reports', {
                    method: 'POST',
                    headers: getHeaders(),
                    body: JSON.stringify(body)
                });
                if (postRes.ok) {
                    showToast('Reporte enviado correctamente. El equipo de soporte lo revisará pronto.');
                    renderReports(); // Recargar la lista
                } else {
                    alert('Error al enviar el reporte. Inténtalo de nuevo.');
                }
            } catch (err) { alert('Error de red. Verifica tu conexión.'); }
        });

    } catch (e) {
        document.getElementById('content-area').innerHTML = `<div class="bento-card">Error cargando sección de reportes</div>`;
    }
}

// --- Renderizadores de Vista (Estilo Bento) ---

/**
 * Renderiza la Vista General (Overview) con estadísticas rápidas y próximos trabajos.
 */
async function renderOverview() {
    try {
        const res = await fetch(`${API_BASE}/overview`, { headers: getHeaders() });

        // Caso: El usuario no tiene rol de proveedor o el token expiró
        if (res.status === 403) {
            let errDetail = 'Acceso Denegado';
            try { const errData = await res.json(); errDetail = errData.detail || 'Sin detalles'; } catch (e) { }
            document.getElementById('content-area').innerHTML = `
                <div class="bento-card" style="grid-column: span 12; text-align: center; padding: 48px;">
                    <div style="font-size: 3rem; margin-bottom: 16px;">🚫</div>
                    <h3 class="text-h2">Acceso Denegado</h3>
                    <p class="text-body" style="margin-top: 16px; margin-bottom: 24px;">Tu cuenta actual no tiene permisos de Proveedor.</p>
                    <div style="font-family:monospace; background:#f3f4f6; padding:8px; border-radius:4px; margin-bottom:16px;">Error: ${errDetail}</div>
                    <button class="btn btn-primary" onclick="sessionStorage.removeItem('${AUTH_TOKEN_KEY}'); sessionStorage.removeItem('${USER_KEY}'); window.location.href = '/users/login.html';">Cerrar Sesión</button>
                </div>`;
            return;
        }

        if (!res.ok) throw new Error(`API Error: ${res.status}`);
        const data = await res.json();
        const upcoming_jobs = Array.isArray(data.upcoming_jobs) ? data.upcoming_jobs : [];
        const stats = { total_services: data.total_services || 0, pending_requests: data.pending_requests || 0, average_rating: data.average_rating || 0, balance: data.balance || 0 };

        document.getElementById('content-area').innerHTML = `
            <div class="bento-grid">
                <!-- Estadísticas de Resumen -->
                <div class="bento-card stat-card"><span class="text-sm">Total Servicios</span><div class="text-h2" style="margin-top: 8px;">${stats.total_services}</div></div>
                <div class="bento-card stat-card"><span class="text-sm">Solicitudes Pendientes</span><div class="text-h2" style="margin-top: 8px; color: var(--warning);">${stats.pending_requests}</div></div>
                <div class="bento-card stat-card"><span class="text-sm">Rating General</span><div class="text-h2" style="margin-top: 8px;">${stats.average_rating.toFixed(1)} <span style="font-size:1rem; color:var(--warning);">★</span></div></div>
                <div class="bento-card stat-card"><span class="text-sm">Balance Estimado</span><div class="text-h2" style="margin-top: 8px; color: var(--success);">$${stats.balance.toLocaleString('es-CO')}</div></div>
                
                <!-- Lista de Próximos Trabajos Agendados -->
                <div class="bento-card" style="grid-column: span 8; grid-row: span 2;">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 16px;"><h3 class="text-h3">Próximos Trabajos</h3><button class="btn btn-secondary" style="padding: 4px 12px; font-size: 0.8rem;" onclick="loadView('requests')">Ver todos</button></div>
                    <div class="table-container"><table><thead><tr><th>Cliente</th><th>Servicio</th><th>Fecha</th><th>Estado</th></tr></thead>
                            <tbody>${upcoming_jobs.length > 0 ? upcoming_jobs.map(job => `
                                    <tr><td style="font-weight:500;">${job.client_name}</td><td>${job.service_title}</td><td>${new Date(job.scheduled_date).toLocaleDateString()} ${new Date(job.scheduled_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td><td><span class="badge badge-accepted">${job.status}</span></td></tr>
                                `).join('') : '<tr><td colspan="4" style="text-align:center;">No hay trabajos próximos.</td></tr>'}
                            </tbody></table></div></div>
                
                <!-- Acciones Rápidas -->
                <div class="bento-card" style="grid-column: span 4; grid-row: span 2;"><h3 class="text-h3" style="margin-bottom: 16px;">Acciones Rápidas</h3><div style="display: flex; flex-direction: column; gap: 12px;"><button class="btn btn-primary" style="width: 100%;" onclick="openCreateServiceModal()">+ Crear Nuevo Servicio</button><button class="btn btn-secondary" style="width: 100%;" onclick="loadView('profile')">Editar Perfil</button></div></div>
            </div>`;
    } catch (e) {
        console.error("Render Overview Error:", e);
        document.getElementById('content-area').innerHTML = `<div class="bento-card" style="color:red;">Error cargando dashboard: ${e.message}</div>`;
    }
}

/**
 * Renderiza la sección de administración de servicios del proveedor.
 */
async function renderServices() {
    try {
        const res = await fetch(`${API_BASE}/services`, { headers: getHeaders() });
        if (!res.ok) throw new Error(`API Error: ${res.status}`);
        const services = await res.json();
        const safeServices = Array.isArray(services) ? services : [];
        window._services = safeServices; // Cache temporal para edición

        document.getElementById('content-area').innerHTML = `
            <div class="bento-card" style="width: 100%;">
                 <div style="display:flex; justify-content:space-between; margin-bottom: 24px;"><h3 class="text-h3">Mis Servicios (${safeServices.length})</h3><button class="btn btn-primary" onclick="openCreateServiceModal()">Nuevo Servicio</button></div>
                <div class="table-container"><table><thead><tr><th>Servicio</th><th>Precio</th><th>Categoría</th><th>Estado</th><th>Acciones</th></tr></thead>
                        <tbody>${safeServices.length > 0 ? safeServices.map(s => `
                                <tr><td>
                                    <div style="display:flex; align-items:center; gap:12px;">
                                        ${s.image_urls && s.image_urls[0] ? `<img src="${s.image_urls[0]}" style="width:40px; height:40px; border-radius:4px; object-fit:cover; border:1px solid #eee;">` : `<div style="width:40px; height:40px; border-radius:4px; background:#f3f4f6; display:flex; align-items:center; justify-content:center; color:#9ca3af;"><i class="fas fa-image"></i></div>`}
                                        <div>
                                            <div style="font-weight:600;">${s.title}</div>
                                            <div class="text-sm">${s.duration || (s.duration_minutes ? s.duration_minutes + ' m' : '-')}</div>
                                        </div>
                                    </div>
                                </td><td>$${(s.price || 0).toLocaleString('es-CO')}</td><td>${s.category || '-'}</td><td><span class="badge ${s.is_active ? 'badge-active' : 'badge-inactive'}">${s.is_active ? 'Activo' : 'Inactivo'}</span></td><td>
                                        <button class="btn btn-secondary" style="padding:6px;" title="Editar" onclick="editService(${s.id})"><i class="fas fa-edit"></i></button> <button class="btn btn-secondary" style="padding:6px;" title="Activar/Desactivar" onclick="toggleService(${s.id})"><i class="fas fa-power-off"></i></button> <button class="btn btn-danger" style="padding:6px;" title="Eliminar" onclick="deleteService(${s.id})"><i class="fas fa-trash"></i></button></td></tr>
                            `).join('') : '<tr><td colspan="5" style="text-align:center;">No tienes servicios creados.</td></tr>'}
                        </tbody></table></div></div>`;
    } catch (e) { document.getElementById('content-area').innerHTML = `<div class="bento-card" style="color:red;">Error: ${e.message}</div>`; }
}

/**
 * Renderiza la sección de solicitudes de clientes (pedidos).
 */
async function renderRequests() {
    try {
        const res = await fetch(`${API_BASE}/requests`, { headers: getHeaders() });
        if (!res.ok) throw new Error(`API Error: ${res.status}`);
        const requests = await res.json();
        const safeRequests = Array.isArray(requests) ? requests : [];
        document.getElementById('content-area').innerHTML = `
            <div class="bento-card" style="width: 100%;"><h3 class="text-h3" style="margin-bottom: 24px;">Solicitudes de Clientes</h3><div class="table-container"><table><thead><tr><th>Cliente</th><th>Solicitud</th><th>Fecha Propuesta</th><th>Estado</th><th>Acciones</th></tr></thead>
                        <tbody>${safeRequests.length > 0 ? safeRequests.map(r => `
                                <tr><td>${r.client_name}</td><td><div style="font-weight:600;">${r.service_title}</div><div class="text-sm">$${(r.price || 0).toLocaleString('es-CO')}</div></td><td>${new Date(r.scheduled_date).toLocaleString()}</td><td><span class="badge badge-${r.status.toLowerCase()}">${r.status}</span></td><td>${renderRequestActions(r)}</td></tr>
                             `).join('') : '<tr><td colspan="5" style="text-align:center;">No tienes solicitudes pendientes.</td></tr>'}
                        </tbody></table></div></div>`;
    } catch (e) { document.getElementById('content-area').innerHTML = `<div class="bento-card" style="color:red;">Error: ${e.message}</div>`; }
}


// --- Acciones de Solicitud ---

/**
 * Renderiza los botones de acción para una solicitud específica según su estado actual.
 * @param {Object} req - Objeto de la solicitud.
 */
function renderRequestActions(req) {
    let buttons = '';

    // Botón de Chat: Siempre visible si existe un cliente asociado para permitir comunicación inmediata.
    if (req.client_id) {
        buttons += `<button class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.8rem; margin-right: 4px;" onclick="openChatWithClient(${req.client_id}, '${escapeHtml(req.client_name)}')"><i class="fas fa-comment"></i> Chatear</button> `;
    }

    // Acciones según el estado del flujo de trabajo (Workflow)
    if (req.status === 'PENDING') {
        buttons += `<button class="btn btn-primary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="updateRequestStatus(${req.id}, 'accept')">Aceptar</button> <button class="btn btn-danger" style="padding: 6px 12px; font-size: 0.8rem;" onclick="updateRequestStatus(${req.id}, 'reject')">Rechazar</button>`;
    } else if (req.status === 'ACCEPTED' || req.status === 'ACTIVE') {
        buttons += `<button class="btn btn-primary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="updateRequestStatus(${req.id}, 'complete')">Completar</button> <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="openRescheduleModal(${req.id})">Reprogramar</button>`;
    }
    return buttons;
}

/**
 * Inicia o recupera una conversación con un cliente y redirige a la vista de mensajes.
 * @param {number} clientId - ID del cliente.
 * @param {string} clientName - Nombre del cliente para mostrar.
 */
async function openChatWithClient(clientId, clientName) {
    try {
        // Crear o recuperar la conversación existente desde el backend
        const res = await fetch(`${CHAT_API_BASE}`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({ client_id: clientId })
        });

        if (!res.ok) throw new Error('No se pudo iniciar el chat');

        const conversation = await res.json();

        // Almacenar el ID de la conversación para abrirla automáticamente al cargar la vista de mensajes
        chatState.pendingConversationId = conversation.id;

        // Cambiar dinámicamente a la vista de mensajes
        loadView('messages');

    } catch (e) {
        alert('Error al abrir chat: ' + e.message);
        console.error(e);
    }
}

// ... existing renderCalendar, renderReviews, renderNotifications, renderProfile ...

// ... (existing code for renderCalendar, renderReviews, renderNotifications) ...

/**
 * Renderiza el Calendario de trabajos próximos y en curso.
 */
async function renderCalendar() {
    try {
        // Obtener todas las solicitudes para filtrar las agendadas
        const res = await fetch(`${API_BASE}/requests`, { headers: getHeaders() });
        const allRequests = await res.json();

        // Filtrar solo las aceptadas o activas para mostrar en el calendario
        const requests = allRequests.filter(r => r.status === 'ACCEPTED' || r.status === 'ACTIVE');

        // Ordenar cronológicamente
        requests.sort((a, b) => new Date(a.scheduled_date) - new Date(b.scheduled_date));

        document.getElementById('content-area').innerHTML = `
            <div class="bento-grid">
                ${requests.map(r => `
                    <div class="bento-card" style="grid-column: span 4; border-left: 4px solid var(--primary);">
                        <div style="display:flex; gap: 16px; align-items:center;">
                            <!-- Indicador de Fecha Visual -->
                            <div style="background:#EFF6FF; padding: 12px; border-radius:8px; text-align:center; min-width: 60px;">
                                <div style="font-weight:700; font-size:1.2rem; color:var(--primary);">${new Date(r.scheduled_date).getDate()}</div>
                                <div style="font-size:0.8rem; text-transform:uppercase; color:var(--primary);">${new Date(r.scheduled_date).toLocaleString('default', { month: 'short' })}</div>
                            </div>
                            <div>
                                <div style="font-weight:600;">${r.service_title}</div>
                                <div class="text-sm">Cliente: ${r.client_name}</div>
                                <div class="text-sm" style="color:var(--text-main); margin-top:4px;">
                                    <i class="fas fa-clock"></i> ${new Date(r.scheduled_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </div>
                                <div class="text-xs" style="margin-top:4px;">
                                    <span class="badge badge-${r.status.toLowerCase()}">${r.status === 'ACTIVE' ? 'En Progreso' : 'Agendado'}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                `).join('')}
                ${requests.length === 0 ? '<div class="bento-card" style="grid-column: span 12; text-align: center; padding: 40px;">No hay citas programadas o en curso.</div>' : ''}
            </div>`;
    } catch (e) {
        console.error("Calendar Error:", e);
        document.getElementById('content-area').innerHTML = `<div class="bento-card" style="color:red;">Error cargando calendario: ${e.message}</div>`;
    }
}

/**
 * Renderiza la sección de Reseñas y calificaciones recibidas.
 */
async function renderReviews() {
    try {
        const res = await fetch(`${API_BASE}/reviews`, { headers: getHeaders() });
        const reviews = await res.json();
        document.getElementById('content-area').innerHTML = `<div class="bento-grid">${reviews.map(r => `
                    <div class="bento-card" style="grid-column: span 4;"><div style="display:flex; justify-content:space-between; margin-bottom: 12px;"><div style="font-weight:600;">${r.client_name || 'Cliente'}</div><div style="color:var(--warning);">${'★'.repeat(r.rating)}</div></div><p class="text-body" style="font-style:italic;">"${r.comment}"</p><div class="text-sm" style="margin-top: 12px;">${new Date(r.created_at).toLocaleDateString()}</div></div>
                 `).join('')}${reviews.length === 0 ? '<div class="bento-card" style="grid-column: span 12;">No hay reseñas aún.</div>' : ''}</div>`;
    } catch (e) { }
}

/**
 * Renderiza el centro de Notificaciones del proveedor.
 */
async function renderNotifications() {
    try {
        const res = await fetch(`${API_BASE}/notifications`, { headers: getHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => ({}));
            throw new Error(errData.detail || `Error del servidor: ${res.status}`);
        }

        const notifs = await res.json();
        const safeNotifs = Array.isArray(notifs) ? notifs : [];
        const contentArea = document.getElementById('content-area');

        let html = `
            <div class="bento-card" style="grid-column: span 10; margin: 0 auto; max-width: 900px; width: 100%;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 24px;">
                    <h3 class="text-h3">Centro de Notificaciones</h3>
                    <span class="badge badge-active">${safeNotifs.filter(n => !n.is_read).length} nuevas</span>
                </div>
                <div style="display:flex; flex-direction:column; gap: 12px;">
        `;

        if (safeNotifs.length === 0) {
            html += `
                <div style="padding: 60px 20px; text-align: center; background: #f8fafc; border-radius: 16px; border: 2px dashed #e2e8f0;">
                    <div style="font-size: 3rem; margin-bottom: 16px;">🔔</div>
                    <div style="color: var(--text-main); font-weight: 600; font-size: 1.1rem; margin-bottom: 8px;">No hay notificaciones</div>
                    <p style="color: var(--text-tertiary);">Te avisaremos cuando recibas nuevas solicitudes o mensajes.</p>
                </div>
            `;
        } else {
            html += safeNotifs.map(n => `
                <div style="padding: 20px; border-radius: 12px; border: 1px solid ${n.is_read ? '#E5E7EB' : '#DBEAFE'}; background: ${n.is_read ? 'white' : '#F0F7FF'}; transition: all 0.2s;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 8px;">
                        <div style="font-weight:700; color: var(--text-main); font-size: 1rem;">${n.title}</div>
                        <div class="text-sm" style="white-space:nowrap;">${new Date(n.created_at).toLocaleString('es-CO', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}</div>
                    </div>
                    <div class="text-body" style="font-size: 0.95rem; color: var(--text-secondary); line-height: 1.5;">${n.message}</div>
                    ${!n.is_read ? '<div style="margin-top:12px;"><span style="font-size: 0.7rem; font-weight:800; text-transform:uppercase; color: var(--primary);">• Nueva</span></div>' : ''}
                </div>
            `).join('');
        }

        html += `</div></div>`;
        contentArea.innerHTML = html;

    } catch (e) {
        console.error("Notifications Error:", e);
        document.getElementById('content-area').innerHTML = `
            <div class="bento-card" style="grid-column: span 10; margin: 0 auto; max-width: 900px; padding: 40px; text-align: center;">
                <div style="color:var(--danger); font-size: 3rem; margin-bottom: 16px;">⚠️</div>
                <h3 class="text-h3" style="color:var(--danger); margin-bottom: 8px;">Error al cargar</h3>
                <p style="color:var(--text-secondary);">${e.message}</p>
                <button class="btn btn-primary" style="margin-top: 20px;" onclick="renderNotifications()">Reintentar</button>
            </div>
        `;
    }
}

/**
 * Renderiza el formulario de Perfil Profesional, incluyendo mapa interactivo y configuración de cuenta.
 */
async function renderProfile() {
    try {
        const res = await fetch(`${API_BASE}/profile`, { headers: getHeaders() });
        if (!res.ok) throw new Error("Error al cargar perfil");
        const profile = await res.json();

        // Coordenadas por defecto (Bogotá) si no existen en el perfil
        const defaultLat = profile.latitude || 4.6097;
        const defaultLng = profile.longitude || -74.0817;

        document.getElementById('content-area').innerHTML = `
            <div class="bento-grid">
                <!-- Columna Izquierda: Información Profesional y Biografía -->
                <div class="bento-card" style="grid-column: span 8; grid-row: span 2;">
                    <h3 class="text-h3" style="margin-bottom: 24px;">Perfil Profesional Premium</h3>
                    <form id="profile-form">
                        <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                            <div class="form-group">
                                <label class="form-label">Especialidad Principal</label>
                                <input type="text" class="form-control" id="profile-specialty" value="${profile.specialty || ''}" placeholder="Ej: Plomero Experto...">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Idiomas</label>
                                <input type="text" class="form-control" id="profile-languages" value="${profile.languages || ''}" placeholder="Ej: Español, Inglés...">
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Sobre mí (Resumen Profesional)</label>
                            <textarea class="form-control" id="profile-description" rows="5" placeholder="Cuéntales a tus clientes sobre tu trayectoria...">${profile.description || ''}</textarea>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Certificaciones (Separadas por comas)</label>
                            <input type="text" class="form-control" id="profile-certifications" value="${(profile.certifications || []).join(', ')}" placeholder="Ej: Certificación SENA, ISO 9001...">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Habilidades Especializadas</label>
                            <input type="text" class="form-control" id="profile-skills" value="${profile.skills || ''}" placeholder="Ej: Soldadura, Pintura epóxica...">
                        </div>
                        <div style="text-align:right; margin-top:24px;">
                            <button type="submit" class="btn btn-primary">Guardar Cambios Profesionales</button>
                        </div>
                    </form>
                </div>

                <!-- Columna Derecha: Mapa y Ubicación -->
                <div class="bento-card" style="grid-column: span 4;">
                    <h3 class="text-h3" style="margin-bottom: 12px;">Ubicación Geográfica</h3>
                    <div class="text-sm" style="margin-bottom: 8px;">Mueve el marcador para precisar tu zona de servicio en Colombia.</div>
                    <div id="profile-map" style="height: 350px; width: 100%; border-radius: 12px; border: 1px solid #E5E7EB; margin-top: 12px; position: relative;"></div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; margin-top:12px;">
                        <input type="hidden" id="profile-lat" value="${defaultLat}">
                        <input type="hidden" id="profile-lng" value="${defaultLng}">
                        <div class="form-group" style="margin-bottom:0;">
                            <label class="form-label">Latitud</label>
                            <div class="text-sm" id="display-lat" style="padding:8px; background:var(--bg-surface-alt); border-radius:4px;">${defaultLat.toFixed(4)}</div>
                        </div>
                        <div class="form-group" style="margin-bottom:0;">
                            <label class="form-label">Longitud</label>
                            <div class="text-sm" id="display-lng" style="padding:8px; background:var(--bg-surface-alt); border-radius:4px;">${defaultLng.toFixed(4)}</div>
                        </div>
                    </div>
                </div>

                <!-- Columna Derecha: Cuenta y Seguridad -->
                <div class="bento-card" style="grid-column: span 4;">
                    <h3 class="text-h3" style="margin-bottom: 20px;">Cuenta y Seguridad</h3>
                    <div class="form-group">
                        <label class="form-label">Nombre Completo</label>
                        <input type="text" class="form-control" id="profile-name" value="${profile.full_name || ''}">
                    </div>
                    <div class="form-group">
                        <label class="form-label">Correo Electrónico</label>
                        <input type="email" class="form-control" id="profile-email" value="${profile.email || ''}">
                    </div>
                    <div style="margin-top:20px; padding:16px; background:#FEF2F2; border-radius:12px; border:1px solid #FEE2E2;">
                        <h4 style="font-size:0.9rem; color:#991B1B; margin-bottom:12px;">Cambiar Contraseña</h4>
                        <div class="form-group">
                            <input type="password" class="form-control" id="profile-password" placeholder="Nueva contraseña">
                        </div>
                        <div class="form-group" style="margin-bottom:0;">
                            <input type="password" class="form-control" id="profile-password-confirm" placeholder="Confirmar contraseña">
                        </div>
                    </div>
                </div>

                <!-- Columna Derecha: Métricas de Negocio -->
                <div class="bento-card" style="grid-column: span 4;">
                    <h3 class="text-h3" style="margin-bottom: 20px;">Información de Negocio</h3>
                    <div class="form-group">
                        <label class="form-label">Ubicación (Texto)</label>
                        <input type="text" class="form-control" id="profile-location" value="${profile.location || ''}" placeholder="Ciudad, Barrio...">
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                        <div class="form-group">
                            <label class="form-label">Años Exp.</label>
                            <input type="number" class="form-control" id="profile-experience" value="${profile.experience_years || 0}">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Tarifa ($)</label>
                            <input type="number" class="form-control" id="profile-base-rate" value="${profile.base_rate || 0}" step="1">
                        </div>
                    </div>
                    <div style="margin-top:12px; padding:12px; background:var(--bg-surface-alt); border-radius:8px;">
                        <div style="font-size:0.75rem; color:var(--text-secondary); margin-bottom:4px;">Disponibilidad</div>
                        <input type="text" class="form-control" id="profile-availability" value="${profile.availability || ''}" placeholder="Ej: L-V 8am-5pm">
                    </div>
                </div>
            </div>
        `;

        // Inicialización diferida del Mapa (Leaflet.js)
        setTimeout(() => {
            try {
                const mapContainer = document.getElementById('profile-map');
                if (!mapContainer) return;

                if (typeof L === 'undefined') {
                    mapContainer.innerHTML = '<div style="padding:40px; text-align:center; color:var(--danger);">Error: Leaflet.js no cargado. Revisa tu conexión.</div>';
                    return;
                }

                const map = L.map('profile-map').setView([defaultLat, defaultLng], 13);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap'
                }).addTo(map);

                const marker = L.marker([defaultLat, defaultLng], { draggable: true }).addTo(map);

                // Evento al arrastrar el marcador para actualizar coordenadas
                marker.on('dragend', function (e) {
                    const pos = marker.getLatLng();
                    // Restricción a Colombia (bordes aproximados)
                    if (pos.lat < -4.2 || pos.lat > 13.5 || pos.lng < -82 || pos.lng > -66) {
                        alert("Por favor selecciona una ubicación dentro de Colombia");
                        marker.setLatLng([defaultLat, defaultLng]);
                        return;
                    }
                    document.getElementById('profile-lat').value = pos.lat;
                    document.getElementById('profile-lng').value = pos.lng;
                    document.getElementById('display-lat').textContent = pos.lat.toFixed(4);
                    document.getElementById('display-lng').textContent = pos.lng.toFixed(4);
                });

                // Forzar recalculado del tamaño del mapa tras renderizado
                setTimeout(() => map.invalidateSize(), 200);

            } catch (err) {
                console.error("Leaflet Init Error:", err);
                const mapContainer = document.getElementById('profile-map');
                if (mapContainer) mapContainer.innerHTML = `<div style="padding:20px;">Error al iniciar mapa: ${err.message}</div>`;
            }
        }, 150);

        document.getElementById('profile-form').addEventListener('submit', (e) => {
            e.preventDefault();
            handleProfileSubmit();
        });
    } catch (e) {
        document.getElementById('content-area').innerHTML = `<div class="bento-card" style="color:red;">Error: ${e.message}</div>`;
    }
}

/**
 * Procesa el envío del formulario de perfil y actualización de cuenta.
 */
async function handleProfileSubmit() {
    const certsRaw = document.getElementById('profile-certifications')?.value || '';
    const certsArray = certsRaw.split(',').map(s => s.trim()).filter(s => s !== '');

    // Validación de contraseñas si el usuario desea cambiarla
    const password = document.getElementById('profile-password')?.value;
    const confirm = document.getElementById('profile-password-confirm')?.value;

    if (password && password !== confirm) {
        alert('Las contraseñas no coinciden');
        return;
    }

    const body = {
        full_name: document.getElementById('profile-name')?.value,
        email: document.getElementById('profile-email')?.value,
        new_password: password || undefined,
        description: document.getElementById('profile-description')?.value,
        specialty: document.getElementById('profile-specialty')?.value,
        skills: document.getElementById('profile-skills')?.value,
        base_rate: document.getElementById('profile-base-rate') ? parseFloat(document.getElementById('profile-base-rate').value) : undefined,
        experience_years: document.getElementById('profile-experience') ? parseInt(document.getElementById('profile-experience').value) : undefined,
        location: document.getElementById('profile-location')?.value,
        availability: document.getElementById('profile-availability')?.value,
        latitude: parseFloat(document.getElementById('profile-lat').value),
        longitude: parseFloat(document.getElementById('profile-lng').value),
        languages: document.getElementById('profile-languages')?.value,
        certifications: certsArray
    };

    try {
        const res = await fetch(`${API_BASE}/profile`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(body)
        });

        if (res.ok) {
            showToast('Perfil y cuenta actualizados correctamente');
            // Actualizar datos de sesión local si cambiaron
            const user = JSON.parse(sessionStorage.getItem(USER_KEY) || '{}');
            user.full_name = body.full_name;
            user.email = body.email;
            sessionStorage.setItem(USER_KEY, JSON.stringify(user));

            await renderProfile(); // Recargar vista
        } else {
            const err = await res.json();
            alert('Error al actualizar: ' + (err.detail || 'Error desconocido'));
        }
    } catch (e) {
        alert('Error de red al actualizar perfil');
    }
}
function openCreateServiceModal() {
    document.getElementById('service-form').reset();
    document.getElementById('service-id').value = '';
    document.getElementById('service-image-preview').style.display = 'none';
    document.getElementById('service-modal').classList.add('open');
}
function closeServiceModal() { document.getElementById('service-modal').classList.remove('open'); }
function editService(id) {
    const service = window._services.find(s => s.id === id);
    if (!service) return;
    document.getElementById('service-id').value = id;
    document.getElementById('service-title').value = service.title;
    document.getElementById('service-description').value = service.description;
    document.getElementById('service-price').value = service.price;
    document.getElementById('service-category').value = service.category;

    const preview = document.getElementById('service-image-preview');
    if (service.image_urls && service.image_urls.length > 0) {
        preview.querySelector('img').src = service.image_urls[0];
        preview.style.display = 'block';
    } else {
        preview.style.display = 'none';
    }

    document.getElementById('service-modal').classList.add('open');
}
// Helpers de gestión de servicios y solicitudes
async function toggleService(id) { await fetch(`${API_BASE}/services/${id}/toggle`, { method: 'PUT', headers: getHeaders() }); renderServices(); }
async function deleteService(id) { if (confirm('¿Eliminar servicio permanentemente?')) { await fetch(`${API_BASE}/services/${id}`, { method: 'DELETE', headers: getHeaders() }); renderServices(); } }
async function updateRequestStatus(id, action) { await fetch(`${API_BASE}/requests/${id}/${action}`, { method: 'PUT', headers: getHeaders() }); renderRequests(); }
function openRescheduleModal(id) { document.getElementById('reschedule-request-id').value = id; document.getElementById('reschedule-modal').classList.add('open'); }
function closeRescheduleModal() { document.getElementById('reschedule-modal').classList.remove('open'); }

/**
 * Configura los formularios del dashboard, incluyendo la lógica de "Drag and Drop" para imágenes.
 */
function setupForms() {
    // Lógica de Vista Previa de Imagen y Arrastrar/Soltar
    const imageInput = document.getElementById('service-image-input');
    const dropZone = document.getElementById('service-drop-zone');

    if (dropZone && imageInput) {
        dropZone.addEventListener('click', () => imageInput.click());

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        ['dragleave', 'dragend'].forEach(type => {
            dropZone.addEventListener(type, () => {
                dropZone.classList.remove('drag-over');
            });
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                imageInput.files = files;
                handleImageSelection(files[0]);
            }
        });

        imageInput.addEventListener('change', (e) => {
            if (e.target.files[0]) handleImageSelection(e.target.files[0]);
        });
    }

    /**
     * Muestra una vista previa de la imagen seleccionada antes de subirla.
     */
    function handleImageSelection(file) {
        if (file) {
            const reader = new FileReader();
            reader.onload = (e) => {
                const preview = document.getElementById('service-image-preview');
                preview.querySelector('img').src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }
    }

    // Procesamiento del formulario de creación/edición de servicio
    document.getElementById('service-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('service-id').value;
        const imageInput = document.getElementById('service-image-input');
        let image_urls = [];

        // Recuperar imágenes existentes si estamos editando
        if (id) {
            const service = window._services.find(s => s.id == id);
            if (service && service.image_urls) image_urls = [...service.image_urls];
        }

        // Subir nueva imagen al servidor si se seleccionó una
        if (imageInput.files.length > 0) {
            const formData = new FormData();
            formData.append('file', imageInput.files[0]);
            try {
                const uploadRes = await fetch(`${API_BASE}/services/upload-image`, {
                    method: 'POST',
                    headers: { 'Authorization': `Bearer ${sessionStorage.getItem(AUTH_TOKEN_KEY)}` },
                    body: formData
                });
                if (uploadRes.ok) {
                    const uploadData = await uploadRes.json();
                    image_urls = [uploadData.url]; // Por ahora, se maneja una sola imagen principal
                } else {
                    alert('Error al subir la imagen al servidor');
                    return;
                }
            } catch (err) {
                alert('Error de red al intentar subir la imagen');
                return;
            }
        }

        const body = {
            title: document.getElementById('service-title').value,
            description: document.getElementById('service-description').value,
            price: parseFloat(document.getElementById('service-price').value),
            category: document.getElementById('service-category').value,
            image_urls: image_urls
        };

        const method = id ? 'PUT' : 'POST';
        const url = id ? `${API_BASE}/services/${id}` : `${API_BASE}/services`;

        try {
            const res = await fetch(url, {
                method,
                headers: getHeaders(),
                body: JSON.stringify(body)
            });
            if (res.ok) {
                showToast(id ? 'Servicio actualizado correctamente' : 'Servicio creado exitosamente');
                closeServiceModal();
                renderServices();
            } else {
                const err = await res.json();
                alert('Error en la operación: ' + (err.detail || 'No se pudo guardar el servicio'));
            }
        } catch (err) {
            alert('Error de red al conectar con el servidor');
        }
    });

    // Procesamiento del formulario de reprogramación de citas
    document.getElementById('reschedule-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('reschedule-request-id').value;
        const date = document.getElementById('reschedule-date').value;
        await fetch(`${API_BASE}/requests/${id}/reschedule`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify({ status: 'ACCEPTED', scheduled_date: date })
        });
        closeRescheduleModal();
        renderRequests();
    });
}
// Consolidated handleProfileSubmit moved up.

function showToast(msg) {
    const t = document.createElement('div'); t.style.cssText = 'background:#10B981; color:white; padding:12px 24px; border-radius:8px; margin-top:8px; box-shadow:0 4px 6px rgba(0,0,0,0.1); animation: fadein 0.3s;'; t.textContent = msg; document.getElementById('toast-container').appendChild(t); setTimeout(() => t.remove(), 3000);
}

// --- Lógica del Módulo de Chat (Espejo del Chat de Usuario) ---

/**
 * Inicializa el módulo de chat dentro del área de contenido del dashboard.
 * Configura la interfaz, enlaza eventos y comienza el polleo de mensajes.
 */
async function initChatModule() {
    const user = chatState.user;
    if (!user || (!user.id && !user.sub)) {
        chatState.user = JSON.parse(localStorage.getItem(USER_KEY) || '{}');
    }

    // Inyectar la estructura del chat (HTML dinámico) en el área de contenido
    document.getElementById('content-area').innerHTML = `
        <div class="chat-container" id="chat-container">
            <!-- Barra Lateral del Chat: Lista de Conversaciones -->
            <aside class="chat-sidebar">
                <div class="chat-search-container">
                    <input type="text" class="chat-search-input" placeholder="Buscar conversación..." id="chat-search-input">
                </div>
                <div class="conversation-list" id="conversation-list">
                    <div style="padding: 20px; text-align: center; color: var(--text-tertiary);">Cargando conversaciones...</div>
                </div>
            </aside>

            <!-- Área Principal del Chat -->
            <section class="chat-area">
                <!-- Cabecera del Chat: Información del participante activo -->
                <div class="chat-header" id="chat-header" style="visibility: hidden;">
                    <div class="header-user">
                        <div class="back-button" id="chat-back-btn">←</div>
                        <div class="chat-avatar" id="header-avatar" style="width:40px; height:40px;">?</div>
                        <div class="header-info">
                            <h3 id="header-name">Selecciona un chat</h3>
                            <div class="header-status" id="header-status"></div>
                        </div>
                    </div>
                </div>

                <!-- Estado Vacío: Se muestra cuando no hay chat seleccionado -->
                <div class="chat-empty-state" id="empty-state">
                    <div class="empty-icon">💬</div>
                    <h3>Tus Mensajes</h3>
                    <p>Selecciona una conversación para hablar con tus clientes y coordinar servicios.</p>
                </div>

                <!-- Contenedor de Mensajes -->
                <div class="messages-container" id="messages-container" style="display: none;"></div>

                <!-- Área de Entrada de Texto -->
                <div class="chat-input-area" id="input-area" style="display: none;">
                    <div class="input-wrapper">
                        <textarea class="chat-input" placeholder="Escribe un mensaje..." rows="1" id="chat-input-field"></textarea>
                        <button class="btn-send" id="chat-send-btn" disabled>
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16">
                                <path d="M15.854.146a.5.5 0 0 1 .11.54l-5.819 14.547a.75.75 0 0 1-1.329.124l-3.178-4.995L.643 7.184a.75.75 0 0 1 .124-1.33L15.314.037a.5.5 0 0 1 .54.11ZM6.636 10.07l2.761 4.338L14.13 2.576 6.636 10.07Zm6.787-8.201L1.591 6.602l4.339 2.76 7.494-7.493Z"/>
                            </svg>
                        </button>
                    </div>
                </div>
            </section>
        </div>
    `;

    // Enlazar Eventos de la Interfaz de Chat
    const searchInput = document.getElementById('chat-search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value;
            renderConversationList(chatState.conversations, term);
        });
    }

    const sendBtn = document.getElementById('chat-send-btn');
    const inputField = document.getElementById('chat-input-field');

    if (inputField) {
        // Ajuste automático de altura del campo de texto
        inputField.addEventListener('input', () => {
            sendBtn.disabled = inputField.value.trim().length === 0;
            inputField.style.height = 'auto';
            inputField.style.height = inputField.scrollHeight + 'px';
        });

        // Enviar con Enter (sin Shift)
        inputField.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
            }
        });
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', sendChatMessage);
    }

    const backBtn = document.getElementById('chat-back-btn');
    if (backBtn) {
        backBtn.addEventListener('click', () => {
            chatState.currentConversationId = null;
            document.getElementById('chat-container').classList.remove('chat-open');
        });
    }

    // Carga inicial de datos
    await fetchConversations();

    // Abrir conversación pendiente si existe (ej. desde el botón "Chatear" en solicitudes)
    if (chatState.pendingConversationId) {
        selectConversation(chatState.pendingConversationId);
        chatState.pendingConversationId = null;
    }

    // Iniciar ciclo de sincronización (polleo) cada 5 segundos
    chatState.pollingInterval = setInterval(async () => {
        await fetchConversations(true); // Actualización silenciosa de la lista
        if (chatState.currentConversationId) {
            await fetchMessages(chatState.currentConversationId, true); // Actualización silenciosa del chat activo
        }
    }, 5000);
}

/**
 * Obtiene la lista de conversaciones activas del proveedor.
 * @param {boolean} silent - Si es true, no actualiza la UI a menos que haya cambios de datos.
 */
async function fetchConversations(silent = false) {
    try {
        const res = await fetch(`${CHAT_API_BASE}`, { headers: getHeaders() });
        if (!res.ok) return;
        const data = await res.json();

        // Evitar re-renderizado innecesario si los datos no han cambiado
        if (silent && JSON.stringify(data) === JSON.stringify(chatState.conversations)) return;

        // Ordenar por actividad más reciente
        chatState.conversations = data.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));

        const term = document.getElementById('chat-search-input')?.value || '';
        renderConversationList(chatState.conversations, term);
    } catch (e) {
        if (!silent) console.error('Error al cargar conversaciones', e);
    }
}

/**
 * Renderiza la lista de conversaciones en la barra lateral del chat.
 * @param {Array} list - Lista de objetos de conversación.
 * @param {string} filterText - Texto para filtrar por nombre de cliente.
 */
function renderConversationList(list, filterText = "") {
    const container = document.getElementById('conversation-list');
    if (!container) return;

    // Filtrar conversaciones por el nombre del participante
    const filtered = list.filter(c => {
        const name = c.participant?.full_name || 'Usuario';
        return name.toLowerCase().includes(filterText.toLowerCase());
    });

    if (filtered.length === 0) {
        container.innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-tertiary);">No se encontraron conversaciones.</div>';
        return;
    }

    const myId = chatState.user.id || (JSON.parse(sessionStorage.getItem(USER_KEY) || '{}')).id;

    container.innerHTML = filtered.map(c => {
        const user = c.participant || { full_name: 'Usuario', avatar_initials: '?' };
        const isActive = chatState.currentConversationId === c.id ? 'active' : '';
        const lastMsg = c.last_message ? c.last_message.content : 'Sin mensajes';
        const time = c.last_message ? new Date(c.last_message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';

        // Lógica de mensajes no leídos: Resaltar si el último mensaje no es mío y no ha sido leído
        let unreadClass = '';
        let unreadBadge = '';
        if (c.last_message && !c.last_message.is_read && Number(c.last_message.sender_id) !== Number(myId)) {
            unreadClass = 'unread';
            unreadBadge = `<span class="unread-badge">!</span>`;
        }

        const avatarHtml = user.avatar_url
            ? `<img src="${user.avatar_url}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;">`
            : (user.avatar_initials || '?');

        return `
            <div class="conversation-item ${isActive} ${unreadClass}" onclick="selectConversation(${c.id})">
                <div class="avatar-wrapper">
                    <div class="chat-avatar" style="${user.avatar_url ? 'background:none;' : ''}">${avatarHtml}</div>
                </div>
                <div class="conversation-info">
                    <div class="conv-top">
                        <span class="conv-name">${user.full_name}</span>
                        <span class="conv-time">${time}</span>
                    </div>
                    <div class="conv-bottom">
                        <span class="conv-preview">${escapeHtml(lastMsg)}</span>
                        ${unreadBadge}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * Selecciona una conversación y carga su historial de mensajes.
 * @param {number} id - ID de la conversación.
 */
async function selectConversation(id) {
    if (chatState.currentConversationId === id) return;
    chatState.currentConversationId = id;

    // Actualizar UI para reflejar la selección activa
    renderConversationList(chatState.conversations, document.getElementById('chat-search-input').value);

    document.getElementById('empty-state').style.display = 'none';
    const msgsContainer = document.getElementById('messages-container');
    msgsContainer.style.display = 'flex';
    document.getElementById('input-area').style.display = 'block';
    document.getElementById('chat-header').style.visibility = 'visible';
    document.getElementById('chat-container').classList.add('chat-open');

    // Actualizar información de la cabecera con los datos del cliente
    const conv = chatState.conversations.find(c => c.id === id);
    if (conv) {
        const user = conv.participant || {};
        document.getElementById('header-name').textContent = user.full_name || 'Usuario';
        const avatarEl = document.getElementById('header-avatar');
        if (user.avatar_url) avatarEl.innerHTML = `<img src='${user.avatar_url}' style='width:100%;height:100%;border-radius:50%;object-fit:cover;'>`;
        else { avatarEl.textContent = user.avatar_initials || '?'; avatarEl.innerHTML = user.avatar_initials || '?'; }
    }

    msgsContainer.innerHTML = '<div style="text-align:center; padding:20px;">Cargando mensajes...</div>';
    await fetchMessages(id);
}

/**
 * Obtiene y renderiza los mensajes de una conversación específica.
 * @param {number} id - ID de la conversación.
 * @param {boolean} silent - Si es true, actualiza sin desplazar el scroll (para polleo).
 */
async function fetchMessages(id, silent = false) {
    try {
        const res = await fetch(`${CHAT_API_BASE}/${id}/messages`, { headers: getHeaders() });
        if (!res.ok) return;
        const msgs = await res.json();

        const container = document.getElementById('messages-container');
        if (!container) return;

        const myId = chatState.user.id || (JSON.parse(sessionStorage.getItem(USER_KEY) || '{}')).id;

        const html = msgs.sort((a, b) => new Date(a.created_at) - new Date(b.created_at)).map(m => {
            const isMine = Number(m.sender_id) === Number(myId);
            const time = new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            return `
                <div class="message-row ${isMine ? 'sent' : 'received'}">
                    <div class="message-bubble">
                        ${escapeHtml(m.content)}
                        <span class="message-meta">${time}</span>
                    </div>
                </div>
            `;
        }).join('');

        // Solo actualizar el DOM si el contenido ha cambiado (para el polleo silencioso)
        if (silent) {
            if (container.innerHTML !== html) container.innerHTML = html;
        } else {
            container.innerHTML = html;
            scrollToBottom();
        }

    } catch (e) { console.error('Error al cargar mensajes', e); }
}

/**
 * Envía un nuevo mensaje en la conversación actual.
 */
async function sendChatMessage() {
    const input = document.getElementById('chat-input-field');
    const content = input.value.trim();
    if (!content || !chatState.currentConversationId || chatState.isSending) return;

    chatState.isSending = true;
    const sendBtn = document.getElementById('chat-send-btn');
    sendBtn.disabled = true;

    try {
        const res = await fetch(`${CHAT_API_BASE}/messages/send`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify({
                conversation_id: chatState.currentConversationId,
                content: content
            })
        });

        if (res.ok) {
            input.value = '';
            input.style.height = 'auto'; // Resetear altura del textarea
            await fetchMessages(chatState.currentConversationId); // Recargar para mostrar el nuevo mensaje
            await fetchConversations(true); // Actualizar lista de conversaciones para actualizar el preview
            scrollToBottom();
        } else {
            alert('Error al enviar mensaje');
        }
    } catch (e) { console.error('Error al enviar', e); }
    finally {
        chatState.isSending = false;
        sendBtn.disabled = false;
    }
}

/**
 * Desplaza el contenedor de mensajes hacia el final (más reciente).
 */
function scrollToBottom() {
    const c = document.getElementById('messages-container');
    if (c) c.scrollTop = c.scrollHeight;
}

/**
 * Escapa caracteres HTML para prevenir ataques XSS.
 * @param {string} text - Texto plano.
 * @returns {string} - Texto escapado.
 */
function escapeHtml(text) {
    if (!text) return "";
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
