import requests
import json

API_URL = "http://localhost:8000/api/v1"

def main():
    email = "provider@test.com"
    password = "password123"
    
    print(f"Logging in as {email}...")
    resp = requests.post(f"{API_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    
    if resp.status_code != 200:
        print(f"Login failed: {resp.text}")
        return
        
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    print("Fetching Dashboard Overview...")
    resp = requests.get(f"{API_URL}/provider/dashboard/overview", headers=headers)
    
    if resp.status_code != 200:
        print(f"Failed to fetch overview: {resp.text}")
        return
        
    data = resp.json()
    print("\n--- DASHBOARD OVERVIEW ---")
    print(json.dumps(data, indent=2))
    
    # Simple assertions
    assert data["total_services"] >= 2, "Should have at least 2 services"
    assert data["total_requests"] >= 4, "Should have at least 4 requests" # 1 pending, 1 accepted, 1 completed, 1 cancelled
    assert data["unread_messages"] >= 1, "Should have unread messages"
    assert len(data["upcoming_jobs"]) > 0, "Should have upcoming jobs"
    
    print("\n--- VERIFICATION SUCCESS ---")

if __name__ == "__main__":
    main()
