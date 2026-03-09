from app.db.session import SessionLocal
from app.models import User
from app.core.security import get_password_hash
from app.models.all_models import UserRole

def create_custom_admin():
    db = SessionLocal()
    email = "admin_master@serviced.com"
    password = "AdminPassword123!"
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print(f"User already exists: {email}")
            # Update role just in case
            existing.role = UserRole.ADMIN
            existing.password_hash = get_password_hash(password)
            db.commit()
            print(f"Updated user {email} to ADMIN with new password.")
        else:
            print(f"Creating new admin: {email}")
            admin = User(
                full_name="Super Admin",
                email=email,
                password_hash=get_password_hash(password),
                role=UserRole.ADMIN,
                is_active=True,
                avatar_initials="SA"
            )
            db.add(admin)
            db.commit()
            print(f"Admin created successfully: {email} / {password}")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_custom_admin()
