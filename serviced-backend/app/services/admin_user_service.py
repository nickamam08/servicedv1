from typing import List, Optional
from sqlalchemy.orm import Session
from app.repositories.admin_repository import admin_repo
from app.models.all_models import User

def get_all_users(
    db: Session, role: Optional[str] = None, is_active: Optional[bool] = None, search: Optional[str] = None
) -> List[User]:
    return admin_repo.fetch_all_users(db, role=role, is_active=is_active, search=search)

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def activate_user(db: Session, user_id: int) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = True
        db.commit()
        db.refresh(user)
    return user

def deactivate_user(db: Session, user_id: int) -> Optional[User]:
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        db.refresh(user)
    return user

def delete_user(db: Session, user_id: int) -> bool:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return False
    
    # Handle dependencies manually if cascades are not set
    # 1. Provider Profile
    if user.provider_profile:
        # Delete services first if profile exists
        from app.models.all_models import Service
        db.query(Service).filter(Service.provider_id == user.provider_profile.id).delete()
        db.delete(user.provider_profile)
    
    # 3. Reports, Requests, Orders, and Conversations
    from app.models.all_models import ServiceRequest, Order, ChatConversation, Report, Review, Notification
    
    # Notifications
    db.query(Notification).filter(Notification.user_id == user.id).delete()
    
    # Reviews (both given and received)
    db.query(Review).filter((Review.client_id == user.id) | (Review.provider_id == user.id)).delete()

    # Reports
    db.query(Report).filter((Report.reporter_id == user.id) | (Report.reported_user_id == user.id)).delete()
    
    # Orders
    db.query(Order).filter(Order.client_id == user.id).delete()

    # Conversations (where user is client or provider)
    # Delete messages first (though they cascade)
    conversations = db.query(ChatConversation).filter((ChatConversation.client_id == user.id) | (ChatConversation.provider_id == user.id)).all()
    for conv in conversations:
        db.delete(conv)

    # Service Requests
    requests = db.query(ServiceRequest).filter(ServiceRequest.client_id == user.id).all()
    for req in requests:
        db.delete(req)

    db.delete(user)
    db.commit()
    return True
