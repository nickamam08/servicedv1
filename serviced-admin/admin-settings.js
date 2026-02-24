/**
 * Admin Settings Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    loadAdminProfile();
    setupSettingsForm();
});

function loadAdminProfile() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    const emailInput = document.querySelector('input[type="email"]');

    // In a real app we'd fetch settings from a /settings endpoint
    // For now we'll just show the logged in user's email if possible
    if (emailInput && user.email) {
        emailInput.value = user.email;
    }
}

function setupSettingsForm() {
    const saveButtons = document.querySelectorAll('.btn-primary');
    saveButtons.forEach(btn => {
        if (btn.textContent.includes('Guardar')) {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                alert('Configuración guardada exitosamente (Simulado)');
            });
        }
    });

    // Handle site status toggle
    const siteStatusToggle = document.querySelector('.switch input');
    if (siteStatusToggle) {
        siteStatusToggle.addEventListener('change', () => {
            const status = siteStatusToggle.checked ? 'Activa' : 'En Mantenimiento';
            console.log(`Estado del sitio cambiado a: ${status}`);
        });
    }
}
