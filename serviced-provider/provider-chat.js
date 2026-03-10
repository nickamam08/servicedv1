/**
 * Lógica del Chat para Proveedores de SERVICED
 * Gestiona la mensajería en tiempo real, administración de conversaciones y actualizaciones de la interfaz para profesionales.
 */

document.addEventListener("DOMContentLoaded", () => {
    // --- Constantes de Configuración ---
    const API_BASE_URL = "/api/v1";
    const POLLING_INTERVAL = 3000; // 3 segundos para el refresco de mensajes

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
            window.location.href = "../serviced-users/login.html";
            return;
        }

        // Configuración de Cierre de Sesión
        if (els.logoutLink) {
            els.logoutLink.addEventListener("click", (e) => {
                e.preventDefault();
                sessionStorage.clear();
                window.location.href = "../serviced-users/login.html";
            });
        }

        // Manejar parámetros de URL (ej: abrir chat directamente desde una solicitud)
        handleUrlParams();

        // Carga inicial de conversaciones
        fetchConversations();

        // Polling: Actualizar lista lateral cada 10s
        setInterval(fetchConversations, 10000);

        // Configurar escuchadores de eventos
        setupEventListeners();
    }

    function setupEventListeners() {
        // Enviar mensaje al hacer clic
        els.sendBtn.addEventListener("click", sendMessage);

        // Enviar al presionar Enter
        els.messageInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Gestión de estado del botón y altura del área de texto
        els.messageInput.addEventListener("input", () => {
            els.sendBtn.disabled = els.messageInput.value.trim().length === 0;
            autoResizeTextarea(els.messageInput);
        });

        // Búsqueda de clientes en la lista
        els.searchInput.addEventListener("input", (e) => {
            renderConversationList(state.conversations, e.target.value);
        });

        // Volver atrás (Vista móvil)
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
                    window.location.href = "../serviced-users/login.html";
                }
                return;
            }

            const data = await resp.json();
            // Ordenar por actividad más reciente
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
            if (!resp.ok) throw new Error("Fallo al cargar mensajes");
            const messages = await resp.json();
            renderMessages(messages);
            markAsRead(conversationId);
        } catch (e) {
            console.error("Error al cargar mensajes:", e);
        }
    }

    async function markAsRead(conversationId) {
        try {
            await fetch(`${API_BASE_URL}/conversations/${conversationId}/read`, {
                method: "PUT",
                headers: { "Authorization": `Bearer ${state.token}` }
            });
            // Despachar evento para que otros componentes (ej: badges) se actualicen
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

            if (!resp.ok) throw new Error("Error al enviar mensaje");

            const msg = await resp.json();

            // Reflejo inmediato en la interfaz
            appendMessage(msg);

            // Limpieza y reseteo
            els.messageInput.value = "";
            els.messageInput.style.height = 'auto';

            // Actualizar lista para mover la conversación arriba
            fetchConversations();

        } catch (e) {
            console.error(e);
            alert("Error al enviar el mensaje");
        } finally {
            state.isSending = false;
        }
    }

    async function createConversation(userId) {
        try {
            const resp = await fetch(`${API_BASE_URL}/conversations`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${state.token}`
                },
                body: JSON.stringify({ client_id: parseInt(userId) })
            });

            if (resp.ok) {
                const conv = await resp.json();
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
            alert("Error de conexión al iniciar chat");
        }
    }

    // --- Lógica Central ---

    async function handleUrlParams() {
        const params = new URLSearchParams(window.location.search);
        const userId = params.get("userId");
        const convId = params.get("id");

        // Si se pasa un userId, intentar abrir/crear conversación con ese cliente
        if (userId) {
            await createConversation(userId);
        } else if (convId) {
            // Lógica para abrir una conversación específica por ID (si está en la lista)
        }
    }

    function selectConversation(conv) {
        if (state.currentConversationId === conv.id) return;

        state.currentConversationId = conv.id;

        // Actualizar UI: resaltar ítem seleccionado
        document.querySelectorAll(".conversation-item").forEach(el => el.classList.remove("active"));
        const activeItem = document.getElementById(`conv-${conv.id}`);
        if (activeItem) activeItem.classList.add("active");

        // Preparar área de mensajes
        els.emptyState.style.display = "none";
        els.messagesContainer.style.display = "flex";
        els.inputArea.style.display = "block";
        els.chatHeader.style.visibility = "visible";
        els.chatContainer.classList.add("chat-open");

        // Cargar datos del remitente en el encabezado
        const otherUser = conv.participant || { full_name: "Usuario", avatar_initials: "?" };
        els.headerName.textContent = otherUser.full_name;

        if (otherUser.avatar_url) {
            els.headerAvatar.innerHTML = `<img src="${otherUser.avatar_url}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">`;
            els.headerAvatar.style.padding = "0";
            els.headerAvatar.style.overflow = "hidden";
        } else {
            els.headerAvatar.textContent = otherUser.avatar_initials || otherUser.full_name[0] || "?";
            els.headerAvatar.style.padding = "";
        }

        // Carga inicial de mensajes del chat seleccionado
        els.messagesContainer.innerHTML = `<div style="text-align:center; padding:20px;">Cargando historial...</div>`;
        fetchMessages(conv.id);

        // Refresco automático de mensajes (Polling corto cada 3s)
        if (state.pollingTimer) clearInterval(state.pollingTimer);
        state.pollingTimer = setInterval(() => {
            if (state.currentConversationId === conv.id) fetchMessages(conv.id);
        }, POLLING_INTERVAL);
    }

    // --- Funciones de Renderizado ---

    function renderConversationList(list, filterText = "") {
        els.conversationList.innerHTML = "";

        const filtered = list.filter(c => {
            const name = c.participant?.full_name || "Usuario";
            return name.toLowerCase().includes(filterText.toLowerCase());
        });

        if (filtered.length === 0) {
            els.conversationList.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-light);">No hay conversaciones que coincidan.</div>`;
            return;
        }

        filtered.forEach(c => {
            const otherUser = c.participant || { full_name: "Usuario", avatar_initials: "?" };
            const lastMsg = c.last_message ? c.last_message.content : "Sin mensajes aún";
            const time = c.last_message ? formatTime(c.last_message.created_at) : "";
            const isActive = c.id === state.currentConversationId ? "active" : "";

            let unreadBadge = "";
            let unreadClass = "";
            // Heurística de mensaje no leído (recibido y no marcado como leído)
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

        // Asegurar que bajamos el scroll para ver los últimos mensajes
        if (atBottom || true) {
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

    // --- Utilidades ---

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

    // Iniciar aplicación
    init();
});
