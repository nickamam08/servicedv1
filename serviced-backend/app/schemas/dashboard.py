from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Esquema para el envío de notificaciones al panel del usuario
class NotificationSchema(BaseModel):
    id: int
    title: str
    message: str
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Información básica del perfil para el cabezote del dashboard
class UserProfileSchema(BaseModel):
    full_name: str
    avatar_initials: Optional[str] # Iniciales calculadas (ej: "JD")
    
    class Config:
        from_attributes = True

# Vista previa simplificada de un servicio para carruseles o listas rápidas
class ServiceSimple(BaseModel):
    id: int
    title: str
    price: float
    description: Optional[str] = None
    category: Optional[str] = None
    image_urls: Optional[List[str]] = []
    
    class Config:
        from_attributes = True

# Resumen mínimo de una solicitud para la tabla de actividad reciente
class RequestMinimal(BaseModel):
    id: int
    status: str
    created_at: datetime
    service_title: Optional[str] = None
    
    class Config:
        from_attributes = True

# Objeto principal enviado al cargar el dashboard del usuario (Cliente)
class DashboardSummary(BaseModel):
    balance: float # Saldo disponible (si aplica)
    active_services_count: int
    active_requests_count: int
    unread_notifications_count: int = 0
    unread_messages_count: int = 0
    notifications: List[NotificationSchema]
    user_profile: UserProfileSchema
    recommended_services: List[ServiceSimple] = [] # Servicios sugeridos según intereses
    recent_requests: List[RequestMinimal] = [] # Últimas transacciones/solicitudes
