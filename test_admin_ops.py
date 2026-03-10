
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.join(os.getcwd(), "serviced-backend"))

from app.db.session import SessionLocal
from app.services import admin_service_service, admin_request_service
from app.models.all_models import Service, ServiceRequest, User, UserRole

def test_ops():
    db = SessionLocal()
    try:
        # 1. Find a service to delete (one that has dependencies)
        service = db.query(Service).first()
        if service:
            print(f"Attempting to delete service ID: {service.id} ({service.title})")
            try:
                success = admin_service_service.delete_service(db, service.id)
                print(f"Delete service success: {success}")
            except Exception as e:
                print(f"Delete service failed: {e}")
        else:
            print("No services found to delete.")

        # 2. Find a request to cancel
        request = db.query(ServiceRequest).first()
        if request:
            print(f"Attempting to cancel request ID: {request.id}")
            try:
                result = admin_request_service.cancel_request(db, request.id)
                if result:
                    print(f"Cancel request success. New status: {result.status}")
                else:
                    print("Cancel request returned None.")
            except Exception as e:
                print(f"Cancel request failed: {e}")
        else:
            print("No requests found to cancel.")

    finally:
        db.close()

if __name__ == "__main__":
    test_ops()
