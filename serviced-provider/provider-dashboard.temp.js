/**
 * Provider Dashboard Logic
 * Refactored to use Bento Grid System & User-Chat like Messaging
 */

const API_BASE = '/api/v1/provider/dashboard';
const CHAT_API_BASE = '/api/v1/conversations';
const AUTH_TOKEN_KEY = 'serviced_token';
/* USER_KEY is used to retrieve user info for chat. Ideally this should come from a profile endpoint, 
   but for now we rely on localStorage matching user-chat logic */
const USER_KEY = 'serviced_user';

// --- Init ---
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupNavigation();
    setupForms();

    // Routing
    const urlParams = new URLSearchParams(window.location.search);
    loadView(urlParams.get('view') || 'overview');

    // Logout
    document.getElementById('logout-btn').addEventListener('click', (e) => {
        e.preventDefault();
        localStorage.removeItem(AUTH_TOKEN_KEY);
        // localStorage.removeItem(USER_KEY); // Optional: keep for convenience or clear
        window.location.href = '/login.html';
    });
});

function checkAuth() {
    if (!localStorage.getItem(AUTH_TOKEN_KEY)) {
        // window.location.href = '/login.html';
    }
}

function getHeaders() {
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem(AUTH_TOKEN_KEY)}`
    };
}

// --- Navigation & Routing ---
function setupNavigation() {
    document.querySelectorAll('.nav-item[data-target]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.dataset.target;
            loadView(view);
            // Update URL
            const newUrl = new URL(window.location);
            newUrl.searchParams.set('view', view);
            window.history.pushState({}, '', newUrl);
        });
    });
}

// --- Chat State ---
const chatState = {
    pollingInterval: null,
    currentConversationId: null,
    conversations: [],
    user: JSON.parse(localStorage.getItem(USER_KEY) || '{}'),
    isSending: false
};

function loadView(viewName) {
    // Cleanup Chat Polling
    if (chatState.pollingInterval) clearInterval(chatState.pollingInterval);
    chatState.pollingInterval = null;
    chatState.currentConversationId = null;

    // Active Nav State
    document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
    const activeNav = document.querySelector(`.nav-item[data-target="${viewName}"]`);
    if (activeNav) activeNav.classList.add('active');

    // Title Update
    const titles = { overview: 'Vista General', services: 'Mis Servicios', requests: 'Solicitudes', calendar: 'Calendario', reviews: 'Reseñas', notifications: 'Notificaciones', profile: 'Perfil', messages: 'Mensajes' };
    document.getElementById('page-title').textContent = titles[viewName] || 'Dashboard';

    // Render Content
    const contentArea = document.getElementById('content-area');
    contentArea.innerHTML = '<div class="spinner"></div>';

    switch (viewName) {
        case 'overview': renderOverview(); break;
        case 'services': renderServices(); break;
        case 'requests': renderRequests(); break;
        case 'calendar': renderCalendar(); break;
        case 'reviews': renderReviews(); break;
        case 'notifications': renderNotifications(); break;
        case 'profile': renderProfile(); break;
        case 'messages': initChatModule(); break;
        default: renderOverview();
    }
}

// --- Renderers (Bento Style) ---

async function renderOverview() {
    try {
        const res = await fetch(`${API_BASE}/overview`, { headers: getHeaders() });

        if (res.status === 403) {
            let errDetail = 'Acceso Denegado';
            try { const errData = await res.json(); errDetail = errData.detail || 'Sin detalles'; } catch (e) { }
            document.getElementById('content-area').innerHTML = `
                <div class="bento-card" style="grid-column: span 12; text-align: center; padding: 48px;">
                    <div style="font-size: 3rem; margin-bottom: 16px;">🚫</div>
                    <h3 class="text-h2">Acceso Denegado</h3>
                    <p class="text-body" style="margin-top: 16px; margin-bottom: 24px;">Tu cuenta actual no tiene permisos de Proveedor.</p>
                    <div style="font-family:monospace; background:#f3f4f6; padding:8px; border-radius:4px; margin-bottom:16px;">Error: ${errDetail}</div>
                    <button class="btn btn-primary" onclick="localStorage.removeItem('${AUTH_TOKEN_KEY}'); window.location.href = '/login.html';">Cerrar Sesión</button>
                </div>`;
            return;
        }

        if (!res.ok) throw new Error(`API Error: ${res.status}`);
        const data = await res.json();
        const upcoming_jobs = Array.isArray(data.upcoming_jobs) ? data.upcoming_jobs : [];
        const stats = { total_services: data.total_services || 0, pending_requests: data.pending_requests || 0, average_rating: data.average_rating || 0, balance: data.balance || 0 };

        document.getElementById('content-area').innerHTML = `
            <div class="bento-grid">
                <div class="bento-card stat-card"><span class="text-sm">Total Servicios</span><div class="text-h2" style="margin-top: 8px;">${stats.total_services}</div></div>
                <div class="bento-card stat-card"><span class="text-sm">Solicitudes Pendientes</span><div class="text-h2" style="margin-top: 8px; color: var(--warning);">${stats.pending_requests}</div></div>
                <div class="bento-card stat-card"><span class="text-sm">Rating General</span><div class="text-h2" style="margin-top: 8px;">${stats.average_rating.toFixed(1)} <span style="font-size:1rem; color:var(--warning);">★</span></div></div>
                <div class="bento-card stat-card"><span class="text-sm">Balance Estimado</span><div class="text-h2" style="margin-top: 8px; color: var(--success);">$${stats.balance}</div></div>
                <div class="bento-card" style="grid-column: span 8; grid-row: span 2;">
                    <div style="display:flex; justify-content:space-between; margin-bottom: 16px;"><h3 class="text-h3">Próximos Trabajos</h3><button class="btn btn-secondary" style="padding: 4px 12px; font-size: 0.8rem;" onclick="loadView('requests')">Ver todos</button></div>
                    <div class="table-container"><table><thead><tr><th>Cliente</th><th>Servicio</th><th>Fecha</th><th>Estado</th></tr></thead>
                            <tbody>${upcoming_jobs.length > 0 ? upcoming_jobs.map(job => `
                                    <tr><td style="font-weight:500;">${job.client_name}</td><td>${job.service_title}</td><td>${new Date(job.scheduled_date).toLocaleDateString()} ${new Date(job.scheduled_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</td><td><span class="badge badge-accepted">${job.status}</span></td></tr>
                                `).join('') : '<tr><td colspan="4" style="text-align:center;">No hay trabajos próximos.</td></tr>'}
                            </tbody></table></div></div>
                <div class="bento-card" style="grid-column: span 4; grid-row: span 2;"><h3 class="text-h3" style="margin-bottom: 16px;">Acciones Rápidas</h3><div style="display: flex; flex-direction: column; gap: 12px;"><button class="btn btn-primary" style="width: 100%;" onclick="openCreateServiceModal()">+ Crear Nuevo Servicio</button><button class="btn btn-secondary" style="width: 100%;" onclick="loadView('profile')">Editar Perfil</button></div></div>
            </div>`;
    } catch (e) {
        console.error("Render Overview Error:", e);
        document.getElementById('content-area').innerHTML = `<div class="bento-card" style="color:red;">Error cargando dashboard: ${e.message}</div>`;
    }
}

async function renderServices() {
    try {
        const res = await fetch(`${API_BASE}/services`, { headers: getHeaders() });
        if (!res.ok) throw new Error(`API Error: ${res.status}`);
        const services = await res.json();
        const safeServices = Array.isArray(services) ? services : [];
        window._services = safeServices;

        document.getElementById('content-area').innerHTML = `
            <div class="bento-card" style="width: 100%;">
                 <div style="display:flex; justify-content:space-between; margin-bottom: 24px;"><h3 class="text-h3">Mis Servicios (${safeServices.length})</h3><button class="btn btn-primary" onclick="openCreateServiceModal()">Nuevo Servicio</button></div>
                <div class="table-container"><table><thead><tr><th>Servicio</th><th>Precio</th><th>Categoria</th><th>Estado</th><th>Acciones</th></tr></thead>
                        <tbody>${safeServices.length > 0 ? safeServices.map(s => `
                                <tr><td><div style="font-weight:600;">${s.title}</div><div class="text-sm">${s.duration || (s.duration_minutes ? s.duration_minutes + ' m' : '-')}</div></td><td>$${s.price}</td><td>${s.category || '-'}</td><td><span class="badge ${s.is_active ? 'badge-active' : 'badge-inactive'}">${s.is_active ? 'Activo' : 'Inactivo'}</span></td><td>
                                        <button class="btn btn-secondary" style="padding:6px;" onclick="editService(${s.id})"><i class="fas fa-edit"></i></button> <button class="btn btn-secondary" style="padding:6px;" onclick="toggleService(${s.id})"><i class="fas fa-power-off"></i></button> <button class="btn btn-danger" style="padding:6px;" onclick="deleteService(${s.id})"><i class="fas fa-trash"></i></button></td></tr>
                            `).join('') : '<tr><td colspan="5" style="text-align:center;">No tienes servicios creados.</td></tr>'}
                        </tbody></table></div></div>`;
    } catch (e) { document.getElementById('content-area').innerHTML = `<div class="bento-card" style="color:red;">Error: ${e.message}</div>`; }
}

async function renderRequests() {
    try {
        const res = await fetch(`${API_BASE}/requests`, { headers: getHeaders() });
        if (!res.ok) throw new Error(`API Error: ${res.status}`);
        const requests = await res.json();
        const safeRequests = Array.isArray(requests) ? requests : [];
        document.getElementById('content-area').innerHTML = `
            <div class="bento-card" style="width: 100%;"><h3 class="text-h3" style="margin-bottom: 24px;">Solicitudes de Clientes</h3><div class="table-container"><table><thead><tr><th>Cliente</th><th>Solicitud</th><th>Fecha Propuesta</th><th>Estado</th><th>Acciones</th></tr></thead>
                        <tbody>${safeRequests.length > 0 ? safeRequests.map(r => `
                                <tr><td>${r.client_name}</td><td><div style="font-weight:600;">${r.service_title}</div><div class="text-sm">$${r.price}</div></td><td>${new Date(r.scheduled_date).toLocaleString()}</td><td><span class="badge badge-${r.status.toLowerCase()}">${r.status}</span></td><td>${renderRequestActions(r)}</td></tr>
                             `).join('') : '<tr><td colspan="5" style="text-align:center;">No tienes solicitudes pendientes.</td></tr>'}
                        </tbody></table></div></div>`;
    } catch (e) { document.getElementById('content-area').innerHTML = `<div class="bento-card" style="color:red;">Error: ${e.message}</div>`; }
}

function renderRequestActions(req) {
    if (req.status === 'PENDING') return `<button class="btn btn-primary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="updateRequestStatus(${req.id}, 'accept')">Aceptar</button> <button class="btn btn-danger" style="padding: 6px 12px; font-size: 0.8rem;" onclick="updateRequestStatus(${req.id}, 'reject')">Rechazar</button>`;
    if (req.status === 'ACCEPTED' || req.status === 'ACTIVE') return `<button class="btn btn-primary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="updateRequestStatus(${req.id}, 'complete')">Completar</button> <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.8rem;" onclick="openRescheduleModal(${req.id})">Reprogramar</button>`;
    return '';
}

