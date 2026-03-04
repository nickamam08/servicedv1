from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Any, List
from sqlalchemy import desc

from app.db.session import get_db
from app.models import Order, OrderStatus, Service, User
from app.schemas.order import OrderCreate, OrderResponse
from app.dependencies.deps import get_current_user

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
) -> Any:
    """
    Recupera el historial de órdenes de compra del usuario autenticado.
    Ordenado por fecha de creación descendente.
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
    Inicia el proceso de contratación de un servicio mediante la creación de una orden.
    Valida la existencia del servicio y previene la auto-contratación.
    """
    # 1. Validar que el servicio existe y está marcado como activo
    service = db.query(Service).filter(Service.id == order_in.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    if not service.is_active:
        raise HTTPException(status_code=400, detail="El servicio no está activo")

    # 2. Impedir que un proveedor contrate sus propios servicios
    if current_user.provider_profile and service.provider_id == current_user.provider_profile.id:
        raise HTTPException(status_code=400, detail="No puedes contratar tu propio servicio")

    # 3. Calcular el precio total (Por ahora solo el precio base del servicio)
    total_price = service.price

    # 4. Registrar la orden en la base de datos con estado PENDIENTE
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
