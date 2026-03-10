from app.db.session import SessionLocal
from app.services import admin_dashboard_service, admin_user_service, admin_request_service
import traceback

def test_admin_services():
    db = SessionLocal()
    try:
        print("Testing platform stats...")
        stats = admin_dashboard_service.get_platform_stats(db)
        print(f"Stats: {stats}")
        
        print("\nTesting get users...")
        users = admin_user_service.get_all_users(db)
        print(f"Found {len(users)} users")
        
        print("\nTesting get requests...")
        requests = admin_request_service.get_all_requests(db)
        print(f"Found {len(requests)} requests")
        
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_services()
