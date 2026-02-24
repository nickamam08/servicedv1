import sys
import os

sys.path.append(os.getcwd())

from app.db.session import SessionLocal
from app.models import User, UserRole

def verify(email):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print("User not found")
            return

        print(f"User Role (DB): '{user.role}' type={type(user.role)}")
        print(f"Enum Provider: '{UserRole.PROVIDER}' type={type(UserRole.PROVIDER)}")
        print(f"Enum Value: '{UserRole.PROVIDER.value}' type={type(UserRole.PROVIDER.value)}")
        
        # Test comparisons
        is_equal_enum = (user.role == UserRole.PROVIDER)
        is_equal_value = (user.role == UserRole.PROVIDER.value)
        is_equal_string = (user.role == "provider")
        
        print(f"user.role == UserRole.PROVIDER: {is_equal_enum}")
        print(f"user.role == UserRole.PROVIDER.value: {is_equal_value}")
        print(f"user.role == 'provider': {is_equal_string}")
        
    finally:
        db.close()

if __name__ == "__main__":
    verify("alvarezmaciasnicolas@gmail.com")
