(function () {
    /**
     * Lógica para actualizar los globos de notificación (badges) en la barra lateral.
     * Consulta el resumen del dashboard para obtener conteos de mensajes y notificaciones no leídos.
     */
    const API_BASE_URL = "/api/v1";
    const token = sessionStorage.getItem("serviced_token");
    if (!token) return;

    async function updateBadges() {
        try {
            // Solicitar el resumen de actividad del usuario al backend
            const response = await fetch(`${API_BASE_URL}/dashboard/summary`, {
                headers: { "Authorization": "Bearer " + token }
            });
            if (!response.ok) return;
            const data = await response.json();

            const notifBadge = document.getElementById('notif-badge');
            const msgBadge = document.getElementById('msg-badge');

            // Actualizar el contador de notificaciones generales
            if (notifBadge) {
                if (data.unread_notifications_count > 0) {
                    notifBadge.textContent = data.unread_notifications_count > 99 ? '99+' : data.unread_notifications_count;
                    notifBadge.style.display = 'flex';
                } else {
                    notifBadge.style.display = 'none';
                }
            }

            // Actualizar el contador de mensajes de chat pendientes
            if (msgBadge) {
                const msgLink = msgBadge.closest('.nav-item');
                if (data.unread_messages_count > 0) {
                    msgBadge.textContent = data.unread_messages_count > 99 ? '99+' : data.unread_messages_count;
                    msgBadge.style.display = 'flex';
                    // Añadir efecto de pulso si hay mensajes nuevos
                    if (msgLink) msgLink.classList.add('pulse-alert');
                } else {
                    msgBadge.style.display = 'none';
                    if (msgLink) msgLink.classList.remove('pulse-alert');
                }
            }
        } catch (error) {
            // Fallo silencioso para no interrumpir la navegación del usuario
        }
    }

    // Ejecutar actualización inicial al cargar el script
    updateBadges();

    // Polling: Actualizar cada 60 segundos automáticamente
    setInterval(updateBadges, 60000);

    // Escuchar eventos personalizados para actualizaciones inmediatas (ej. al recibir un mensaje por socket o marcar como leído)
    window.addEventListener('notificationsUpdated', updateBadges);
    window.addEventListener('messagesUpdated', updateBadges);
})();
