
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def register_or_login_provider():
    email = "provider_search_test@test.com"
    password = "password123"
    
    # Try login
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if resp.status_code == 200:
        return resp.json()["access_token"]
        
    # Register
    print("Registering provider...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Search Provider",
        "role": "provider"
    })
    if resp.status_code == 200:
        return resp.json()["access_token"]
    
    # Login again if register failed due to existence (race condition or whatever)
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if resp.status_code == 200:
        return resp.json()["access_token"]
        
    print(f"Failed to auth: {resp.text}")
    sys.exit(1)

def create_service(token, category):
    print(f"Creating service in category: {category}")
    resp = requests.post(f"{BASE_URL}/services/", headers={"Authorization": f"Bearer {token}"}, json={
        "title": f"Test Service {category}",
        "description": "Description",
        "price": 100,
        "category": category
    })
    if resp.status_code != 200:
        print(f"Failed to create service: {resp.text}")
        return None
    return resp.json()

def search_services(token, category):
    print(f"Searching for category: {category}...")
    resp = requests.get(f"{BASE_URL}/services/", headers={"Authorization": f"Bearer {token}"}, params={"category": category})
    if resp.status_code != 200:
        print(f"Search failed: {resp.text}")
        return []
    return resp.json()

def main():
    token = register_or_login_provider()
    
    # Create services - SKIPPED to verify existing data first
    # svc_tec = create_service(token, "Tecnología")
    # svc_hogar = create_service(token, "Hogar")
    
    # List all services
    print("Listing ALL services...")
    resp = requests.get(f"{BASE_URL}/services/", headers={"Authorization": f"Bearer {token}"})
    all_svcs = resp.json()
    print(f"Total services found: {len(all_svcs)}")
    for s in all_svcs:
        print(f" - ID: {s['id']}, Title: {s['title']}, Category: {s['category']}")

    # Search for Tecnología
    results = search_services(token, "Tecnología")
    print(f"Found {len(results)} services for Tecnología")
    for s in results:
        print(f" - Found Service: {s['title']} (ID: {s['id']})")

    # Search for Hogar
    results_hogar = search_services(token, "Hogar")
    print(f"Found {len(results_hogar)} services for Hogar")
    for s in results_hogar:
        print(f" - Found Service: {s['title']} (ID: {s['id']})")

if __name__ == "__main__":
    main()
