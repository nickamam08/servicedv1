from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Service, User, ProviderProfile
from app.repositories.service import service as service_repo
from app.schemas.provider_dashboard import ProviderServiceCreate, ProviderServiceUpdate, ProviderServiceResponse

class ProviderServiceManagementService:
    """
    Servicio encargado de la creación, edición y administración de los catálogos de servicios propios de un proveedor.
    """
    def _get_provider_profile(self, db: Session, user_id: int) -> ProviderProfile:
        """
        Método interno para validar que el usuario tiene un perfil de proveedor activo.
        """
        provider = db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()
        if not provider:
            raise HTTPException(status_code=404, detail="Perfil de proveedor no encontrado")
        return provider

    def get_services(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Service]:
        """
        Recupera la lista de servicios creados por el proveedor autenticado.
        """
        provider = self._get_provider_profile(db, user_id)
        return service_repo.get_multi_by_provider(db, provider_id=provider.id, skip=skip, limit=limit)

    def create_service(self, db: Session, user_id: int, obj_in: ProviderServiceCreate) -> Service:
        """
        Crea un nuevo servicio en el catálogo del proveedor, vinculándolo automáticamente a su perfil.
        """
        provider = self._get_provider_profile(db, user_id)
        
        # Preparamos los datos inyectando el ID del perfil del proveedor
        service_data = obj_in.dict()
        service_data["provider_id"] = provider.id
        
        # Instanciamos el modelo Service directamente para mayor control sobre los campos inyectados
        db_obj = Service(**service_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_service(self, db: Session, service_id: int, user_id: int) -> Service:
        """
        Obtiene el detalle de un servicio específico validando que pertenezca al proveedor que lo solicita.
        """
        service = service_repo.get(db, id=service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Servicio no encontrado")
        
        # Validación de auditoría: ¿es este proveedor el dueño del servicio?
        if service.provider.user_id != user_id:
             raise HTTPException(status_code=403, detail="No autorizado para acceder a este servicio")
        return service

    def update_service(self, db: Session, service_id: int, user_id: int, obj_in: ProviderServiceUpdate) -> Service:
        """
        Actualiza los detalles (precio, descripción, categoría) de un servicio existente.
        """
        service = self.get_service(db, service_id, user_id)
        return service_repo.update(db, db_obj=service, obj_in=obj_in)

    def delete_service(self, db: Session, service_id: int, user_id: int) -> Service:
        """
        Realiza un borrado lógico (soft delete) del servicio marcándolo como inactivo.
        """
        service = self.get_service(db, service_id, user_id)
        service.is_active = False
        db.add(service)
        db.commit()
        db.refresh(service)
        return service

    def toggle_service_status(self, db: Session, service_id: int, user_id: int) -> Service:
        """
        Activa o desactiva la visibilidad de un servicio en la plataforma.
        """
        service = self.get_service(db, service_id, user_id)
        service.is_active = not service.is_active
        db.add(service)
        db.commit()
        db.refresh(service)
        return service

# Instancia global para la gestión de servicios de proveedores
provider_service_management = ProviderServiceManagementService()
