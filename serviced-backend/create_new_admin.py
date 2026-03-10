from app.db.session import SessionLocal
from app.models.all_models import User, UserRole
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    email = "admin@serviced.com"
    password = "AdminPassword2026!"
    full_name = "Admin Principal"
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"User with email {email} already exists.")
            # Update to admin just in case
            existing_user.role = UserRole.ADMIN.value
            existing_user.password_hash = get_password_hash(password)
            db.commit()
            print(f"Updated existing user to ADMIN with password: {password}")
        else:
            # Create new admin user
            new_admin = User(
                full_name=full_name,
                email=email,
                password_hash=get_password_hash(password),
                role=UserRole.ADMIN.value,
                is_active=True,
                avatar_initials="AP"
            )
            db.add(new_admin)
            db.commit()
            print("Admin user created successfully!")
            print(f"Email: {email}")
            print(f"Password: {password}")
            
    except Exception as e:
        print(f"Error creating admin: {str(e).encode('ascii', 'ignore').decode('ascii')}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
