/**
 * SERVICED Dark Mode Logic
 * Handles theme switching, persistence, and system preference detection.
 */

(function () {
    const theme = localStorage.getItem('serviced_theme');
    const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;

    // Apply theme immediately to prevent flash
    if (theme === 'dark' || (!theme && systemPrefersDark)) {
        document.documentElement.classList.add('dark-mode');
    }

    document.addEventListener('DOMContentLoaded', () => {
        const toggleBtn = document.getElementById('theme-toggle');
        if (!toggleBtn) return;

        // Update icon on load
        updateToggleIcon(document.documentElement.classList.contains('dark-mode'));

        toggleBtn.addEventListener('click', () => {
            const isDark = document.documentElement.classList.toggle('dark-mode');
            localStorage.setItem('serviced_theme', isDark ? 'dark' : 'light');
            updateToggleIcon(isDark);
        });

        function updateToggleIcon(isDark) {
            toggleBtn.innerHTML = isDark ? '☀️' : '🌙';
            toggleBtn.title = isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro';
        }
    });

    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem('serviced_theme')) {
            if (e.matches) {
                document.documentElement.classList.add('dark-mode');
            } else {
                document.documentElement.classList.remove('dark-mode');
            }
        }
    });
})();
