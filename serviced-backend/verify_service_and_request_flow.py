import requests

BASE_URL = "http://localhost:8000/api/v1"

def login(email, password):
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    print(f"Login failed for {email}: {resp.text}")
    return None

def verify_flow():
    # 1. Login as Client
    client_token = login("client1@test.com", "password123")
    if not client_token: return

    # 2. Get Service Detail
    print("Fetching services...")
    services_resp = requests.get(f"{BASE_URL}/services/", headers={"Authorization": f"Bearer {client_token}"})
    if services_resp.status_code != 200:
        print(f"Failed to fetch services: {services_resp.text}")
        return
    
    services = services_resp.json()
    if not services:
        print("No services found.")
        return
    
    svc_id = services[0]["id"]
    print(f"Fetching Service ID {svc_id}...")
    svc_detail = requests.get(f"{BASE_URL}/services/{svc_id}", headers={"Authorization": f"Bearer {client_token}"}).json()
    
    print(f"Service Title: {svc_detail.get('title')}")
    print(f"Provider User ID: {svc_detail.get('provider_user_id')}")
    
    if not svc_detail.get("provider_user_id"):
        print("FAIL: provider_user_id is MISSING. Chat button will fail.")
    else:
        print("SUCCESS: provider_user_id is present.")

    # 3. Login as Provider
    # Use the provider we created/checked before
    provider_token = login("provider_check2@test.com", "password123")
    if not provider_token:
        # Try the initial provider
        provider_token = login("provider@test.com", "password123")
    
    if not provider_token:
        print("Failed to login as provider.")
        return

    # 4. Check Provider Requests
    print("Fetching Provider Requests...")
    req_resp = requests.get(f"{BASE_URL}/provider/dashboard/requests", headers={"Authorization": f"Bearer {provider_token}"})
    if req_resp.status_code == 200:
        print(f"Requests fetched successfully. Count: {len(req_resp.json())}")
    else:
        print(f"FAIL: Failed to fetch requests: {req_resp.status_code} - {req_resp.text}")

if __name__ == "__main__":
    verify_flow()
