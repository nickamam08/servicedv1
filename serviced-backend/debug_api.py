import requests
import sys

# Constants
API_URL = "http://localhost:8000/api/v1"
LOGIN_DATA = {"email": "client@example.com", "password": "password123"} # Adjust credential if needed

def debug_service():
    # 1. Login to get token
    try:
        resp = requests.post(f"{API_URL}/auth/login", json=LOGIN_DATA)
        if resp.status_code != 200:
            print(f"Login failed: {resp.status_code} {resp.text}")
            return
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("Login successful.")

        # 2. Get Services to find one ID
        resp = requests.get(f"{API_URL}/services/", headers=headers)
        services = resp.json()
        if not services:
            print("No services found.")
            return
        
        service_id = services[0]["id"]
        print(f"Checking Service ID: {service_id}")

        # 3. Get Service Detail
        resp = requests.get(f"{API_URL}/services/{service_id}", headers=headers)
        service_detail = resp.json()
        
        print("Service Detail JSON Keys:", service_detail.keys())
        print(f"provider_user_id: {service_detail.get('provider_user_id')}")
        print(f"Full JSON: {service_detail}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_service()
