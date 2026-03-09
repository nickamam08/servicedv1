import requests

def test_validation_error_code():
    url = "http://localhost:8000/api/v1/auth/register"
    # Invalid phone (11 digits) should trigger ValueError in schema
    payload = {
        "full_name": "Test User",
        "email": "valid@example.com",
        "password": "Password123!",
        "phone": "30012345678", # 11 digits
        "location": "Test City",
        "role": "client"
    }
    
    print(f"Testing registration with INVALID phone: {payload['phone']}")
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_validation_error_code()
