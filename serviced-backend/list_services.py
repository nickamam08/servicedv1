
import requests
import sys

BASE_URL = "http://localhost:8000/api/v1"

def main():
    # Login as admin or provider to get token
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "provider_search_test@test.com", "password": "password123"})
    if resp.status_code != 200:
        print("Login failed, trying generic provider...")
        resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "provider_check2@test.com", "password": "password123"})
        if resp.status_code != 200:
             print("Login failed completely.")
             return

    token = resp.json()["access_token"]
    
    print("--- Listing ALL Services ---")
    resp = requests.get(f"{BASE_URL}/services/", headers={"Authorization": f"Bearer {token}"})
    services = resp.json()
    
    for s in services:
        print(f"ID: {s['id']} | Category: '{s['category']}' | Title: {s['title']}")

if __name__ == "__main__":
    main()
