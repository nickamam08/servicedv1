from app.schemas.user import UserCreate
from pydantic import ValidationError

def test_pydantic_validation():
    payload = {
        "full_name": "Juan Perez",
        "email": "juan@example.com",
        "password": "Password123!",
        "phone": "3001234567",
        "location": "Bogota",
        "role": "client"
    }
    
    print("Testing with complete payload...")
    try:
        user = UserCreate(**payload)
        print("Validation successful!")
        print(f"User email: {user.email}")
        print(f"User role: {user.role}")
        print(f"User phone: {user.phone}")
    except ValidationError as e:
        print("Validation failed!")
        print(e.json())

    payload_empty_phone = payload.copy()
    payload_empty_phone["phone"] = ""
    print("\nTesting with empty phone string...")
    try:
        user = UserCreate(**payload_empty_phone)
        print("Validation successful!")
    except ValidationError as e:
        print("Validation failed!")
        print(e.json())

    payload_invalid_password = payload.copy()
    payload_invalid_password["password"] = "123"
    print("\nTesting with invalid password...")
    try:
        user = UserCreate(**payload_invalid_password)
        print("Validation successful!")
    except ValidationError as e:
        print("Validation failed!")
        # print(e.json()) # We expect this to fail

if __name__ == "__main__":
    test_pydantic_validation()
