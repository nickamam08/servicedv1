/**
 * Lógica del Chat para Usuarios (Clientes) de SERVICED
 * Gestiona la mensajería en tiempo real, administración de conversaciones y actualizaciones de la interfaz.
 */

document.addEventListener("DOMContentLoaded", () => {
    // --- Constantes de Configuración ---
    const API_BASE_URL = "/api/v1";

    // --- Estado de la Aplicación (Frontend) ---
    let state = {
        token: sessionStorage.getItem("serviced_token"),
        user: JSON.parse(sessionStorage.getItem("serviced_user") || "null"),
        conversations: [],
        currentConversationId: null,
        pollingTimer: null,
        isSending: false
    };

    // --- Elementos del DOM ---
    const els = {
        conversationList: document.getElementById("conversation-list"),
        messagesContainer: document.getElementById("messages-container"),
        chatHeader: document.getElementById("chat-header"),
        headerAvatar: document.getElementById("header-avatar"),
        headerName: document.getElementById("header-name"),
        headerStatus: document.getElementById("header-status"),
        emptyState: document.getElementById("empty-state"),
        inputArea: document.getElementById("input-area"),
        messageInput: document.getElementById("message-input"),
        sendBtn: document.getElementById("send-btn"),
        chatContainer: document.getElementById("chat-container"),
        backBtn: document.getElementById("back-button"),
        logoutLink: document.querySelector(".logout-link"),
        searchInput: document.getElementById("search-input")
    };

    // --- Inicialización ---
    function init() {
        // Verificar autenticación
        if (!state.token || !state.user) {
            window.location.href = "login.html";
            return;
        }

        // Validación de Rol (Evitar que proveedores entren a vista de cliente)
        if (state.user.role !== 'client') {
            console.warn("Rol incorrecto para esta página, redireccionando...");
            if (state.user.role === 'provider') window.location.href = "/provider/provider-dashboard.html";
            else window.location.href = "login.html";
            return;
        }

        // Configuración de Cierre de Sesión
        if (els.logoutLink) {
            els.logoutLink.addEventListener("click", (e) => {
                e.preventDefault();
                sessionStorage.clear();
                window.location.href = "login.html";
            });
        }

        // Manejar parámetros de URL (ej: abrir chat directamente desde perfil de proveedor)
        handleUrlParams();

        // Carga inicial de datos
        fetchConversations();

        // Polling: Actualizar lista de conversaciones cada 10s
        setInterval(fetchConversations, 10000);

        // Configurar escuchadores de eventos
        setupEventListeners();
    }

    function setupEventListeners() {
        // Enviar mensaje al hacer clic en el botón
        els.sendBtn.addEventListener("click", sendMessage);

        // Enviar al presionar Enter (sin Shift)
        els.messageInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Habilitar/deshabilitar botón según contenido y auto-ajustar altura del input
        els.messageInput.addEventListener("input", () => {
            els.sendBtn.disabled = els.messageInput.value.trim().length === 0;
            autoResizeTextarea(els.messageInput);
        });

        // Buscador de conversaciones
        els.searchInput.addEventListener("input", (e) => {
            renderConversationList(state.conversations, e.target.value);
        });

        // Botón de Volver (especialmente para vista móvil)
        els.backBtn.addEventListener("click", () => {
            state.currentConversationId = null;
            els.chatContainer.classList.remove("chat-open");
            if (state.pollingTimer) clearInterval(state.pollingTimer);
        });
    }

    // --- Interacciones con la API ---

    async function fetchConversations() {
        try {
            const resp = await fetch(`${API_BASE_URL}/conversations`, {
                headers: { "Authorization": `Bearer ${state.token}` }
            });

            if (!resp.ok) {
                if (resp.status === 401) {
                    alert("Sesión expirada");
                    window.location.href = "login.html";
                }
                return;
            }

            const data = await resp.json();
            // Ordenar por fecha de última actualización (más recientes primero)
            state.conversations = data.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));

            renderConversationList(state.conversations, els.searchInput.value);

        } catch (e) {
            console.error("Error al obtener conversaciones:", e);
            els.conversationList.innerHTML = `<div style="padding: 20px; text-align: center; color: red;">Error de conexión</div>`;
        }
    }

    async function fetchMessages(conversationId) {
        try {
            const resp = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages`, {
                headers: { "Authorization": `Bearer ${state.token}` }
            });
            if (!resp.ok) throw new Error("Error al cargar mensajes");
            const messages = await resp.json();
            renderMessages(messages);
            // Marcar conversación como leída automáticamente al entrar
            markAsRead(conversationId);
        } catch (e) {
            console.error("Error detallado de mensajes:", e);
        }
    }

    async function markAsRead(conversationId) {
        try {
            await fetch(`${API_BASE_URL}/conversations/${conversationId}/read`, {
                method: "PUT",
                headers: { "Authorization": `Bearer ${state.token}` }
            });
            // Notificar a otros componentes que los badges pueden haber cambiado
            window.dispatchEvent(new CustomEvent('messagesUpdated'));
        } catch (e) {
            console.error("Error al marcar como leído:", e);
        }
    }

    async function sendMessage() {
        const text = els.messageInput.value.trim();
        if (!text || !state.currentConversationId || state.isSending) return;

        state.isSending = true;
        els.sendBtn.disabled = true;

        try {
            const resp = await fetch(`${API_BASE_URL}/conversations/messages/send`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${state.token}`
                },
                body: JSON.stringify({
                    conversation_id: state.currentConversationId,
                    content: text
                })
            });

            if (!resp.ok) throw new Error("Fallo al enviar");

            const msg = await resp.json();

            // Añadir visualmente el mensaje de inmediato para fluidez
            appendMessage(msg);

            // Limpiar campo de texto
            els.messageInput.value = "";
            els.messageInput.style.height = 'auto';

            // Refrescar lista lateral
            fetchConversations();

        } catch (e) {
            console.error(e);
            alert("Error al enviar mensaje");
        } finally {
            state.isSending = false;
        }
    }

    async function createConversation(providerId) {
        try {
            const resp = await fetch(`${API_BASE_URL}/conversations`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${state.token}`
                },
                body: JSON.stringify({ provider_id: parseInt(providerId) })
            });

            if (resp.ok) {
                const conv = await resp.json();
                // Si no existe en la lista local, añadirla al principio
                if (!state.conversations.find(c => c.id === conv.id)) {
                    state.conversations.unshift(conv);
                }
                selectConversation(conv);
            } else {
                const err = await resp.json();
                alert(`Error al iniciar chat: ${err.detail}`);
            }
        } catch (e) {
            console.error(e);
            alert("Error de red al iniciar chat");
        }
    }

    // --- Lógica de Negocio ---

    async function handleUrlParams() {
        const params = new URLSearchParams(window.location.search);
        // Soporta userId o providerId para abrir un chat automáticamente
        const targetId = params.get("userId") || params.get("providerId");

        if (targetId) {
            await createConversation(targetId);
            // Limpiar URL opcionalmente para evitar re-apertura accidental
            // window.history.replaceState({}, document.title, window.location.pathname);
        }
    }

    function selectConversation(conv) {
        if (state.currentConversationId === conv.id) return;

        state.currentConversationId = conv.id;

        // Actualizar UI: clase activa en sidebar
        document.querySelectorAll(".conversation-item").forEach(el => el.classList.remove("active"));
        const activeItem = document.getElementById(`conv-${conv.id}`);
        if (activeItem) activeItem.classList.add("active");

        // Mostrar Área de Chat
        els.emptyState.style.display = "none";
        els.messagesContainer.style.display = "flex";
        els.inputArea.style.display = "block";
        els.chatHeader.style.visibility = "visible";
        els.chatContainer.classList.add("chat-open");

        // Actualizar encabezado del chat con datos del proveedor
        const otherUser = conv.participant || { full_name: "Proveedor", avatar_initials: "?" };
        els.headerName.textContent = otherUser.full_name;

        if (otherUser.avatar_url) {
            els.headerAvatar.innerHTML = `<img src="${otherUser.avatar_url}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">`;
            els.headerAvatar.style.padding = "0";
            els.headerAvatar.style.overflow = "hidden";
        } else {
            els.headerAvatar.textContent = otherUser.avatar_initials || otherUser.full_name[0] || "?";
            els.headerAvatar.style.padding = "";
        }

        // Cargar mensajes previos
        els.messagesContainer.innerHTML = `<div style="text-align:center; padding:20px;">Cargando mensajes...</div>`;
        fetchMessages(conv.id);

        // Iniciar polling de mensajes para el chat abierto (cada 3s)
        if (state.pollingTimer) clearInterval(state.pollingTimer);
        state.pollingTimer = setInterval(() => {
            if (state.currentConversationId === conv.id) fetchMessages(conv.id);
        }, 3000);
    }

    // --- Renderizado de UI ---

    function renderConversationList(list, filterText = "") {
        els.conversationList.innerHTML = "";

        const filtered = list.filter(c => {
            const name = c.participant?.full_name || "Proveedor";
            return name.toLowerCase().includes(filterText.toLowerCase());
        });

        if (filtered.length === 0) {
            els.conversationList.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-tertiary);">No se encontraron conversaciones.</div>`;
            return;
        }

        filtered.forEach(c => {
            const otherUser = c.participant || { full_name: "Proveedor", avatar_initials: "?" };
            const lastMsg = c.last_message ? c.last_message.content : "Sin mensajes";
            const time = c.last_message ? formatTime(c.last_message.created_at) : "";
            const isActive = c.id === state.currentConversationId ? "active" : "";

            let unreadBadge = "";
            let unreadClass = "";
            // Mostrar badge si el último mensaje no fue nuestro y no está leído
            if (c.last_message && !c.last_message.is_read && Number(c.last_message.sender_id) !== Number(state.user.id)) {
                unreadBadge = `<span class="unread-badge">!</span>`;
                unreadClass = "unread";
            }

            const avatarHtml = otherUser.avatar_url
                ? `<img src="${otherUser.avatar_url}" style="width:100%; height:100%; object-fit:cover;">`
                : (otherUser.avatar_initials || otherUser.full_name[0] || "?");

            const html = `
                <div class="conversation-item ${isActive} ${unreadClass}" id="conv-${c.id}">
                    <div class="avatar-wrapper">
                        <div class="avatar" style="${otherUser.avatar_url ? 'padding:0; overflow:hidden;' : ''}">${avatarHtml}</div>
                        <div class="online-indicator"></div>
                    </div>
                    <div class="conversation-info">
                        <div class="conv-top">
                            <span class="conv-name">${otherUser.full_name}</span>
                            <span class="conv-time">${time}</span>
                        </div>
                        <div class="conv-bottom">
                            <span class="conv-preview">${lastMsg}</span>
                            ${unreadBadge}
                        </div>
                    </div>
                </div>
            `;

            const temp = document.createElement('div');
            temp.innerHTML = html.trim();
            const el = temp.firstChild;
            el.addEventListener("click", () => selectConversation(c));
            els.conversationList.appendChild(el);
        });
    }

    function renderMessages(originalMessages) {
        const atBottom = isAtBottom();
        els.messagesContainer.innerHTML = "";
        // Ordenar mensajes cronológicamente
        const messages = [...originalMessages].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

        messages.forEach(msg => {
            const isMine = Number(msg.sender_id) === Number(state.user.id);
            const time = formatTime(msg.created_at);

            const div = document.createElement("div");
            div.className = `message-row ${isMine ? "sent" : "received"}`;
            div.innerHTML = `
                <div class="message-bubble">
                    ${escapeHtml(msg.content)}
                    <span class="message-meta">${time}</span>
                </div>
            `;
            els.messagesContainer.appendChild(div);
        });

        // Auto-scroll si el usuario estaba al final o en carga inicial
        if (atBottom || messages.length > 0) {
            scrollToBottom();
        }
    }

    function appendMessage(msg) {
        const isMine = Number(msg.sender_id) === Number(state.user.id);
        const time = formatTime(msg.created_at);
        const div = document.createElement("div");
        div.className = `message-row ${isMine ? "sent" : "received"}`;
        div.innerHTML = `
            <div class="message-bubble">
                ${escapeHtml(msg.content)}
                <span class="message-meta">${time}</span>
            </div>
        `;
        els.messagesContainer.appendChild(div);
        scrollToBottom();
    }

    // --- Funciones de Utilidad (Helpers) ---

    function formatTime(isoString) {
        const date = new Date(isoString);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    function scrollToBottom() {
        els.messagesContainer.scrollTop = els.messagesContainer.scrollHeight;
    }

    function isAtBottom() {
        const threshold = 100;
        return els.messagesContainer.scrollHeight - els.messagesContainer.scrollTop - els.messagesContainer.clientHeight < threshold;
    }

    function autoResizeTextarea(element) {
        element.style.height = "auto";
        element.style.height = element.scrollHeight + "px";
    }

    function escapeHtml(text) {
        if (!text) return "";
        return text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    // Iniciar el script
    init();
});
