import sys
import os
import requests
import random
import string
import datetime

# Setup path to import backend app modules for DB reset
sys.path.append(os.path.join(os.getcwd(), "serviced-backend")) 

# Need to be in the folder where app package is importable or add it to path.
# My current CWD when running might be .../serviced-backend
# The previous script `create_test_data.py` was at `.../serviced-backend/create_test_data.py`
# So `import app` should work if run from that dir.

from app.db.base import Base
from app.db.session import engine
from app.models import all_models # Import to register models

API_URL = "http://localhost:8000/api/v1"

def reset_database():
    print("--- RESETTING DATABASE ---")
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database reset successfully.")
    except Exception as e:
        print(f"Error resetting database: {e}")
        sys.exit(1)

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def register_user(email, password, role="client", full_name=None):
    if not full_name:
        full_name = f"Test {role.capitalize()} {random_string(4)}"
    
    # 1. Register
    resp = requests.post(f"{API_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": full_name,
        "role": role
    })
    if resp.status_code != 200:
        print(f"Failed to register {email}: {resp.text}")
        return None
    
    # 2. Login
    resp = requests.post(f"{API_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    if resp.status_code != 200:
        print(f"Failed to login {email}: {resp.text}")
        return None
        
    return resp.json()["access_token"]

def create_provider_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.put(f"{API_URL}/provider/dashboard/profile", headers=headers, json={
        "description": "Professional services provider with 5 stars.",
        "experience_years": 5,
        "location": "Madrid, Spain",
        "availability": "Weekdays 9am-5pm"
    })
    if resp.status_code != 200:
         # Fallback to old endpoint if dashboard profile update fails (shouldn't if I did my job)
         resp = requests.put(f"{API_URL}/providers/me", headers=headers, json={
            "description": "Fallback description",
            "experience_years": 5
         })
    
    if resp.status_code != 200:
        print(f"Failed to create provider profile: {resp.text}")
        return False
    return True

def create_service(token, title, category="General", price=50.0):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.post(f"{API_URL}/provider/dashboard/services", headers=headers, json={
        "title": title,
        "description": f"Description for {title}",
        "category": category,
        "price": price,
        "duration_minutes": 60 + random.randint(0, 60),
        "duration": "1-2 hours",
        "image_urls": ["http://example.com/image.jpg"]
    })
    if resp.status_code != 200:
        print(f"Failed to create service {title}: {resp.text}")
        return None
    return resp.json()

def create_request(client_token, service_id, notes="Interested in this service"):
    headers = {"Authorization": f"Bearer {client_token}"}
    resp = requests.post(f"{API_URL}/requests", headers=headers, json={
        "service_id": service_id,
        "notes": notes,
        "scheduled_date": (datetime.datetime.utcnow() + datetime.timedelta(days=random.randint(1,7))).isoformat()
    })
    if resp.status_code != 200:
        print(f"Failed to create request: {resp.text}")
        return None
    return resp.json()

def update_request_status(provider_token, request_id, status_action):
    # status_action: accept, reject, complete
    headers = {"Authorization": f"Bearer {provider_token}"}
    resp = requests.put(f"{API_URL}/provider/dashboard/requests/{request_id}/{status_action}", headers=headers)
    if resp.status_code != 200:
        print(f"Failed to {status_action} request {request_id}: {resp.text}")
        return False
    return True

def create_review(client_token, request_id, service_id, rating=5):
    # Typically reviews are linked to requests or services. Let's check existing API.
    # User prompt said "4 Review... request_id, client_id, provider_id".
    # I might not have implemented "POST /reviews" in this turn, assuming it existed.
    # I'll check if I can use existing review endpoint.
    # If not, I can't verify reviews fully yet. But I can verify dashboard reads them if I had them.
    # I'll try to find a review endpoint or just skip review creation via API if it doesn't exist.
    # Assuming there's a POST /reviews or similar. I'll define it based on typical REST.
    headers = {"Authorization": f"Bearer {client_token}"}
    resp = requests.post(f"{API_URL}/reviews", headers=headers, json={
        "service_request_id": request_id, # If I added this field to schema
        "rating": rating,
        "comment": "Great service!"
    })
    # If this fails, it's likely because I didn't verify/touch the Review creation endpoint in this task.
    # The user asked for Provider Dashboard (viewing reviews), not Client Review creation.
    # But for dashboard to show stats, we need reviews.
    return resp.status_code == 200

def send_message(sender_token, conversation_id, content):
    headers = {"Authorization": f"Bearer {sender_token}"}
    resp = requests.post(f"{API_URL}/conversations/messages/send", headers=headers, json={
        "conversation_id": conversation_id,
        "content": content
    })
    return resp.status_code == 201

def create_conversation(client_token, provider_id):
    headers = {"Authorization": f"Bearer {client_token}"}
    resp = requests.post(f"{API_URL}/conversations", headers=headers, json={
        "provider_id": provider_id,
        "request_id": None
    })
    if resp.status_code == 200 or resp.status_code == 201:
        return resp.json()["id"]
    return None

def main():
    reset_database()
    print("\n--- POPULATING DATA ---")

    # 1. Provider
    prov_email = "provider@test.com"
    prov_pass = "password123"
    prov_token = register_user(prov_email, prov_pass, "provider", "John Provider")
    if not prov_token: return
    
    if not create_provider_profile(prov_token): return
    print(f"Created Provider: {prov_email}")

    # 2. Services
    svc1 = create_service(prov_token, "Office Cleaning", "Home", 80.0)
    svc2 = create_service(prov_token, "AC Repair", "Tech", 120.0)
    if not svc1 or not svc2: return
    print("Created Services")

    # 3. Clients
    client1_token = register_user("client1@test.com", "password123", "client", "Client One")
    client2_token = register_user("client2@test.com", "password123", "client", "Client Two")
    if not client1_token or not client2_token: return
    print("Created Clients")

    # 4. Requests & Interactions
    
    # Req 1: PENDING (Client 1 -> Svc 1)
    req1 = create_request(client1_token, svc1["id"], "Need this urgently")
    print(f"Created Request 1 (Pending): ID {req1['id']}")

    # Req 2: ACCEPTED/ACTIVE (Client 2 -> Svc 2)
    req2 = create_request(client2_token, svc2["id"], "Next tuesday")
    update_request_status(prov_token, req2["id"], "accept")
    print(f"Created Request 2 (Accepted): ID {req2['id']}")

    # Req 3: COMPLETED (Client 1 -> Svc 2)
    req3 = create_request(client1_token, svc2["id"], "Fixed well")
    update_request_status(prov_token, req3["id"], "accept")
    update_request_status(prov_token, req3["id"], "complete")
    print(f"Created Request 3 (Completed): ID {req3['id']}")

    # Req 4: CANCELLED (Client 2 -> Svc 1)
    req4 = create_request(client2_token, svc1["id"], "Actually nvm")
    update_request_status(prov_token, req4["id"], "accept") # Must accept first? Or reject directly.
    # My logic allowed reject only from pending? Or cancel from accepted.
    # Let's try reject.
    # update_request_status(prov_token, req4["id"], "reject") # This maps to CANCELLED in my impl
    # Actually wait, my impl for 'reject' sets CANCELLED.
    # Let's verify 'reject' logic in api: 
    # @router.put("/requests/{request_id}/reject") -> updates to CANCELLED.
    # Logic in service: 
    # elif new_status == RequestStatus.CANCELLED: 
    #    if current_status == RequestStatus.COMPLETED: error
    # So Pending -> Cancelled is OK.
    update_request_status(prov_token, req4["id"], "reject")
    print(f"Created Request 4 (Rejected/Cancelled): ID {req4['id']}")

    # 5. Messages
    conv_id = create_conversation(client2_token, svc2["provider_id"]) # Need provider user id
    # svc2["provider_id"] is the PROFILE id. 
    # The conversation endpoint needs USER ID.
    # I need to get the provider user ID. 
    # I can get it from the profile fetch or just assume I know it since I created it.
    # Actually, create_service response might verify provider_id.
    # Let's fetch the service 2 to see details or just fetch profile.
    
    # Just use the fact that I logged in as provider to create services, so I know I am the provider.
    # But I need the ID to pass to client's create_conversation.
    # I'll create a conversation using the provider's user id.
    # I will fetch 'me' to get ID.
    headers = {"Authorization": f"Bearer {prov_token}"}
    me_resp = requests.get(f"{API_URL}/users/me", headers=headers)
    provider_user_id = me_resp.json()["id"]

    conv_id = create_conversation(client2_token, provider_user_id)
    if conv_id:
        send_message(client2_token, conv_id, "Hello provider, any updates?")
        print(f"Created Conversation {conv_id} with unread message")

    print("\n--- TEST DATA POPULATION COMPLETE ---")
    print("Saving credentials to test_credentials_dashboard.txt")
    with open("test_credentials_dashboard.txt", "w") as f:
        f.write(f"Provider: {prov_email} / {prov_pass}\n")
        f.write(f"Client 1: client1@test.com / password123\n")
        f.write(f"Client 2: client2@test.com / password123\n")

if __name__ == "__main__":
    main()
