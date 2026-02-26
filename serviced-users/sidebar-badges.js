(function () {
    const API_BASE_URL = "/api/v1";
    const token = sessionStorage.getItem("serviced_token");
    if (!token) return;

    async function updateBadges() {
        try {
            const response = await fetch(`${API_BASE_URL}/dashboard/summary`, {
                headers: { "Authorization": "Bearer " + token }
            });
            if (!response.ok) return;
            const data = await response.json();

            const notifBadge = document.getElementById('notif-badge');
            const msgBadge = document.getElementById('msg-badge');

            if (notifBadge) {
                if (data.unread_notifications_count > 0) {
                    notifBadge.textContent = data.unread_notifications_count > 99 ? '99+' : data.unread_notifications_count;
                    notifBadge.style.display = 'flex';
                } else {
                    notifBadge.style.display = 'none';
                }
            }

            if (msgBadge) {
                const msgLink = msgBadge.closest('.nav-item');
                if (data.unread_messages_count > 0) {
                    msgBadge.textContent = data.unread_messages_count > 99 ? '99+' : data.unread_messages_count;
                    msgBadge.style.display = 'flex';
                    if (msgLink) msgLink.classList.add('pulse-alert');
                } else {
                    msgBadge.style.display = 'none';
                    if (msgLink) msgLink.classList.remove('pulse-alert');
                }
            }
        } catch (error) {
            // Silently fail to not disturb user experience
        }
    }

    // Initial update
    updateBadges();
    // Poll every 60 seconds
    setInterval(updateBadges, 60000);

    // Listen for custom events if needed (e.g. after marking as read)
    window.addEventListener('notificationsUpdated', updateBadges);
    window.addEventListener('messagesUpdated', updateBadges);
})();
