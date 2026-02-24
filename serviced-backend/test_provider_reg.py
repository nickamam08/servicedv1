import requests
import random
import string

API_URL = "http://localhost:8000/api/v1"

def random_string(length=10):
    return ''.join(random.choices(string.ascii_letters, k=length))

def test_provider_registration():
    email = f"provider_{random_string()}@test.com"
    password = "password123"
    payload = {
        "email": email,
        "password": password,
        "full_name": "Test Provider",
        "role": "provider"  # Explicitly sending provider role
    }
    
    print(f"Registering user: {email} with role='provider'")
    
    try:
        res = requests.post(f"{API_URL}/auth/register", json=payload)
        if res.status_code != 200:
            print(f"FAILED: Registration returned {res.status_code}")
            print(res.text)
            return

        data = res.json()
        print("Registration successful.")
        print(f"Token received: {data.get('access_token') is not None}")
        
        user = data.get("user", {})
        print(f"User ID: {user.get('id')}")
        print(f"User Role from Response: {user.get('role')}")
        
        if user.get('role') != 'provider':
            print("CRITICAL_FAILURE: User created but role is NOT provider!")
        else:
            print("SUCCESS: User created with correct role.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_provider_registration()
