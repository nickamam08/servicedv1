from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc

from app.models import Service, ServiceRequest, Review, ChatMessage, ChatConversation, Notification, ProviderProfile, RequestStatus

class ProviderDashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_service_stats(self, provider_id: int) -> Dict[str, int]:
        total = self.db.query(func.count(Service.id)).filter(Service.provider_id == provider_id).scalar()
        active = self.db.query(func.count(Service.id)).filter(
            Service.provider_id == provider_id, 
            Service.is_active == True
        ).scalar()
        return {"total": total or 0, "active": active or 0}

    def get_request_stats(self, provider_profile_id: int) -> Dict[str, int]:
        # Filter requests where the service belongs to the provider
        base_query = self.db.query(ServiceRequest).join(Service).filter(Service.provider_id == provider_profile_id)
        
        total = base_query.count()
        pending = base_query.filter(ServiceRequest.status == RequestStatus.PENDING).count()
        accepted = base_query.filter(ServiceRequest.status == RequestStatus.ACTIVE).count() # Mapping ACTIVE to ACCEPTED concept
        completed = base_query.filter(ServiceRequest.status == RequestStatus.COMPLETED).count()
        cancelled = base_query.filter(ServiceRequest.status == RequestStatus.CANCELLED).count()
        
        return {
            "total": total,
            "pending": pending,
            "accepted": accepted,
            "completed": completed,
            "cancelled": cancelled
        }

    def get_upcoming_jobs(self, provider_profile_id: int, limit: int = 5) -> List[ServiceRequest]:
        now = datetime.utcnow()
        return self.db.query(ServiceRequest).join(Service).join(ServiceRequest.client).filter(
            Service.provider_id == provider_profile_id,
            ServiceRequest.status == RequestStatus.ACTIVE,
            ServiceRequest.scheduled_date >= now
        ).order_by(ServiceRequest.scheduled_date.asc()).limit(limit).all()

    def get_unread_messages_count(self, user_id: int) -> int:
        # Count unread messages in conversations where user is participant
        # But specifically messages SENT TO the user (so sender_id != user_id)
        return self.db.query(func.count(ChatMessage.id)).join(ChatConversation).filter(
            (ChatConversation.client_id == user_id) | (ChatConversation.provider_id == user_id),
            ChatMessage.sender_id != user_id,
            ChatMessage.is_read == False
        ).scalar() or 0

    def get_provider_profile(self, user_id: int) -> Optional[ProviderProfile]:
        return self.db.query(ProviderProfile).filter(ProviderProfile.user_id == user_id).first()

    def get_provider_reviews(self, provider_user_id: int, skip: int = 0, limit: int = 10) -> List[Review]:
        return self.db.query(Review).filter(
            Review.provider_id == provider_user_id
        ).order_by(Review.created_at.desc()).offset(skip).limit(limit).all()
        
    def get_provider_notifications(self, user_id: int, skip: int = 0, limit: int = 20) -> List[Notification]:
        return self.db.query(Notification).filter(
            Notification.user_id == user_id
        ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()
