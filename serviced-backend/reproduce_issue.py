import requests
import uuid

def test_registration():
    url = "http://127.0.0.1:8000/api/v1/auth/register"
    unique_email = f"test_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "full_name": "Test User",
        "email": unique_email,
        "password": "Password123!",
        "phone": "3001234567",
        "location": "Test City",
        "role": "client"
    }
    
    print(f"Testing registration with email: {unique_email}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_registration()
