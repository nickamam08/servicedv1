
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.db.base import Base

# --- Enums ---
class UserRole(str, enum.Enum):
    CLIENT = "client"
    PROVIDER = "provider"
    ADMIN = "admin"

class RequestStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class OrderStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ReportStatus(str, enum.Enum):
    PENDING = "PENDING"
    INVESTIGATING = "INVESTIGATING"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"

class ReportPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

# --- Models ---

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default=UserRole.CLIENT)
    is_active = Column(Boolean, default=True)
    phone = Column(String, nullable=True)
    location = Column(String, nullable=True)
    avatar_initials = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class ProviderProfile(Base):
    __tablename__ = "provider_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    description = Column(String)
    specialty = Column(String, nullable=True)
    skills = Column(String, nullable=True) # Comma-separated
    social_links = Column(JSON, nullable=True) # e.g. {"linkedin": "...", "website": "..."}
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    certifications = Column(JSON, nullable=True) # List of strings or objects
    languages = Column(String, nullable=True) # Comma-separated
    base_rate = Column(Float, default=0.0)
    experience_years = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    availability = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
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
    __tablename__ = "services"
    id = Column(Integer, primary_key=True, index=True)
    provider_id = Column(Integer, ForeignKey("provider_profiles.id"), nullable=False)
    title = Column(String, index=True)
    description = Column(String)
    price = Column(Float) # base_price
    duration = Column(String) # legacy or display string
    duration_minutes = Column(Integer, nullable=True)
    category = Column(String, index=True, nullable=True)
    image_urls = Column(JSON, nullable=True)
    faqs = Column(JSON, nullable=True)
    rating = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    @property
    def provider_user_id(self):
        return self.provider.user_id if self.provider else None

class ServiceRequest(Base):
    __tablename__ = "service_requests"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    status = Column(String, default=RequestStatus.PENDING)
    price_at_purchase = Column(Float, nullable=True)
    scheduled_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String, nullable=True)
    history = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True)

class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("chat_conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=True) # Added for linking review to request
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(String, nullable=True) # e.g. "request_update", "message", "system"
    title = Column(String, nullable=False)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=False)
    status = Column(String, default=OrderStatus.PENDING)
    total_price = Column(Float, nullable=False)
    payment_method = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reported_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True)
    request_id = Column(Integer, ForeignKey("service_requests.id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    type = Column(String, nullable=False) # e.g. "behavior", "payment", "content", "technical"
    status = Column(String, default=ReportStatus.PENDING)
    priority = Column(String, default=ReportPriority.MEDIUM)
    
    admin_notes = Column(String, nullable=True)
    resolution = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Set relationships AFTER all classes are defined
# Using PrimaryJoin for definitive resolution

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
