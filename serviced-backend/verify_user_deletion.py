import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.all_models import User, ProviderProfile, UserRole
from app.services import admin_user_service
from app.core import security

def verify_deletion():
    db = SessionLocal()
    email = "test_delete_user@example.com"
    
    print(f"Checking if user {email} exists...")
    user = db.query(User).filter(User.email == email).first()
    if user:
        print("User exists, deleting first to start clean.")
        admin_user_service.delete_user(db, user.id)
        db.commit()

    print(f"Creating test user {email}...")
    new_user = User(
        email=email,
        full_name="Delete Me",
        password_hash=security.get_password_hash("testpass123"),
        role=UserRole.CLIENT,
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    user_id = new_user.id
    print(f"User created with ID: {user_id}")

    # Optionally add a profile if it's a provider to test dependency handling
    # print("Adding provider profile for the user...")
    # profile = ProviderProfile(user_id=user_id, description="Test")
    # db.add(profile)
    # db.commit()

    print("\nAttempting to delete user...")
    success = admin_user_service.delete_user(db, user_id)
    
    if success:
        print("SUCCESS: User deleted from service layer.")
        
        # Verify it's gone from DB
        check_user = db.query(User).filter(User.id == user_id).first()
        if not check_user:
            print("CONFIRMED: User no longer in database.")
        else:
            print("FAILURE: User still exists in database.")
    else:
        print("FAILURE: admin_user_service.delete_user returned False.")
        
    db.close()

if __name__ == "__main__":
    verify_deletion()
