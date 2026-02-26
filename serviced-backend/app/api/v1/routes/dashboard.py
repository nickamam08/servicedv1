from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Any, List, Optional

from app.db.session import get_db
# Models
from app.models import User, Service, ServiceRequest, RequestStatus, Order, OrderStatus, Notification, ChatConversation, ChatMessage
# Schemas
from app.schemas.dashboard import DashboardSummary, NotificationSchema, UserProfileSchema
# Auth dependency
from app.dependencies.deps import get_current_user

router = APIRouter()

@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get dashboard summary statistics for the current user.
    """
    try:
        # 1. Balance (Mocked for now as per plan)
        balance = 1250.50
        
        # 2. Active Services Count
        active_services_count = 0
        
        # 3. Active Requests Count (for Client) & Services (for Provider)
        if current_user.role == "provider":
            # Provider: count active services they OFFER
            if current_user.provider_profile:
                active_services_count = db.query(Service).filter(
                    Service.provider_id == current_user.provider_profile.id,
                    Service.is_active == True
                ).count()
                # Provider might also have requests they made as a client? 
                active_requests_count = db.query(ServiceRequest).filter(
                    ServiceRequest.client_id == current_user.id,
                    ServiceRequest.status.in_([RequestStatus.PENDING, RequestStatus.ACTIVE])
                ).count()
        else:
            # Client: count active requests
            # Note: Model is ServiceRequest, not Order (unless we migrated). Usage: ServiceRequest.
            active_requests_count = db.query(ServiceRequest).filter(
                ServiceRequest.client_id == current_user.id,
                ServiceRequest.status.in_([RequestStatus.PENDING, RequestStatus.ACTIVE])
            ).count()
            active_services_count = 0 # Clients don't offer services

        # 4. Notifications (Latest unread)
        notifications = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).order_by(Notification.created_at.desc()).limit(5).all()

        unread_notifications_count = db.query(Notification).filter(
            Notification.user_id == current_user.id,
            Notification.is_read == False
        ).count()

        # 5. Messages Unread Count
        unread_messages_count = db.query(ChatMessage).join(ChatConversation).filter(
            (ChatConversation.client_id == current_user.id) | (ChatConversation.provider_id == current_user.id),
            ChatMessage.sender_id != current_user.id,
            ChatMessage.is_read == False
        ).count()

        # 6. Recommended Services (Random 4 active services)
        recommended_services = db.query(Service).filter(
            Service.is_active == True
        ).order_by(func.random()).limit(4).all()

        # 7. User Profile
        user_profile = {
            "full_name": current_user.full_name,
            "avatar_initials": current_user.avatar_initials
        }

        # 8. Recent Requests (for Client)
        recent_requests = []
        if current_user.role == "client":
            requests_data = db.query(
                ServiceRequest.id,
                ServiceRequest.status,
                ServiceRequest.created_at,
                Service.title.label("service_title")
            ).join(Service, ServiceRequest.service_id == Service.id).filter(
                ServiceRequest.client_id == current_user.id
            ).order_by(ServiceRequest.created_at.desc()).limit(5).all()
            
            recent_requests = [
                {
                    "id": r.id, 
                    "status": r.status, 
                    "created_at": r.created_at, 
                    "service_title": r.service_title
                } for r in requests_data
            ]

        return {
            "balance": balance,
            "active_services_count": active_services_count,
            "active_requests_count": active_requests_count,
            "unread_notifications_count": unread_notifications_count,
            "unread_messages_count": unread_messages_count,
            "notifications": notifications,
            "user_profile": user_profile,
            "recommended_services": recommended_services,
            "recent_requests": recent_requests
        }
    except Exception as e:
        print(f"Error generating dashboard summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not generate dashboard summary: {str(e)}"
        )

@router.get("/notifications", response_model=List[NotificationSchema])
def get_all_notifications(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get all notifications for the current user.
    """
    return db.query(Notification).filter(
        Notification.user_id == current_user.id
    ).order_by(Notification.created_at.desc()).offset(skip).limit(limit).all()

@router.post("/notifications/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Mark a specific notification as read.
    """
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notification.is_read = True
    db.add(notification)
    db.commit()
    return {"status": "success"}

@router.post("/notifications/mark-all-read")
def mark_all_notifications_as_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Mark all notifications for the current user as read.
    """
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({"is_read": True})
    db.commit()
    return {"status": "success"}
