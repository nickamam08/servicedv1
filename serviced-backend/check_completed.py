from app.db.session import SessionLocal
from app.models import ServiceRequest, RequestStatus, Service
from sqlalchemy import func

def check_completed():
    db = SessionLocal()
    try:
        count = db.query(ServiceRequest).filter(ServiceRequest.status == RequestStatus.COMPLETED).count()
        print(f"Total de solicitudes COMPLETADAS en la DB: {count}")
        
        if count > 0:
            details = db.query(ServiceRequest.id, ServiceRequest.price_at_purchase, Service.price)\
                .join(Service)\
                .filter(ServiceRequest.status == RequestStatus.COMPLETED).all()
            for d in details:
                print(f"ID: {d.id}, PriceAtPurchase: {d.price_at_purchase}, ServicePrice: {d.price}")
                
    finally:
        db.close()

if __name__ == "__main__":
    check_completed()
