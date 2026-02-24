from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any

from app.db.session import get_db
from app.models import Order, OrderStatus, Service, User
from app.schemas.order import OrderCreate, OrderResponse
from app.dependencies.deps import get_current_user

from typing import Any, List
from sqlalchemy import desc

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
) -> Any:
    """
    Get all orders for the current user.
    """
    orders = db.query(Order).filter(
        Order.client_id == current_user.id
    ).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    return orders

@router.post("/create", response_model=OrderResponse)
def create_order(
    order_in: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Create a new hiring order.
    """
    # 1. Validate Service exists and is active
    service = db.query(Service).filter(Service.id == order_in.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    if not service.is_active:
        raise HTTPException(status_code=400, detail="Service is not active")

    # 2. Prevent self-hiring
    if current_user.provider_profile and service.provider_id == current_user.provider_profile.id:
        raise HTTPException(status_code=400, detail="You cannot hire your own service")

    # 3. Calculate Total Price (Just base price for now, could add quantities later)
    total_price = service.price

    # 4. Create Order
    db_order = Order(
        client_id=current_user.id,
        service_id=service.id,
        status=OrderStatus.PENDING,
        total_price=total_price,
        payment_method=order_in.payment_method
    )
    
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    return db_order
