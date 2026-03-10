import sys
import os
sys.path.append(os.getcwd())
from dotenv import load_dotenv
load_dotenv()

from app.db.session import SessionLocal
from app.repositories import user as user_repo
from app.schemas.user import UserCreate

def init():
    db = SessionLocal()
    try:
        user = user_repo.get_by_email(db, email="admin@serviced.com")
        if not user:
            user_in = UserCreate(
                email="admin@serviced.com",
                password="password123",
                full_name="Super Admin",
                role="admin",
                phone="+123456789",
                location="Nube"
            )
            user = user_repo.create(db, obj_in=user_in)
            print(f"✅ Application Admin created: {user.email}")
        else:
            print(f"✅ Application Admin already exists: {user.email}")
    except Exception as e:
        print(f"❌ Error creating initial data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating initial data...")
    init()
