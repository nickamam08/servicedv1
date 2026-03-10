from app.db.session import SessionLocal
from app.services import admin_user_service, admin_service_service
from app.models.all_models import User, UserRole, ProviderProfile, Service
import sys

def test_admin_actions():
    db = SessionLocal()
    try:
        # 1. Create a dummy user
        test_email = "test_admin_bug@example.com"
        existing = db.query(User).filter(User.email == test_email).first()
        if existing:
            db.delete(existing)
            db.commit()
        
        new_user = User(
            full_name="Test User",
            email=test_email,
            password_hash="fake",
            role=UserRole.CLIENT,
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(f"Created test user with ID: {new_user.id}")

        # 2. Test Deactivate
        print("Testing deactivation...")
        updated = admin_user_service.deactivate_user(db, new_user.id)
        if updated and not updated.is_active:
            print("Deactivation successful.")
        else:
            print("Deactivation FAIL.")

        # 3. Test Delete
        print("Testing deletion...")
        success = admin_user_service.delete_user(db, new_user.id)
        if success:
            print("Deletion successful.")
        else:
            print("Deletion FAIL.")

        # 4. Test Service Deletion (optional but good)
        # We need a provider first
        prov_user = User(
            full_name="Test Provider",
            email="test_prov_admin@example.com",
            password_hash="fake",
            role=UserRole.PROVIDER,
            is_active=True
        )
        db.add(prov_user)
        db.commit()
        db.refresh(prov_user)
        
        profile = ProviderProfile(user_id=prov_user.id, description="Test")
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        service = Service(provider_id=profile.id, title="Test Service", price=100.0, is_active=True)
        db.add(service)
        db.commit()
        db.refresh(service)
        print(f"Created test service with ID: {service.id}")
        
        print("Testing service deletion...")
        svc_success = admin_service_service.delete_service(db, service.id)
        if svc_success:
            print("Service deletion successful.")
        else:
            print("Service deletion FAIL.")
            
        # Clean up provider
        admin_user_service.delete_user(db, prov_user.id)
        print("Cleanup successful.")

    except Exception as e:
        print(f"ERROR during test: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_admin_actions()
