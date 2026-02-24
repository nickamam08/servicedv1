import sys
import os

# Ensure we can import from app
sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models import User, ProviderProfile, UserRole

def fix_provider_permissions(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User not found: {email}")
            return

        print(f"Found user: {user.full_name} (Current Role: {user.role})")
        
        # Update Role
        if user.role != UserRole.PROVIDER:
            user.role = UserRole.PROVIDER
            print(f"-> Updated role to {UserRole.PROVIDER}")
            db.add(user)
        
        # Check/Create Profile
        profile = db.query(ProviderProfile).filter(ProviderProfile.user_id == user.id).first()
        if not profile:
            print("-> ProviderProfile missing. Creating one...")
            profile = ProviderProfile(
                user_id=user.id,
                description="Perfil de proveedor generado automáticamente.",
                experience_years=0,
                location="Ubicación pendiente",
                availability="Disponibilidad pendiente",
                is_verified=True
            )
            db.add(profile)
        else:
            print("-> ProviderProfile already exists.")

        db.commit()
        print("Done! User permissions fixed.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python fix_provider_role.py <email>")
    else:
        fix_provider_permissions(sys.argv[1])
