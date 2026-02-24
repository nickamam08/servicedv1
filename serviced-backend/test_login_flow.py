import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_login(email, password):
    print(f"Testing login for {email}...")
    try:
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
        if resp.status_code == 200:
            data = resp.json()
            print("Login successful.")
            print(f"Token: {data.get('access_token')[:10]}...")
            print(f"User: {data.get('user', {}).get('full_name')} ({data.get('user', {}).get('role')})")
            return data
        else:
            print(f"Login failed: {resp.status_code} - {resp.text}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    # Test Client
    print("--- Test Client Login ---")
    test_login("client@test.com", "password123")
    
    # Test Provider
    print("\n--- Test Provider Login ---")
    test_login("provider@test.com", "password123")
