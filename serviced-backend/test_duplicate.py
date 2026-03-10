import requests

def test_duplicate_registration():
    url = "http://127.0.0.1:8000/api/v1/auth/register"
    # We know this email exists from previous list_users output (ID 10)
    payload = {
        "full_name": "Duplicate User",
        "email": "marin@gmail.com",
        "password": "Password123!",
        "phone": "3001234567",
        "location": "Test City",
        "role": "client"
    }
    
    print(f"Testing registration with EXISTING email: {payload['email']}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_duplicate_registration()
