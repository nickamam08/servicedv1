import sys
import os

# Ensure we can import from app
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models import User, ProviderProfile

def inspect_user(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User NOT FOUND: {email}")
            return

        print(f"User ID: {user.id}")
        print(f"Name: {user.full_name}")
        print(f"Email: {user.email}")
        print(f"Role: '{user.role}'")
        print(f"Is Active: {user.is_active}")
        
        profile = db.query(ProviderProfile).filter(ProviderProfile.user_id == user.id).first()
        if profile:
            print(f"Provider Profile: FOUND (ID: {profile.id})")
        else:
            print("Provider Profile: MISSING")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python inspect_user.py <email>")
    else:
        inspect_user(sys.argv[1])