async function renderCalendar() {
    try {
        const res = await fetch(`${API_BASE}/requests?status=ACCEPTED`, { headers: getHeaders() });
        const requests = await res.json();
        requests.sort((a, b) => new Date(a.scheduled_date) - new Date(b.scheduled_date));
        document.getElementById('content-area').innerHTML = `<div class="bento-grid">${requests.map(r => `
                    <div class="bento-card" style="grid-column: span 4; border-left: 4px solid var(--primary);"><div style="display:flex; gap: 16px; align-items:center;"><div style="background:#EFF6FF; padding: 12px; border-radius:8px; text-align:center; min-width: 60px;"><div style="font-weight:700; font-size:1.2rem; color:var(--primary);">${new Date(r.scheduled_date).getDate()}</div><div style="font-size:0.8rem; text-transform:uppercase; color:var(--primary);">${new Date(r.scheduled_date).toLocaleString('default', { month: 'short' })}</div></div><div><div style="font-weight:600;">${r.service_title}</div><div class="text-sm">Cliente: ${r.client_name}</div><div class="text-sm" style="color:var(--text-main); margin-top:4px;"><i class="fas fa-clock"></i> ${new Date(r.scheduled_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div></div></div></div>
                `).join('')}${requests.length === 0 ? '<div class="bento-card" style="grid-column: span 12;">No hay citas programadas.</div>' : ''}</div>`;
    } catch (e) { }
}

async function renderReviews() {
    try {
        const res = await fetch(`${API_BASE}/reviews`, { headers: getHeaders() });
        const reviews = await res.json();
        document.getElementById('content-area').innerHTML = `<div class="bento-grid">${reviews.map(r => `
                    <div class="bento-card" style="grid-column: span 4;"><div style="display:flex; justify-content:space-between; margin-bottom: 12px;"><div style="font-weight:600;">${r.client_name || 'Cliente'}</div><div style="color:var(--warning);">${'★'.repeat(r.rating)}</div></div><p class="text-body" style="font-style:italic;">"${r.comment}"</p><div class="text-sm" style="margin-top: 12px;">${new Date(r.created_at).toLocaleDateString()}</div></div>
                 `).join('')}${reviews.length === 0 ? '<div class="bento-card" style="grid-column: span 12;">No hay reseñas aún.</div>' : ''}</div>`;
    } catch (e) { }
}

async function renderNotifications() {
    try {
        const res = await fetch(`${API_BASE}/notifications`, { headers: getHeaders() });
        const notifs = await res.json();
        document.getElementById('content-area').innerHTML = `<div class="bento-card" style="grid-column: span 8; margin: 0 auto; max-width: 800px;"><h3 class="text-h3" style="margin-bottom: 20px;">Notificaciones</h3><div style="display:flex; flex-direction:column; gap: 0;">${notifs.map(n => `
                        <div style="padding: 16px; border-bottom: 1px solid #E5E7EB; border-left: 3px solid ${n.is_read ? 'transparent' : 'var(--primary)'}; background: ${n.is_read ? 'white' : '#F9FAFB'};"><div style="font-weight:600; margin-bottom: 4px;">${n.title}</div><div class="text-body">${n.message}</div><div class="text-sm" style="margin-top:8px;">${new Date(n.created_at).toLocaleString()}</div></div>
                    `).join('')}</div></div>`;
    } catch (e) { }
}

async function renderProfile() {
    try {
        const res = await fetch(`${API_BASE}/profile`, { headers: getHeaders() });
        const profile = await res.json();
        document.getElementById('content-area').innerHTML = `<div class="bento-card" style="max-width: 600px; margin: 0 auto; grid-column: span 12;"><h3 class="text-h3" style="margin-bottom: 24px;">Editar Perfil Profesional</h3><form id="profile-form"><div class="form-group"><label class="form-label">Nombre Visible</label><input type="text" class="form-control" value="${profile.full_name}" disabled style="background:#F3F4F6;"></div><div class="form-group"><label class="form-label">Sobre mí (Descripción)</label><textarea class="form-control" id="profile-description" rows="4">${profile.description || ''}</textarea></div><div class="form-group"><label class="form-label">Años de Experiencia</label><input type="number" class="form-control" id="profile-experience" value="${profile.experience_years || 0}"></div><div class="form-group"><label class="form-label">Ubicación</label><input type="text" class="form-control" id="profile-location" value="${profile.location || ''}"></div><div class="form-group"><label class="form-label">Disponibilidad Típica</label><input type="text" class="form-control" id="profile-availability" value="${profile.availability || ''}"></div><div style="text-align:right; margin-top:24px;"><button type="submit" class="btn btn-primary">Guardar Cambios</button></div></form></div>`;
        document.getElementById('profile-form').addEventListener('submit', handleProfileSubmit);
    } catch (e) { }
}


// --- Action Handlers ---
function openCreateServiceModal() { document.getElementById('service-form').reset(); document.getElementById('service-id').value = ''; document.getElementById('service-modal').classList.add('open'); }
function closeServiceModal() { document.getElementById('service-modal').classList.remove('open'); }
function editService(id) {
    const service = window._services.find(s => s.id === id); if (!service) return;
    document.getElementById('service-id').value = id; document.getElementById('service-title').value = service.title; document.getElementById('service-description').value = service.description; document.getElementById('service-price').value = service.price; document.getElementById('service-category').value = service.category; document.getElementById('service-modal').classList.add('open');
}
async function toggleService(id) { await fetch(`${API_BASE}/services/${id}/toggle`, { method: 'PUT', headers: getHeaders() }); renderServices(); }
async function deleteService(id) { if (confirm('¿Eliminar servicio?')) { await fetch(`${API_BASE}/services/${id}`, { method: 'DELETE', headers: getHeaders() }); renderServices(); } }
async function updateRequestStatus(id, action) { await fetch(`${API_BASE}/requests/${id}/${action}`, { method: 'PUT', headers: getHeaders() }); renderRequests(); }
function openRescheduleModal(id) { document.getElementById('reschedule-request-id').value = id; document.getElementById('reschedule-modal').classList.add('open'); }
function closeRescheduleModal() { document.getElementById('reschedule-modal').classList.remove('open'); }

function setupForms() {
    document.getElementById('service-form').addEventListener('submit', async (e) => {
        e.preventDefault(); const id = document.getElementById('service-id').value; const body = { title: document.getElementById('service-title').value, description: document.getElementById('service-description').value, price: document.getElementById('service-price').value, category: document.getElementById('service-category').value };
        const method = id ? 'PUT' : 'POST'; const url = id ? `${API_BASE}/services/${id}` : `${API_BASE}/services`; await fetch(url, { method, headers: getHeaders(), body: JSON.stringify(body) }); closeServiceModal(); renderServices();
    });
    document.getElementById('reschedule-form').addEventListener('submit', async (e) => {
        e.preventDefault(); const id = document.getElementById('reschedule-request-id').value; const date = document.getElementById('reschedule-date').value; await fetch(`${API_BASE}/requests/${id}/reschedule`, { method: 'PUT', headers: getHeaders(), body: JSON.stringify({ status: 'ACCEPTED', scheduled_date: date }) }); closeRescheduleModal(); renderRequests();
    });
}
async function handleProfileSubmit(e) {
    e.preventDefault(); const body = { description: document.getElementById('profile-description').value, experience_years: document.getElementById('profile-experience').value, location: document.getElementById('profile-location').value, availability: document.getElementById('profile-availability').value };
    await fetch(`${API_BASE}/profile`, { method: 'PUT', headers: getHeaders(), body: JSON.stringify(body) }); showToast('Perfil actualizado');
}
function showToast(msg) {
    const t = document.createElement('div'); t.style.cssText = 'background:#10B981; color:white; padding:12px 24px; border-radius:8px; margin-top:8px; box-shadow:0 4px 6px rgba(0,0,0,0.1); animation: fadein 0.3s;'; t.textContent = msg; document.getElementById('toast-container').appendChild(t); setTimeout(() => t.remove(), 3000);
}

// --- Chat Module Logic (Mirrors User Chat) ---

async function initChatModule() {
    const user = chatState.user;
    if (!user || !user.id) {
        document.getElementById('content-area').innerHTML = '<div class="bento-card" style="color:red;">Error: No se encontró información de usuario. Re-login requerido.</div>';
        return;
    }

    // Matches user-chat.html structure inside the content area
    // Note: We use CHAT_API_BASE for chat operations
    document.getElementById('content-area').innerHTML = `
        <div class="chat-container" id="chat-container">
            <!-- Chat Sidebar -->
            <aside class="chat-sidebar">
                <div class="chat-search-container">
                    <input type="text" class="chat-search-input" placeholder="Buscar conversación..." id="chat-search-input">
                </div>
                <div class="conversation-list" id="conversation-list">
                    <div style="padding: 20px; text-align: center; color: var(--text-tertiary);">Cargando...</div>
                </div>
            </aside>

            <!-- Chat Area -->
            <section class="chat-area">
                <!-- Chat Header -->
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

                <!-- Empty State -->
                <div class="chat-empty-state" id="empty-state">
                    <div class="empty-icon">💬</div>
                    <h3>Tus Mensajes</h3>
                    <p>Selecciona una conversación para hablar con tus clientes.</p>
                </div>

                <!-- Messages -->
                <div class="messages-container" id="messages-container" style="display: none;"></div>

                <!-- Input Area -->
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

    // Bind Events
    document.getElementById('chat-search-input').addEventListener('input', (e) => {
        const term = e.target.value;
        renderConversationList(chatState.conversations, term);
    });

    const sendBtn = document.getElementById('chat-send-btn');
    const inputField = document.getElementById('chat-input-field');

    inputField.addEventListener('input', () => {
        sendBtn.disabled = inputField.value.trim().length === 0;
        inputField.style.height = 'auto';
        inputField.style.height = inputField.scrollHeight + 'px';
    });

    inputField.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendChatMessage();
        }
    });

    sendBtn.addEventListener('click', sendChatMessage);

    document.getElementById('chat-back-btn').addEventListener('click', () => {
        chatState.currentConversationId = null;
        document.getElementById('chat-container').classList.remove('chat-open');
    });

    // Initial Load
    await fetchConversations();

    // Resume polling
    chatState.pollingInterval = setInterval(async () => {
        await fetchConversations(true);
        if (chatState.currentConversationId) {
            await fetchMessages(chatState.currentConversationId, true);
        }
    }, 5000); // 5s cycle
}

async function fetchConversations(silent = false) {
    try {
        const res = await fetch(`${CHAT_API_BASE}`, { headers: getHeaders() });
        if (!res.ok) return;
        const data = await res.json();

        if (silent && JSON.stringify(data) === JSON.stringify(chatState.conversations)) return;

        chatState.conversations = data.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));

        const term = document.getElementById('chat-search-input')?.value || '';
        renderConversationList(chatState.conversations, term);
    } catch (e) {
        if (!silent) console.error('Error loading conversations', e);
    }
}

function renderConversationList(list, filterText = "") {
    const container = document.getElementById('conversation-list');
    if (!container) return;

    const filtered = list.filter(c => {
        const name = c.participant?.full_name || 'Usuario';
        return name.toLowerCase().includes(filterText.toLowerCase());
    });

    if (filtered.length === 0) {
        container.innerHTML = '<div style="padding:20px; text-align:center; color:var(--text-tertiary);">No se encontraron conversaciones.</div>';
        return;
    }

    container.innerHTML = filtered.map(c => {
        const user = c.participant || { full_name: 'Usuario', avatar_initials: '?' };
        const isActive = chatState.currentConversationId === c.id ? 'active' : '';
        const lastMsg = c.last_message ? c.last_message.content : 'Sin mensajes';
        const time = c.last_message ? new Date(c.last_message.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '';

        // Unread logic
        let unreadClass = '';
        let unreadBadge = '';
        if (c.last_message && !c.last_message.is_read && Number(c.last_message.sender_id) !== Number(chatState.user.id)) {
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

async function selectConversation(id) {
    if (chatState.currentConversationId === id) return;
    chatState.currentConversationId = id;

    // UI Updates
    renderConversationList(chatState.conversations, document.getElementById('chat-search-input').value);

    document.getElementById('empty-state').style.display = 'none';
    const msgsContainer = document.getElementById('messages-container');
    msgsContainer.style.display = 'flex';
    document.getElementById('input-area').style.display = 'block';
    document.getElementById('chat-header').style.visibility = 'visible';
    document.getElementById('chat-container').classList.add('chat-open');

    // Header Info
    const conv = chatState.conversations.find(c => c.id === id);
    if (conv) {
        const user = conv.participant || {};
        document.getElementById('header-name').textContent = user.full_name || 'Usuario';
        const avatarEl = document.getElementById('header-avatar');
        if (user.avatar_url) avatarEl.innerHTML = `<img src='${user.avatar_url}' style='width:100%;height:100%;border-radius:50%;object-fit:cover;'>`;
        else { avatarEl.textContent = user.avatar_initials || '?'; avatarEl.innerHTML = user.avatar_initials || '?'; }
    }

    msgsContainer.innerHTML = '<div style="text-align:center; padding:20px;">Cargando...</div>';
    await fetchMessages(id);
}

async function fetchMessages(id, silent = false) {
    try {
        const res = await fetch(`${CHAT_API_BASE}/${id}/messages`, { headers: getHeaders() });
        if (!res.ok) return;
        const msgs = await res.json();

        const container = document.getElementById('messages-container');
        if (!container) return;

        const html = msgs.sort((a, b) => new Date(a.created_at) - new Date(b.created_at)).map(m => {
            const isMine = Number(m.sender_id) === Number(chatState.user.id);
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

        if (silent) {
            if (container.innerHTML !== html) container.innerHTML = html;
        } else {
            container.innerHTML = html;
            scrollToBottom();
        }

    } catch (e) { console.error('Error loading messages', e); }
}

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
            input.style.height = 'auto';
            await fetchMessages(chatState.currentConversationId); // Refresh to show new msg
            await fetchConversations(true); // Update list
            scrollToBottom();
        } else {
            alert('Error al enviar mensaje');
        }
    } catch (e) { console.error('Error sending', e); }
    finally {
        chatState.isSending = false;
        sendBtn.disabled = false;
    }
}

function scrollToBottom() {
    const c = document.getElementById('messages-container');
    if (c) c.scrollTop = c.scrollHeight;
}

function escapeHtml(text) {
    if (!text) return "";
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}
