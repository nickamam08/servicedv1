/**
 * Admin Services Moderation Logic - Enhanced
 */

let allServices = [];

document.addEventListener('DOMContentLoaded', () => {
    loadServices();
    setupFilters();
});

async function loadServices() {
    try {
        const search = document.getElementById('search-input')?.value || '';
        const status = document.getElementById('status-filter')?.value || 'all';
        const sort = document.getElementById('sort-filter')?.value || 'newest';

        console.log('Loading services with filters:', { search, status, sort });

        let queryParams = [];
        if (search) queryParams.push(`search=${encodeURIComponent(search)}`);
        if (status !== 'all') queryParams.push(`is_active=${status === 'active'}`);

        const queryString = queryParams.length > 0 ? `?${queryParams.join('&')}` : '';
        const services = await apiFetch(`/admin/dashboard/services${queryString}`);

        if (!services) return;

        allServices = services;
        applyLocalSorting(sort);
        displayServices(allServices);
        updateStats(allServices);
    } catch (error) {
        console.error('Error loading services:', error);
    }
}

function applyLocalSorting(criteria) {
    switch (criteria) {
        case 'price_asc':
            allServices.sort((a, b) => a.price - b.price);
            break;
        case 'price_desc':
            allServices.sort((a, b) => b.price - a.price);
            break;
        case 'rating_desc':
            allServices.sort((a, b) => b.rating - a.rating);
            break;
        case 'newest':
        default:
            allServices.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
            break;
    }
}

