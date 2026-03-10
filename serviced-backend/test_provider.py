import requests
import uuid

def test_provider_registration():
    url = "http://127.0.0.1:8000/api/v1/auth/register"
    unique_email = f"provider_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "full_name": "Test Provider",
        "email": unique_email,
        "password": "Password123!",
        "phone": "3007654321",
        "location": "Test City",
        "role": "provider"
    }
    
    print(f"Testing PROVIDER registration with email: {unique_email}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_provider_registration()
