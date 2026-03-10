from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, timedelta
from app.models.all_models import (
    User, ProviderProfile, Service, ServiceRequest, 
    Review, ChatConversation, ChatMessage, Category, 
    UserRole, RequestStatus
)

class AdminRepository:
    """
    Repositorio especializado en consultas globales y estadísticas para el panel de Administración.
    """
    def fetch_all_users(
        self, db: Session, *, role: Optional[str] = None, is_active: Optional[bool] = None, search: Optional[str] = None
    ) -> List[User]:
        """
        Obtiene la lista de usuarios con filtros opcionales por rol, estado de actividad y búsqueda por nombre/email.
        """
        query = db.query(User)
        if role:
            query = query.filter(User.role == role)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        if search:
            query = query.filter(
                (User.full_name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
            )
        return query.all()

    def fetch_all_providers(self, db: Session) -> List[ProviderProfile]:
        """
        Obtiene todos los perfiles de proveedores registrados.
        """
        return db.query(ProviderProfile).all()

    def fetch_all_services(
        self, db: Session, *, category: Optional[str] = None, is_active: Optional[bool] = None, 
        provider_id: Optional[int] = None, search: Optional[str] = None
    ) -> List[Service]:
        """
        Obtiene todos los servicios de la plataforma con filtros por categoría, estado, proveedor y búsqueda textual.
        """
        query = db.query(Service)
        if category:
            query = query.filter(Service.category == category)
        if is_active is not None:
            query = query.filter(Service.is_active == is_active)
        if provider_id:
            query = query.filter(Service.provider_id == provider_id)
        if search:
            query = query.filter(
                (Service.title.ilike(f"%{search}%")) | (Service.description.ilike(f"%{search}%"))
            )
        return query.all()

    def fetch_all_requests(
        self, db: Session, *, status: Optional[str] = None, provider_id: Optional[int] = None, 
        client_id: Optional[int] = None, date_from: Optional[datetime] = None, date_to: Optional[datetime] = None
    ) -> List[ServiceRequest]:
        """
        Obtiene todas las solicitudes de servicio con filtros detallados por estado, participantes y rango de fechas.
        """
        query = db.query(ServiceRequest)
        if status:
            query = query.filter(ServiceRequest.status == status)
        if provider_id:
            # Requiere JOIN con Service para filtrar por el proveedor que ofrece el servicio
            query = query.join(Service).filter(Service.provider_id == provider_id)
        if client_id:
            query = query.filter(ServiceRequest.client_id == client_id)
        if date_from:
            query = query.filter(ServiceRequest.created_at >= date_from)
        if date_to:
            query = query.filter(ServiceRequest.created_at <= date_to)
        return query.all()

    def fetch_all_reviews(self, db: Session) -> List[Review]:
        """
        Obtiene todas las reseñas de la plataforma, de la más reciente a la más antigua.
        """
        return db.query(Review).order_by(Review.created_at.desc()).all()

    def fetch_platform_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Calcula y retorna estadísticas globales clave del rendimiento de la plataforma.
        """
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        total_users = db.query(func.count(User.id)).filter(User.role == UserRole.CLIENT).scalar() or 0
        total_providers = db.query(func.count(User.id)).filter(User.role == UserRole.PROVIDER).scalar() or 0
        total_services = db.query(func.count(Service.id)).scalar() or 0
        total_requests = db.query(func.count(ServiceRequest.id)).scalar() or 0
        total_completed_requests = db.query(func.count(ServiceRequest.id)).filter(ServiceRequest.status == RequestStatus.COMPLETED).scalar() or 0
        total_cancelled_requests = db.query(func.count(ServiceRequest.id)).filter(ServiceRequest.status == RequestStatus.CANCELLED).scalar() or 0
        total_reviews = db.query(func.count(Review.id)).scalar() or 0
        average_platform_rating = db.query(func.avg(Review.rating)).scalar() or 0.0
        
        new_users_last_30_days = db.query(func.count(User.id)).filter(User.created_at >= thirty_days_ago).scalar() or 0
        new_requests_last_30_days = db.query(func.count(ServiceRequest.id)).filter(ServiceRequest.created_at >= thirty_days_ago).scalar() or 0
        
        return {
            "total_users": total_users,
            "total_providers": total_providers,
            "total_services": total_services,
            "total_requests": total_requests,
            "total_completed_requests": total_completed_requests,
            "total_cancelled_requests": total_cancelled_requests,
            "total_reviews": total_reviews,
            "average_platform_rating": float(average_platform_rating),
            "new_users_last_30_days": new_users_last_30_days,
            "new_requests_last_30_days": new_requests_last_30_days
        }

    def fetch_all_categories(self, db: Session) -> List[Category]:
        """
        Obtiene la lista completa de categorías de servicios.
        """
        return db.query(Category).all()

# Instancia global del repositorio administrativo
admin_repo = AdminRepository()
