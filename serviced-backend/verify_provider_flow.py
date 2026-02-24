import requests
import os

BASE_URL = "http://localhost:8000/api/v1"

def verify_provider_flow():
    print("--- Verifying Provider Flow ---")
    
    # 1. Register new provider
    email = "provider_check2@test.com"
    password = "password123"
    print(f"Registering {email}...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Pro Check",
        "role": "provider"
    })
    
    token = None
    if resp.status_code == 200:
        token = resp.json()["access_token"]
        print("Registration success, token received.")
    elif resp.status_code == 400 and "already exists" in resp.text:
         print("User exists, logging in...")
         resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
         if resp.status_code == 200:
             token = resp.json()["access_token"]
    
    if not token:
        print(f"Failed to authenticate: {resp.text}")
        return

    # 2. Check Profile
    print("Checking Provider Profile...")
    resp = requests.get(f"{BASE_URL}/provider/dashboard/profile", headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        print("Profile EXISTS (Auto-creation worked!).")
    else:
        print(f"Profile MISSING: {resp.status_code} - {resp.text}")
        return

    # 3. Create Service
    print("Creating Service...")
    resp = requests.post(f"{BASE_URL}/provider/dashboard/services", headers={"Authorization": f"Bearer {token}"}, json={
        "title": "Test Service",
        "description": "Test Desc",
        "price": 50,
        "category": "Tecnología"
    })
    if resp.status_code == 200:
        print("Service Created Successfully.")
    else:
        print(f"Failed to create service: {resp.text}")

    # 4. Check Clients Endpoint
    print("Checking /clients endpoint...")
    resp = requests.get(f"{BASE_URL}/provider/dashboard/clients", headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        print(f"Clients endpoint work. Count: {len(resp.json())}")
    else:
        print(f"Clients endpoint failed: {resp.status_code} - {resp.text}")

if __name__ == "__main__":
    verify_provider_flow()