function displayServices(services) {
    const container = document.getElementById('services-container');
    if (!container) return;

    container.innerHTML = '';

    if (services.length === 0) {
        container.innerHTML = '<div class="bento-card" style="grid-column: span 12; text-align: center; padding: 40px; color: var(--text-secondary);">No se encontraron servicios que coincidan con los criterios.</div>';
        return;
    }

    services.forEach(service => {
        const card = document.createElement('div');
        card.className = 'bento-card service-card';
        card.style.cssText = 'grid-column: span 4; padding: 0; overflow: hidden; display: flex; flex-direction: column; transition: transform 0.2s; cursor: default;';

        const imgUrl = (service.image_urls && service.image_urls.length > 0)
            ? service.image_urls[0]
            : 'https://via.placeholder.com/300x160?text=Serviced';

        card.innerHTML = `
            <div style="height: 160px; background: #f3f4f6; overflow: hidden; position: relative; cursor: pointer;" onclick="viewServiceDetails(${service.id})">
                <img src="${imgUrl}" alt="${service.title}" style="width: 100%; height: 100%; object-fit: cover;">
                <div style="position: absolute; top: 12px; right: 12px;">
                    <span class="badge ${service.is_active ? 'badge-success' : 'badge-danger'}" style="box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);">
                        ${service.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                </div>
            </div>
            <div style="padding: 20px; flex: 1; display: flex; flex-direction: column;">
                <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px;">
                    <h3 class="text-h3" style="font-size: 1.1rem; margin-bottom: 0; line-height: 1.3; cursor: pointer; flex: 1;" onclick="viewServiceDetails(${service.id})">${service.title}</h3>
                    <span style="font-weight: 700; color: var(--primary); font-size: 1.1rem; margin-left: 12px;">
                        $${service.price.toLocaleString('es-CO')}
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
                    <span style="color: #fbbf24; font-size: 0.9rem;">⭐ ${service.rating.toFixed(1)}</span>
                    <span style="color: var(--text-secondary); font-size: 0.8rem;">• ${service.category || 'Sin categoría'}</span>
                </div>
                
                <p class="text-sm" style="color: var(--text-secondary); margin-bottom: 16px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; height: 2.8em;">
                    ${service.description || 'Sin descripción disponible.'}
                </p>

                <div style="margin-top: auto; display: flex; gap: 8px;">
                    <button class="btn ${service.is_active ? 'btn-outline' : 'btn-primary'}" 
                            style="flex: 1; font-size: 0.85rem; padding: 8px; ${service.is_active ? 'color: var(--danger); border-color: var(--danger);' : ''}"
                            onclick="toggleServiceStatus(${service.id}, ${service.is_active})">
                        ${service.is_active ? 'Desactivar' : 'Activar'}
                    </button>
                    <button class="btn btn-outline" style="padding: 8px; font-size: 0.85rem;" onclick="deleteService(${service.id})" title="Eliminar Permanentemente">🗑️</button>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

async function viewServiceDetails(serviceId) {
    const service = allServices.find(s => s.id === serviceId);
    if (!service) return;

    const modal = document.getElementById('service-modal');
    const content = document.getElementById('modal-content');

    content.innerHTML = `
        <div style="display: flex; gap: 32px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 300px;">
                <img src="${(service.image_urls && service.image_urls.length > 0) ? service.image_urls[0] : 'https://via.placeholder.com/600x400'}" 
                     style="width: 100%; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);">
                
                <div style="margin-top: 24px; padding: 20px; background: #f9fafb; border-radius: 12px; border: 1px solid var(--border);">
                    <h4 style="margin-bottom: 12px; font-size: 1rem;">Detalles del Proveedor</h4>
                    <p style="font-size: 0.9rem; margin-bottom: 8px;">ID Proveedor: <strong>#${service.provider_id}</strong></p>
                    <p style="font-size: 0.9rem; margin-bottom: 8px;">Nombre: <strong>${service.provider_name || 'Desconocido'}</strong></p>
                    <button class="btn btn-outline" style="width: 100%; margin-top: 12px; font-size: 0.85rem;">Ver Perfil del Proveedor</button>
                </div>
            </div>
            
            <div style="flex: 1.5; min-width: 300px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <span class="badge ${service.is_active ? 'badge-success' : 'badge-danger'}">${service.is_active ? 'Servicio Activo' : 'Servicio Inactivo'}</span>
                    <span style="font-size: 0.85rem; color: var(--text-secondary);">Publicado: ${new Date(service.created_at).toLocaleDateString()}</span>
                </div>
                
                <h2 class="text-h2" style="margin-bottom: 8px;">${service.title}</h2>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
                    <span style="font-size: 1.5rem; font-weight: 700; color: var(--primary);">$${service.price.toLocaleString('es-CO')}</span>
                    <span style="color: #fbbf24; font-size: 1.1rem;">⭐ ${service.rating.toFixed(1)}</span>
                    <span style="padding: 4px 12px; background: #eff6ff; color: #1e40af; border-radius: 20px; font-size: 0.8rem; font-weight: 600;">${service.category}</span>
                </div>

                <div style="margin-bottom: 32px;">
                    <h4 style="margin-bottom: 12px; font-size: 1rem; border-bottom: 1px solid var(--border); padding-bottom: 8px;">Descripción</h4>
                    <p style="line-height: 1.6; color: var(--text-secondary);">${service.description || 'No hay descripción detallada para este servicio.'}</p>
                </div>

                <div style="display: flex; gap: 12px;">
                    <button class="btn ${service.is_active ? 'btn-outline' : 'btn-primary'}" 
                            style="flex: 1; ${service.is_active ? 'color: var(--danger); border-color: var(--danger);' : ''}"
                            onclick="toggleServiceStatus(${service.id}, ${service.is_active})">
                        ${service.is_active ? 'Desactivar Servicio' : 'Activar Servicio'}
                    </button>
                    <button class="btn btn-danger" onclick="deleteService(${service.id})">Eliminar Permanente</button>
                </div>
            </div>
        </div>
    `;

    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('service-modal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function (event) {
    const modal = document.getElementById('service-modal');
    if (event.target == modal) {
        closeModal();
    }
}

async function toggleServiceStatus(serviceId, currentStatus) {
    try {
        const action = currentStatus ? 'deactivate' : 'activate';
        const confirmChange = confirm(`¿Estás seguro de que deseas ${action === 'activate' ? 'activar' : 'desactivar'} este servicio?`);
        if (!confirmChange) return;

        await apiFetch(`/admin/dashboard/services/${serviceId}/${action}`, { method: 'PUT' });
        closeModal();
        loadServices();
    } catch (error) {
        alert('Error: ' + error.message);
    }
}

async function deleteService(serviceId) {
    try {
        const confirmDelete = confirm('¡ADVERTENCIA CRÍTICA! Esta acción eliminará el servicio y TODO su historial asociado (solicitudes, pedidos y chats) de forma permanente. No se puede deshacer.\n\n¿Deseas eliminarlo definitivamente?');
        if (!confirmDelete) return;

        console.log(`Attempting to delete service ${serviceId}...`);
        const response = await apiFetch(`/admin/dashboard/services/${serviceId}`, { method: 'DELETE' });

        // apiFetch handles 200-299. If it returns, it was successful.
        closeModal();
        loadServices();
        alert('Servicio eliminado exitosamente.');
    } catch (error) {
        console.error('Error deleting service:', error);
        alert('No se pudo eliminar el servicio: ' + error.message);
    }
}

function updateStats(services) {
    const totalCount = document.getElementById('total-services-count');
    const activeCount = document.getElementById('active-services-count');
    const inactiveCount = document.getElementById('inactive-services-count');

    if (totalCount) totalCount.textContent = services.length.toLocaleString();
    if (activeCount) activeCount.textContent = services.filter(s => s.is_active).length.toLocaleString();
    if (inactiveCount) inactiveCount.textContent = services.filter(s => !s.is_active).length.toLocaleString();
}

function setupFilters() {
    const searchInput = document.getElementById('search-input');
    const statusFilter = document.getElementById('status-filter');
    const sortFilter = document.getElementById('sort-filter');

    if (searchInput) {
        searchInput.addEventListener('input', debounce(() => loadServices(), 300));
    }
    if (statusFilter) {
        statusFilter.addEventListener('change', () => loadServices());
    }
    if (sortFilter) {
        sortFilter.addEventListener('change', () => {
            applyLocalSorting(sortFilter.value);
            displayServices(allServices);
        });
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
