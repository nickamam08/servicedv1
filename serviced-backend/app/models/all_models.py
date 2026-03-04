# Importaciones necesarias de SQLAlchemy para definir la estructura de la base de datos
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

# Importación de la clase base para los modelos
from app.db.base import Base

# --- Enumeraciones (Enums) ---
class UserRole(str, enum.Enum):
    """Roles de usuario disponibles en la plataforma"""
    CLIENT = "client"      # Cliente/Usuario que busca servicios
    PROVIDER = "provider"  # Proveedor de servicios
    ADMIN = "admin"        # Administrador del sistema

class RequestStatus(str, enum.Enum):
    """Estados posibles de una solicitud de servicio"""
    PENDING = "PENDING"      # Pendiente de aprobación
    ACTIVE = "ACTIVE"        # En curso
    COMPLETED = "COMPLETED"  # Finalizada
    CANCELLED = "CANCELLED"  # Cancelada

class OrderStatus(str, enum.Enum):
    """Estados posibles de una orden (transacción)"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ReportStatus(str, enum.Enum):
    """Estados para los reportes o denuncias"""
    PENDING = "PENDING"         # Pendiente de revisión
    INVESTIGATING = "INVESTIGATING" # En investigación por un admin
    RESOLVED = "RESOLVED"       # Resuelto
    DISMISSED = "DISMISSED"     # Descartado

class ReportPriority(str, enum.Enum):
    """Prioridad de los reportes"""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

# --- Modelos de la Base de Datos ---

class Category(Base):
    """Modelo para las categorías de servicios (ej. Limpieza, Plomería)"""
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # Nombre de la categoría
    is_active = Column(Boolean, default=True) # Indica si la categoría está disponible
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    """Modelo principal de Usuario centralizando datos de acceso y perfil básico"""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True) # Nombre completo
    email = Column(String, unique=True, index=True, nullable=False) # Correo electrónico único
    password_hash = Column(String, nullable=False) # Contraseña encriptada
    role = Column(String, default=UserRole.CLIENT) # Rol del usuario (cliente, proveedor, admin)
    is_active = Column(Boolean, default=True) # Estado de la cuenta
    phone = Column(String, nullable=True) # Teléfono de contacto
    location = Column(String, nullable=True) # Ubicación general
    avatar_initials = Column(String, nullable=True) # Iniciales para el avatar por defecto
    avatar_url = Column(String, nullable=True) # URL de la imagen de perfil
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProviderProfile(Base):
    """Perfil extendido para usuarios que actúan como Proveedores de servicios"""
    __tablename__ = "provider_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True) # Relación con el usuario base
    description = Column(String) # Bio/Descripción del proveedor
    specialty = Column(String, nullable=True) # Especialidad principal
    skills = Column(String, nullable=True) # Habilidades separadas por comas
    social_links = Column(JSON, nullable=True) # Enlaces sociales (JSON)
    latitude = Column(Float, nullable=True) # Coordenadas para geolocalización
    longitude = Column(Float, nullable=True)
    certifications = Column(JSON, nullable=True) # Lista de certificaciones
    languages = Column(String, nullable=True) # Idiomas que habla
    base_rate = Column(Float, default=0.0) # Tarifa base sugerida
    experience_years = Column(Integer, nullable=True) # Años de experiencia
    location = Column(String, nullable=True) # Ubicación específica del proveedor
    availability = Column(String, nullable=True) # Horarios de disponibilidad
    is_verified = Column(Boolean, default=False) # Indica si el proveedor ha sido verificado por admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def rating_average(self):
        if not self.user or not self.user.reviews_received:
            return 0.0
        ratings = [r.rating for r in self.user.reviews_received]
        return sum(ratings) / len(ratings)

    @property
    def total_reviews(self):
        return len(self.user.reviews_received) if self.user and self.user.reviews_received else 0

    @property
    def full_name(self):
        return self.user.full_name if self.user else "Unknown"

    @property
    def avatar_url(self):
        return self.user.avatar_url if self.user else None

class Service(Base):
    """Modelo para los servicios específicos ofrecidos por un Proveedor"""
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("provider_profiles.id"), nullable=False) # Quién ofrece el servicio
    title = Column(String, index=True) # Título del servicio
    description = Column(String) # Detalle de lo que incluye
    price = Column(Float) # Precio base
    duration = Column(String) # Texto descriptivo de la duración
    duration_minutes = Column(Integer, nullable=True) # Duración estimada en minutos
    category = Column(String, index=True, nullable=True) # Categoría del servicio
    image_urls = Column(JSON, nullable=True) # URLs de imágenes del servicio
    faqs = Column(JSON, nullable=True) # Preguntas frecuentes (JSON)
    rating = Column(Float, default=0.0) # Calificación promedio del servicio
    is_active = Column(Boolean, default=True) # Si el servicio se muestra en búsquedas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def provider_user_id(self):
        return self.provider.user_id if self.provider else None

class ServiceRequest(Base):
    """Modelo para las solicitudes de servicios realizadas por Clientes"""
    __tablename__ = "service_requests"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Cliente que solicita
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False) # Servicio solicitado
    status = Column(String, default=RequestStatus.PENDING) # Estado de la solicitud
    price_at_purchase = Column(Float, nullable=True) # Precio acordado al momento de la solicitud
    scheduled_date = Column(DateTime(timezone=True), nullable=True) # Fecha y hora agendada
    notes = Column(String, nullable=True) # Notas adicionales del cliente
    history = Column(JSON, nullable=True) # Historial de cambios de estado (JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

class ChatConversation(Base):
    """Modelo para agrupar mensajes de chat entre un Cliente y un Proveedor"""
    __tablename__ = "chat_conversations"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False) # ID del cliente
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False) # ID del proveedor
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=True) # Solicitud relacionada (opcional)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ChatMessage(Base):
    """Modelo para mensajes individuales dentro de una conversación"""
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False) # Conversación a la que pertenece
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Quién envió el mensaje
    content = Column(String, nullable=False) # Contenido del mensaje
    is_read = Column(Boolean, default=False) # Indica si el destinatario lo leyó
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Review(Base):
    """Modelo para las reseñas y calificaciones entre usuarios"""
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Cliente que califica
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Proveedor calificado
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=True) # Solicitud que originó la reseña
    rating = Column(Integer, nullable=False) # Calificación de 1 a 5
    comment = Column(String, nullable=True) # Comentario escrito
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Notification(Base):
    """Modelo para el sistema de notificaciones del usuario"""
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Destinatario
    type = Column(String, nullable=True) # Tipo: "request_update", "message", "system"
    title = Column(String, nullable=False) # Título de la notificación
    message = Column(String, nullable=False) # Cuerpo del mensaje
    is_read = Column(Boolean, default=False) # Estado de lectura
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Order(Base):
    """Modelo para transacciones económicas dentro de la plataforma"""
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Cliente que paga
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False) # Servicio pagado
    status = Column(String, default=OrderStatus.PENDING) # Estado del pago
    total_price = Column(Float, nullable=False) # Monto total
    payment_method = Column(String, nullable=True) # Método usado
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Report(Base):
    """Modelo para el sistema de reportes, denuncias y soporte técnico"""
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False) # Quién reporta
    reported_user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Usuario reportado (si aplica)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True) # Servicio reportado (si aplica)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=True) # Solicitud reportada (si aplica)
    
    title = Column(String, nullable=False) # Breve título del reporte
    description = Column(String, nullable=False) # Explicación detallada
    type = Column(String, nullable=False) # Tipo: "behavior", "payment", "content", "technical"
    status = Column(String, default=ReportStatus.PENDING) # Estado administrativo
    priority = Column(String, default=ReportPriority.MEDIUM) # Nivel de urgencia
    
    admin_notes = Column(String, nullable=True) # Notas internas para administradores
    resolution = Column(String, nullable=True) # Descripción de cómo se resolvió
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Configuración de Relaciones (ORM)
# Se definen aquí una vez que todas las clases han sido cargadas para evitar errores de referencia circular.
# Se utiliza PrimaryJoin para una resolución precisa entre tablas relacionadas.

User.provider_profile = relationship(ProviderProfile, back_populates="user", uselist=False)
User.notifications = relationship(Notification, back_populates="user")
User.reviews_given = relationship(Review, primaryjoin=User.id == Review.client_id, back_populates="client")
User.reviews_received = relationship(Review, primaryjoin=User.id == Review.provider_id, back_populates="provider")
User.client_conversations = relationship(ChatConversation, primaryjoin=User.id == ChatConversation.client_id, back_populates="client")
User.provider_conversations = relationship(ChatConversation, primaryjoin=User.id == ChatConversation.provider_id, back_populates="provider")
User.sent_messages = relationship(ChatMessage, primaryjoin=User.id == ChatMessage.sender_id, back_populates="sender")
User.service_requests = relationship(ServiceRequest, back_populates="client")
User.orders = relationship(Order, back_populates="client")

ProviderProfile.user = relationship(User, back_populates="provider_profile")
ProviderProfile.services = relationship(Service, back_populates="provider")

Service.provider = relationship(ProviderProfile, back_populates="services")
Service.requests = relationship(ServiceRequest, back_populates="service")
Service.orders = relationship(Order, back_populates="service")

ServiceRequest.client = relationship(User, back_populates="service_requests")
ServiceRequest.service = relationship(Service, back_populates="requests")
ServiceRequest.conversation = relationship(ChatConversation, back_populates="request", uselist=False)

ChatConversation.client = relationship(User, primaryjoin=ChatConversation.client_id == User.id, back_populates="client_conversations")
ChatConversation.provider = relationship(User, primaryjoin=ChatConversation.provider_id == User.id, back_populates="provider_conversations")
ChatConversation.request = relationship(ServiceRequest, back_populates="conversation")
ChatConversation.messages = relationship(ChatMessage, back_populates="conversation", cascade="all, delete-orphan")

ChatMessage.conversation = relationship(ChatConversation, back_populates="messages")
ChatMessage.sender = relationship(User, primaryjoin=ChatMessage.sender_id == User.id, back_populates="sent_messages")

Review.client = relationship(User, primaryjoin=Review.client_id == User.id, back_populates="reviews_given")
Review.provider = relationship(User, primaryjoin=Review.provider_id == User.id, back_populates="reviews_received")

Notification.user = relationship(User, back_populates="notifications")

Order.client = relationship(User, back_populates="orders")
Order.service = relationship(Service, back_populates="orders")

Report.reporter = relationship(User, primaryjoin=Report.reporter_id == User.id, back_populates="reports_made")
Report.reported_user = relationship(User, primaryjoin=Report.reported_user_id == User.id, back_populates="reports_received")
Report.service = relationship(Service)
Report.request = relationship(ServiceRequest)

User.reports_made = relationship(Report, primaryjoin=User.id == Report.reporter_id, back_populates="reporter")
User.reports_received = relationship(Report, primaryjoin=User.id == Report.reported_user_id, back_populates="reported_user")
