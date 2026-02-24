
import http.client
import json
import random
import string

def random_string(length=10):
    return ''.join(random.choice(string.ascii_letters) for i in range(length))

CONN_HOST = "localhost"
CONN_PORT = 8000

def test_flow():
    conn = http.client.HTTPConnection(CONN_HOST, CONN_PORT)
    
    # 1. Register User
    email = f"test_{random_string()}@example.com"
    password = "password123"
    payload = json.dumps({
        "full_name": "Test User",
        "email": email,
        "password": password,
        "phone": "+1234567890",
        "location": "Test City",
        "role": "client"
    })
    headers = {'Content-Type': 'application/json'}
    
    print(f"Registering user: {email}")
    conn.request("POST", "/auth/register", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    if res.status != 200:
        print(f"Registration failed: {res.status} {res.reason}")
        print(data.decode("utf-8"))
        return
        
    user_data = json.loads(data)
    token = user_data['access_token']
    print("Registration successful.")
    
    # 2. Login User
    # Not strictly necessary if register returns token, but good to test independently
    payload = json.dumps({
        "email": email,
        "password": password
    })
    print("Logging in...")
    conn.request("POST", "/auth/login", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    if res.status != 200:
        print(f"Login failed: {res.status} {res.reason}")
        return

    login_data = json.loads(data)
    token = login_data['access_token']
    print("Login successful.")
    
    # 3. Get Profile
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    print("Getting profile...")
    conn.request("GET", "/users/me", headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    if res.status != 200:
        print(f"Get Profile failed: {res.status} {res.reason}")
        print(data.decode("utf-8"))
        return
        
    profile = json.loads(data)
    print(f"Profile retrieved: {profile['email']}")
    assert profile['email'] == email
    
    # 4. Update Profile
    new_location = "Updated City"
    payload = json.dumps({
        "location": new_location
    })
    print("Updating profile...")
    conn.request("PUT", "/users/me", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    if res.status != 200:
        print(f"Update Profile failed: {res.status} {res.reason}")
        print(data.decode("utf-8"))
        return
        
    updated_profile = json.loads(data)
    print(f"Profile updated: {updated_profile['location']}")
    assert updated_profile['location'] == new_location
    
    print("ALL TESTS PASSED!")

if __name__ == "__main__":
    try:
        test_flow()
    except ConnectionRefusedError:
        print("Error: Could not connect to server. Is it running?")
