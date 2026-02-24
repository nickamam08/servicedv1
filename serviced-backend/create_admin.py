from app.db.session import SessionLocal
from app.models import User
from app.core.security import get_password_hash
from app.models.all_models import UserRole

def create_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            print("Creating default admin...")
            admin = User(
                full_name="Admin User",
                email="admin@serviced.com",
                password_hash=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                avatar_initials="AU"
            )
            db.add(admin)
            db.commit()
            print("Admin created: admin@serviced.com / admin123")
        else:
            print(f"Admin already exists: {admin.email}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
