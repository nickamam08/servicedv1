
import requests
import json
import sys

BASE_URL = "http://localhost:8000/api/v1"

def register_or_login(email, password, role):
    # Try login first
    resp = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": password})
    if resp.status_code == 200:
        return resp.json()
    
    # Register if login fails
    print(f"Login failed, registering {email}...")
    resp = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": f"Test {role.capitalize()}",
        "role": role
    })
    if resp.status_code != 200:
        print(f"Registration failed for {email}: {resp.text}")
        sys.exit(1)
    return resp.json()

def main():
    # 1. Login as Client
    print("--- Login/Register Client ---")
    client_auth = register_or_login("client_chat_test@test.com", "password123", "client")
    client_token = client_auth["access_token"]
    client_id = client_auth["user"]["id"]
    print(f"Client ID: {client_id}")

    # 2. Login as Provider
    print("\n--- Login/Register Provider ---")
    provider_auth = register_or_login("provider_chat_test@test.com", "password123", "provider")
    provider_token = provider_auth["access_token"]
    provider_id = provider_auth["user"]["id"]
    print(f"Provider ID: {provider_id}")

    # 3. Client creates conversation with Provider
    print(f"\n--- Client creating conversation with Provider {provider_id} ---")
    headers_client = {"Authorization": f"Bearer {client_token}"}
    resp = requests.post(f"{BASE_URL}/conversations", json={"provider_id": provider_id}, headers=headers_client)
    if resp.status_code not in [200, 201]:
        print(f"Failed to create conversation: {resp.text}")
        sys.exit(1)
    
    conversation = resp.json()
    conv_id = conversation["id"]
    print(f"Conversation ID: {conv_id}")

    # 4. Client sends message
    print("\n--- Client sending message 'Hello from Client' ---")
    resp = requests.post(f"{BASE_URL}/conversations/messages/send", 
                         json={"conversation_id": conv_id, "content": "Hello from Client"},
                         headers=headers_client)
    msg_client = resp.json()
    print(f"Client Msg Sender ID: {msg_client['sender_id']}")

    # 5. Provider sends message
    print("\n--- Provider sending message 'Hello from Provider' ---")
    headers_provider = {"Authorization": f"Bearer {provider_token}"}
    resp = requests.post(f"{BASE_URL}/conversations/messages/send", 
                         json={"conversation_id": conv_id, "content": "Hello from Provider"},
                         headers=headers_provider)
    msg_provider = resp.json()
    print(f"Provider Msg Sender ID: {msg_provider['sender_id']}")

    # 6. Fetch messages as Provider to verify view
    print("\n--- Fetching messages as Provider ---")
    resp = requests.get(f"{BASE_URL}/conversations/{conv_id}/messages", headers=headers_provider)
    messages = resp.json()
    
    print(f"Fetched {len(messages)} messages.")
    for m in messages:
        sender = m['sender_id']
        is_mine = (sender == provider_id)
        side = "RIGHT (Sent)" if is_mine else "LEFT (Received)"
        content = m['content']
        print(f"Msg: {content} | Sender: {sender} | Me (Provider): {provider_id} | IsMine: {is_mine} -> Should be {side}")
        sys.stdout.flush()
        
        if content == "Hello from Client" and is_mine:
            print("CRITICAL ERROR: Client message marked as Mine!")
        if content == "Hello from Provider" and not is_mine:
            print("CRITICAL ERROR: Provider message marked as Receive!")

if __name__ == "__main__":
    main()
