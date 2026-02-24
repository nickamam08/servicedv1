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
    print("\n--- DASHBOARD OVERVIEW JSON ---")
    print(json.dumps(data, indent=2))

    print("\nFetching Provider Requests...")
    resp = requests.get(f"{API_URL}/provider/dashboard/requests", headers=headers)
    if resp.status_code == 200:
        reqs = resp.json()
        print("\n--- REQUESTS JSON ---")
        print(json.dumps(reqs, indent=2))
    print("\nWriting output to debug_dashboard_output.json...")
    output = {
        "overview": data,
        "requests": reqs if 'reqs' in locals() else []
    }
    with open("debug_dashboard_output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)

if __name__ == "__main__":
    main()
