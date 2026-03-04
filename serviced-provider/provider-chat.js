/**
 * SERVICED Provider Chat Logic
 * Handles real-time messaging, conversation management, and UI updates.
 */

document.addEventListener("DOMContentLoaded", () => {
    // --- Constants ---
    const API_BASE_URL = "/api/v1";
    const POLLING_INTERVAL = 3000; // 3 seconds

    // --- State ---
    let state = {
        token: sessionStorage.getItem("serviced_token"),
        user: JSON.parse(sessionStorage.getItem("serviced_user") || "null"),
        conversations: [],
        currentConversationId: null,
        pollingTimer: null,
        isSending: false
    };

    // --- DOM Elements ---
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

    // --- Initialization ---
    function init() {
        if (!state.token || !state.user) {
            window.location.href = "../serviced-users/login.html";
            return;
        }

        // Setup Logout
        if (els.logoutLink) {
            els.logoutLink.addEventListener("click", (e) => {
                e.preventDefault();
                sessionStorage.clear();
                window.location.href = "../serviced-users/login.html";
            });
        }

        // Check for URL params (auto-open logic)
        handleUrlParams();

        // Initial Fetch
        fetchConversations();

        // Start Polling
        setInterval(fetchConversations, 10000); // Poll list every 10s

        // Event Listeners
        setupEventListeners();
    }

    function setupEventListeners() {
        // Send Message
        els.sendBtn.addEventListener("click", sendMessage);

        // Enter to send
        els.messageInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // Input typing listener
        els.messageInput.addEventListener("input", () => {
            els.sendBtn.disabled = els.messageInput.value.trim().length === 0;
            autoResizeTextarea(els.messageInput);
        });

        // Search
        els.searchInput.addEventListener("input", (e) => {
            renderConversationList(state.conversations, e.target.value);
        });

        // Mobile Back
        els.backBtn.addEventListener("click", () => {
            state.currentConversationId = null;
            els.chatContainer.classList.remove("chat-open");
            clearInterval(state.pollingTimer);
        });
    }

    // --- API Interactions ---

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
            // Sort by updated_at desc
            state.conversations = data.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));

            renderConversationList(state.conversations, els.searchInput.value);

            // Re-select current if open (to update last message snippet in list)
            if (state.currentConversationId) {
                // Determine if we need to update message list too? 
                // We do that via separate polling for active chat
            }

        } catch (e) {
            console.error("Error fetching conversations:", e);
            els.conversationList.innerHTML = `<div style="padding: 20px; text-align: center; color: red;">Error de conexión</div>`;
        }
    }

    async function fetchMessages(conversationId) {
        try {
            const resp = await fetch(`${API_BASE_URL}/conversations/${conversationId}/messages`, {
                headers: { "Authorization": `Bearer ${state.token}` }
            });
            if (!resp.ok) throw new Error("Failed to load messages");
            const messages = await resp.json();
            renderMessages(messages);
            markAsRead(conversationId);
        } catch (e) {
            console.error("Error fetching messages:", e);
        }
    }

    async function markAsRead(conversationId) {
        try {
            await fetch(`${API_BASE_URL}/conversations/${conversationId}/read`, {
                method: "PUT",
                headers: { "Authorization": `Bearer ${state.token}` }
            });
            // Ideally assume success and clear local badges
        } catch (e) {
            console.error("Error marking read:", e);
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

            if (!resp.ok) throw new Error("Failed to send");

            const msg = await resp.json();

            // Append locally immediately
            appendMessage(msg);

            // Clear input
            els.messageInput.value = "";
            els.messageInput.style.height = 'auto'; // Reset height

            // Refresh conversations list to show latest msg
            fetchConversations();

        } catch (e) {
            console.error(e);
            alert("Error al enviar mensaje");
        } finally {
            state.isSending = false;
        }
    }

    async function createConversation(userId) {
        try {
            console.log("Attempting to create/open conversation with user:", userId);
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
                // Add to list and select
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

    // --- Core Logic ---

    async function handleUrlParams() {
        const params = new URLSearchParams(window.location.search);
        const userId = params.get("userId");
        const convId = params.get("id");

        // We need to wait for initial conversation load? 
        // Or we can just try to create/fetch immediately.
        // Let's modify fetchConversations to handle this after loading.

        // Actually, safer to just run logic after fetchConversations resolves first time.
        // Implementing custom logic here based on params.

        if (userId) {
            // Check if we have it already manually or just hit create endpoint which returns existing
            // Best to wait for list? No, just hit create, it handles "return existing"
            await createConversation(userId);
            // URL cleanup?
            // window.history.replaceState({}, document.title, window.location.pathname);
        } else if (convId) {
            // We can select it from list later, or fetch it specifically if pagination implemented
            // For now assume it's in list (small scale)
        }
    }

    function selectConversation(conv) {
        if (state.currentConversationId === conv.id) return;

        state.currentConversationId = conv.id;

        // Update UI state
        // Sidebar active class
        document.querySelectorAll(".conversation-item").forEach(el => el.classList.remove("active"));
        const activeItem = document.getElementById(`conv-${conv.id}`);
        if (activeItem) activeItem.classList.add("active");

        // Show Chat Area
        els.emptyState.style.display = "none";
        els.messagesContainer.style.display = "flex";
        els.inputArea.style.display = "block";
        els.chatHeader.style.visibility = "visible";
        els.chatContainer.classList.add("chat-open"); // Mobile view

        // Update Header
        const otherUser = conv.participant || { full_name: "Usuario", avatar_initials: "?" };
        els.headerName.textContent = otherUser.full_name;

        if (otherUser.avatar_url) {
            els.headerAvatar.innerHTML = `<img src="${otherUser.avatar_url}" style="width:100%; height:100%; border-radius:50%; object-fit:cover;">`;
            els.headerAvatar.style.padding = "0";
            els.headerAvatar.style.overflow = "hidden";
        } else {
            els.headerAvatar.textContent = otherUser.avatar_initials || otherUser.full_name[0] || "?";
            els.headerAvatar.style.padding = ""; // Reset
        }
        // els.headerStatus.textContent = "En línea"; // Mock

        // Clear & Load Messages
        els.messagesContainer.innerHTML = `<div style="text-align:center; padding:20px;">Cargando mensajes...</div>`;
        fetchMessages(conv.id);

        // Clear old polling
        if (state.pollingTimer) clearInterval(state.pollingTimer);
        state.pollingTimer = setInterval(() => {
            if (state.currentConversationId === conv.id) fetchMessages(conv.id);
        }, 3000); // Poll messages every 3s
    }

    // --- Rendering ---

    function renderConversationList(list, filterText = "") {
        els.conversationList.innerHTML = "";

        const filtered = list.filter(c => {
            const name = c.participant?.full_name || "Usuario";
            return name.toLowerCase().includes(filterText.toLowerCase());
        });

        if (filtered.length === 0) {
            els.conversationList.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-light);">No se encontraron conversaciones.</div>`;
            return;
        }

        filtered.forEach(c => {
            const otherUser = c.participant || { full_name: "Usuario", avatar_initials: "?" };
            const lastMsg = c.last_message ? c.last_message.content : "Sin mensajes";
            const time = c.last_message ? formatTime(c.last_message.created_at) : "";
            const isActive = c.id === state.currentConversationId ? "active" : "";
            const isUnread = false; // Need logic. Backend 'is_read' is on message level. 
            // We can check if last message is received & unread, OR backend provides unread_count.
            // Current backend schema DOES NOT provide unread_count per conversation.
            // We'll skip unread badge for now or implement client side heuristic if possible.
            // Heuristic: last_message.is_read === false && sender_id !== me

            let unreadBadge = "";
            let unreadClass = "";
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

            // Create element to attach event (avoiding innerHTML string parsing issues for events)
            const temp = document.createElement('div');
            temp.innerHTML = html.trim();
            const el = temp.firstChild;
            el.addEventListener("click", () => selectConversation(c));
            els.conversationList.appendChild(el);
        });
    }

    function renderMessages(originalMessages) {
        // Only update if changed or first load.
        // For simplicity, re-render all (inefficient but safe).
        // Optimization: Check last ID.

        // Sort asc
        /*
        const messages = [...originalMessages].sort((a,b) => new Date(a.created_at) - new Date(b.created_at));
        
        // Naive render:
        els.messagesContainer.innerHTML = "";
        messages.forEach(msg => appendMessage(msg, false));
        scrollToBottom();
        */

        // Smarter Render: Maintain scroll position if not at bottom? 
        // For now, simple wipe and render.
        const atBottom = isAtBottom();

        els.messagesContainer.innerHTML = "";
        // Sort asc
        const messages = [...originalMessages].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

        // Group by day? (Extra requirement: date separators)

        messages.forEach(msg => {
            const isMine = Number(msg.sender_id) === Number(state.user.id);
            console.log(`Msg: ${msg.id}, Sender: ${msg.sender_id} (${typeof msg.sender_id}), Me: ${state.user.id} (${typeof state.user.id}), IsMine: ${isMine}`);
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

        if (atBottom || true) { // Always scroll to bottom on new messages for chat app feel
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

    // --- Helpers ---

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

    // Start
    init();
});
