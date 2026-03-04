from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

# --- Resumen del Dashboard (Vista General) ---

class UpcomingJob(BaseModel):
    """Información básica de un trabajo programado próximamente."""
    id: int
    client_name: str
    service_title: str
    scheduled_date: datetime
    status: str

    class Config:
        from_attributes = True

class DashboardOverview(BaseModel):
    """Estadísticas consolidadas para el dashboard principal del proveedor."""
    total_services: int # Total de servicios creados por el proveedor
    active_services: int # Servicios actualmente visibles
    total_requests: int # Solicitudes históricas recibidas
    pending_requests: int # Solicitudes esperando respuesta
    accepted_requests: int # Trabajos en curso (aceptados)
    completed_requests: int # Trabajos finalizados
    cancelled_requests: int # Trabajos rechazados o cancelados
    average_rating: float = 0.0 # Calificación promedio del proveedor
    total_reviews: int
    unread_messages: int # Mensajes de chat sin leer
    balance: float = 0.0 # Saldo acumulado (simulado)
    upcoming_jobs: List[UpcomingJob] # Lista de los próximos compromisos

# --- Gestión de Servicios (Catálogo) ---

class ProviderServiceBase(BaseModel):
    """Atributos base de un servicio compartido entre creación y respuesta."""
    title: str
    description: str
    category: Optional[str] = None
    price: float
    duration_minutes: Optional[int] = 60
    duration: Optional[str] = "1 hora" # Representación textual (ej: "45 min")
    is_active: bool = True
    image_urls: Optional[List[str]] = []

class ProviderServiceCreate(ProviderServiceBase):
    """Esquema para que el proveedor publique un nuevo servicio."""
    pass

class ProviderServiceUpdate(BaseModel):
    """Esquema para que el proveedor edite un servicio existente."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    price: Optional[float] = None
    duration_minutes: Optional[int] = None
    duration: Optional[str] = None
    is_active: Optional[bool] = None
    image_urls: Optional[List[str]] = None

class ProviderServiceResponse(ProviderServiceBase):
    """Respuesta con el detalle de un servicio del proveedor."""
    id: int
    provider_id: int
    rating: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Gestión de Solicitudes (Contrataciones) ---

class ProviderRequestResponse(BaseModel):
    """Detalle de una solicitud de servicio recibida por el proveedor."""
    id: int
    client_id: int
    client_name: str
    service_title: str
    status: str
    price: float
    scheduled_date: Optional[datetime]
    notes: Optional[str] # Notas o instrucciones enviadas por el cliente
    created_at: datetime

    class Config:
        from_attributes = True

class RequestStatusUpdate(BaseModel):
    """Esquema para aceptar, rechazar o marcar como completada una solicitud."""
    status: str # Estados válidos: ACCEPTED, REJECTED, COMPLETED
    scheduled_date: Optional[datetime] = None # Opcional para reprogramar al aceptar

# --- Gestión del Perfil del Proveedor ---

class ProviderProfileUpdate(BaseModel):
    """Esquema para actualizar la información profesional y personal del proveedor."""
    description: Optional[str] = None # Biografía profesional
    specialty: Optional[str] = None
    skills: Optional[str] = None
    social_links: Optional[dict] = None
    base_rate: Optional[float] = None
    experience_years: Optional[int] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    certifications: Optional[list] = None
    languages: Optional[str] = None
    # Datos de usuario base (opcionales en la actualización del perfil)
    full_name: Optional[str] = None
    email: Optional[str] = None
    new_password: Optional[str] = None


class ProviderProfileResponse(BaseModel):
    """Respuesta completa con la información pública y privada del proveedor."""
    id: int
    user_id: int
    full_name: str
    avatar_url: Optional[str]
    description: Optional[str]
    specialty: Optional[str]
    skills: Optional[str]
    social_links: Optional[dict]
    base_rate: Optional[float] = 0.0
    experience_years: Optional[int]
    location: Optional[str]
    availability: Optional[str]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    certifications: Optional[list] = None
    languages: Optional[str] = None
    email: Optional[str] = None

    rating_average: Optional[float] = 0.0
    total_reviews: Optional[int] = 0
    is_verified: bool # Indica si el administrador ha validado al proveedor

    class Config:
        from_attributes = True

# --- Notificaciones ---

class NotificationResponse(BaseModel):
    """Aviso del sistema dirigido al proveedor (ej: 'Nueva solicitud recibida')."""
    id: int
    title: str
    message: str
    type: Optional[str] # Categoría (ej: 'request_update', 'chat_message')
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
