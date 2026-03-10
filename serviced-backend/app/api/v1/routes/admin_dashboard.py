from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_db
from app.dependencies.deps import require_admin
from app.models import User
from app.schemas.admin_dashboard import PlatformStats
from app.schemas.admin_category import CategoryCreate, CategoryUpdate, CategoryOut
from app.schemas.user import UserResponse
from app.schemas.provider import ProviderResponse
from app.schemas.service import ServiceResponse, ServiceRequestResponse
from app.schemas.review import ReviewResponse
from app.schemas.chat import ConversationResponse, ConversationWithMessages
from app.schemas.report import ReportResponse, ReportUpdate

from app.services import (
    admin_dashboard_service, admin_user_service, admin_provider_service,
    admin_service_service, admin_request_service, admin_review_service,
    admin_category_service, chat as chat_service_mod
)
from app.services.report_service import report_service

router = APIRouter()

# 1. Resumen Global de la Plataforma
@router.get("/overview", response_model=PlatformStats)
def get_overview(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Obtiene estadísticas generales de usuarios, proveedores, servicios y solicitudes."""
    return admin_dashboard_service.get_platform_stats(db)

# 2. Gestión de Usuarios (Clientes y Proveedores)
@router.get("/users", response_model=List[UserResponse])
def get_users(
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Lista todos los usuarios con filtros por rol, estado activo y búsqueda por nombre/email."""
    return admin_user_service.get_all_users(db, role=role, is_active=is_active, search=search)

@router.get("/users/{id}", response_model=UserResponse)
def get_user_detail(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Obtiene el detalle de un usuario específico."""
    user = admin_user_service.get_user_by_id(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.put("/users/{id}/activate", response_model=UserResponse)
def activate_user(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Reactiva la cuenta de un usuario previamente desactivado."""
    user = admin_user_service.activate_user(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.put("/users/{id}/deactivate", response_model=UserResponse)
def deactivate_user(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Desactiva la cuenta de un usuario (bloqueo de acceso)."""
    user = admin_user_service.deactivate_user(db, id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.delete("/users/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Elimina permanentemente a un usuario y sus registros asociados."""
    success = admin_user_service.delete_user(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return None

# 3. Gestión de Proveedores (Verificación)
@router.get("/providers", response_model=List[ProviderResponse])
def get_providers(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Lista todos los perfiles profesionales de proveedores."""
    return admin_provider_service.get_all_providers(db)

@router.put("/providers/{id}/verify", response_model=ProviderResponse)
def verify_provider(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Otorga el sello de verificación a un proveedor tras revisar sus datos."""
    provider = admin_provider_service.verify_provider(db, id)
    if not provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return provider

@router.put("/providers/{id}/unverify", response_model=ProviderResponse)
def unverify_provider(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Retira el sello de verificación de un proveedor."""
    provider = admin_provider_service.unverify_provider(db, id)
    if not provider:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return provider

# 4. Gestión de Servicios Publicados
@router.get("/services", response_model=List[ServiceResponse])
def get_services(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    provider_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Supervisa todos los servicios ofrecidos en la plataforma con filtros avanzados."""
    return admin_service_service.get_all_services(
        db, category=category, is_active=is_active, provider_id=provider_id, search=search
    )

@router.put("/services/{id}/activate", response_model=ServiceResponse)
def activate_service(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Vuelve a habilitar un servicio para que sea visible por clientes."""
    service = admin_service_service.activate_service(db, id)
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return service

@router.put("/services/{id}/deactivate", response_model=ServiceResponse)
def deactivate_service(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Oculta un servicio de la plataforma (ej: por infringir normas)."""
    service = admin_service_service.deactivate_service(db, id)
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return service

@router.delete("/services/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_service(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Elimina un servicio de manera definitiva."""
    success = admin_service_service.delete_service(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    return None

# 5. Supervisión de Solicitudes y Contrataciones
@router.get("/requests") 
def get_requests(
    status: Optional[str] = None,
    provider_id: Optional[int] = None,
    client_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Lista histórica y actual de todas las solicitudes de servicios entre usuarios."""
    return admin_request_service.get_all_requests(
        db, status=status, provider_id=provider_id, client_id=client_id, 
        date_from=date_from, date_to=date_to
    )

@router.put("/requests/{id}/cancel", response_model=ServiceRequestResponse)
def cancel_request(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Intervención administrativa para cancelar una solicitud pendiente o activa."""
    request = admin_request_service.cancel_request(db, id)
    if not request:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    return request

# 6. Moderación de Reseñas
@router.get("/reviews", response_model=List[ReviewResponse])
def get_reviews(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Recupera todas las valoraciones y comentarios realizados por clientes."""
    return admin_review_service.get_all_reviews(db)

@router.delete("/reviews/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Elimina una reseña (ej: por lenguaje inapropiado)."""
    success = admin_review_service.delete_review(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")
    return None

# 7. Auditoría de Conversaciones (Solo lectura para soporte/seguridad)
@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Permite al administrador auditar hilos de chat entre usuarios."""
    from app.models.all_models import ChatConversation
    return db.query(ChatConversation).all()

@router.get("/conversations/{id}", response_model=ConversationWithMessages)
def get_conversation_detail(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Muestra el historial completo de mensajes de un chat específico."""
    from app.models.all_models import ChatConversation
    conversation = db.query(ChatConversation).filter(ChatConversation.id == id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversación no encontrada")
    return conversation

# 8. Gestión de Categorías de la Plataforma
@router.get("/categories", response_model=List[CategoryOut])
def get_categories(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Lista las categorías oficiales (ej: Limpieza, Reparaciones)."""
    return admin_category_service.get_all_categories(db)

@router.post("/categories", response_model=CategoryOut)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Añade una nueva categoría de servicios al catálogo."""
    return admin_category_service.create_category(db, category_in)

@router.put("/categories/{id}", response_model=CategoryOut)
def update_category(
    id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Modifica el nombre o estado de una categoría existente."""
    category = admin_category_service.update_category(db, id, category_in)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category

@router.delete("/categories/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    id: int,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Elimina una categoría del sistema."""
    success = admin_category_service.delete_category(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return None

# 9. Administración y Resolución de Reportes (Bugs o Denuncias)
@router.get("/reports", response_model=List[ReportResponse])
def get_reports(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Lista los reportes enviados por usuarios, filtrados por estado o prioridad."""
    return report_service.get_all_reports(db, status=status, priority=priority)

@router.put("/reports/{id}", response_model=ReportResponse)
def update_report(
    id: int,
    report_in: ReportUpdate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    """Actualiza el estado, prioridad o resolución de un reporte administrativo."""
    report = report_service.update_report(db, id, report_in)
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return report
