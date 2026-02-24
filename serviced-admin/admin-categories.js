/**
 * Admin Categories Management Logic - Enhanced
 */

document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    setupCategoryForm();
});

async function loadCategories() {
    try {
        const categories = await apiFetch('/admin/dashboard/categories');
        if (!categories) return;

        displayCategories(categories);
        updateStats(categories);
    } catch (error) {
        console.error('Error loading categories:', error);
    }
}

function displayCategories(categories) {
    const tbody = document.getElementById('categories-table-body');
    if (!tbody) return;

    tbody.innerHTML = '';

    if (categories.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 40px; color: var(--text-secondary);">No hay categorías registradas.</td></tr>';
        return;
    }

    // Sort alphabetically by name
    categories.sort((a, b) => a.name.localeCompare(b.name));

    categories.forEach(cat => {
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid var(--border)';
        tr.innerHTML = `
            <td style="padding: 16px 24px;">
                <div style="font-weight: 600; color: var(--text-primary);">${cat.name}</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">ID: #${cat.id}</div>
            </td>
            <td style="padding: 16px 24px;">
                <span class="badge ${cat.is_active ? 'badge-success' : 'badge-danger'}" style="font-size: 0.75rem;">
                    ${cat.is_active ? 'Activo' : 'Inactivo'}
                </span>
            </td>
            <td style="padding: 16px 24px; color: var(--text-secondary); font-size: 0.85rem;">
                ${new Date(cat.created_at).toLocaleDateString('es-ES', { day: '2-digit', month: 'short', year: 'numeric' })}
            </td>
            <td style="padding: 16px 24px;">
                <div style="display: flex; gap: 12px;">
                    <button class="action-link" style="font-weight: 600;" onclick="editCategory(${cat.id}, '${cat.name}', ${cat.is_active})">Editar</button>
                    <button class="action-link" style="color: var(--danger); font-weight: 600;" onclick="deleteCategory(${cat.id})">Eliminar</button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function updateStats(categories) {
    const countEl = document.getElementById('cat-count');
    if (countEl) {
        countEl.textContent = `${categories.length} categorías en total`;
    }
}

function setupCategoryForm() {
    const form = document.getElementById('category-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const id = document.getElementById('cat-id').value;
        const name = document.getElementById('cat-name').value;
        const is_active = document.getElementById('cat-active').checked;

        try {
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.disabled = true;
            submitBtn.textContent = 'Guardando...';

            if (id) {
                // Update
                await apiFetch(`/admin/dashboard/categories/${id}`, {
                    method: 'PUT',
                    body: JSON.stringify({ name, is_active })
                });
                console.log(`Updated category ${id}`);
            } else {
                // Create
                await apiFetch('/admin/dashboard/categories', {
                    method: 'POST',
                    body: JSON.stringify({ name, is_active })
                });
                console.log('Created new category');
            }

            resetForm();
            loadCategories();

            // Temporary success indicator could be added here if needed
        } catch (error) {
            console.error('Form submission error:', error);
            alert('Error al guardar: ' + error.message);
        } finally {
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Guardar Cambios';
        }
    });

    const cancelBtn = document.getElementById('cancel-edit');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            resetForm();
        });
    }
}

function resetForm() {
    const form = document.getElementById('category-form');
    if (form) form.reset();
    document.getElementById('cat-id').value = '';
    document.getElementById('form-title').textContent = 'Nueva Categoría';
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) submitBtn.textContent = 'Guardar Cambios';
}

function editCategory(id, name, isActive) {
    document.getElementById('cat-id').value = id;
    document.getElementById('cat-name').value = name;
    document.getElementById('cat-active').checked = isActive;
    document.getElementById('form-title').textContent = 'Editar Categoría';

    // Add visual highlight or scroll
    const formPanel = document.getElementById('category-form').parentElement;
    formPanel.style.transition = 'background-color 0.5s';
    formPanel.style.backgroundColor = '#eef2ff';
    setTimeout(() => {
        formPanel.style.backgroundColor = '#f9fafb';
    }, 1000);

    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: 'smooth'
    });
}

async function deleteCategory(id) {
    const confirmDelete = confirm('¿Estás seguro de que deseas eliminar esta categoría permanentemente?\n\nAdvertencia: Si hay servicios activos en esta categoría, es posible que el sistema impida la eliminación por integridad de datos.');
    if (!confirmDelete) return;

    try {
        await apiFetch(`/admin/dashboard/categories/${id}`, { method: 'DELETE' });
        loadCategories();
    } catch (error) {
        console.error('Delete error:', error);
        alert('No se pudo eliminar: ' + error.message);
    }
}
