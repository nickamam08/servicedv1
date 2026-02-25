import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services import admin_user_service
from app.schemas.user import UserResponse
from pydantic import ValidationError

def diagnose_admin_users():
    db = SessionLocal()
    print("Fetching users via admin_user_service.get_all_users...")
    try:
        users = admin_user_service.get_all_users(db)
        print(f"Found {len(users)} users.")
        
        print("\nAttempting to serialize users to UserResponse...")
        for i, user in enumerate(users):
            try:
                # This mimics what FastAPI does with response_model=List[UserResponse]
                validated = UserResponse.model_validate(user)
                # print(f"User {i} (ID: {user.id}) validated successfully.")
            except Exception as e:
                print(f"\n!!! ERROR validating User at index {i} (ID: {getattr(user, 'id', 'Unknown')}):")
                print(f"Error type: {type(e).__name__}")
                print(f"Error details: {e}")
                
    except Exception as e:
        print("\n!!! ERROR fetching users:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error details: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    diagnose_admin_users()
