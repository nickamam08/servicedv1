import requests

BASE_URL = "http://localhost:8000/api/v1"

def login_client():
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": "client1@test.com", "password": "password123"})
    if resp.status_code == 200:
        return resp.json()["access_token"]
    print(f"Login failed: {resp.status_code} - {resp.text}")
    return None

def verify_dashboard():
    token = login_client()
    if not token: return

    print("Testing /dashboard/summary...")
    resp = requests.get(f"{BASE_URL}/dashboard/summary", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"Keys: {list(data.keys())}")
        print(f"Active Requests: {data.get('active_requests_count')}")
        print(f"Rec. Services: {len(data.get('recommended_services', []))}")
    else:
        print(resp.text)

    print("\nTesting /services/...")
    resp = requests.get(f"{BASE_URL}/services/", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {resp.status_code}")
    if resp.status_code != 200: print(resp.text)

    print("\nTesting /requests/...")
    resp = requests.get(f"{BASE_URL}/requests/", headers={"Authorization": f"Bearer {token}"})
    print(f"Status: {resp.status_code}")
    if resp.status_code != 200: print(resp.text)

if __name__ == "__main__":
    verify_dashboard()
