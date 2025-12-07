import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TESTING PROFILE UPDATE WITH GUEST ACCOUNT")
print("=" * 60)

# Step 1: Register/Login guest user
print("\n1. Logging in as guest...")
try:
    # Try login first
    login_data = {"username": "guest@jobai.com", "password": "guest123"}
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✓ Guest user logged in successfully")
    else:
        # Register if login fails
        print("Guest not found, registering...")
        register_data = {
            "email": "guest@jobai.com",
            "password": "guest123",
            "full_name": "Guest User"
        }
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        if response.status_code == 200:
            print("✓ Guest user registered")
            # Now login
            response = requests.post(f"{BASE_URL}/login", data=login_data)
            token = response.json()["access_token"]
            print("✓ Guest user logged in")
        else:
            print(f"✗ Registration failed: {response.text}")
            exit(1)
except Exception as e:
    print(f"✗ Login/Register failed: {e}")
    exit(1)

# Step 2: Update profile
print("\n2. Updating profile...")
headers = {"Authorization": f"Bearer {token}"}

update_data = {
    "full_name": "Test User Fixed",
    "location": "San Francisco",
    "skills": ["Python", "JavaScript", "React"]
}

try:
    response = requests.put(f"{BASE_URL}/users/me", json=update_data, headers=headers)
    
    if response.status_code == 200:
        print("✓ Profile updated successfully")
        profile = response.json()
        print(f"  - Name: {profile['full_name']}")
        print(f"  - Location: {profile['location']}")
        print(f"  - Skills: {profile['skills']}")
    else:
        print(f"✗ Profile update failed: {response.status_code}")
        print(f"  Response: {response.text}")
        exit(1)
except Exception as e:
    print(f"✗ Update failed: {e}")
    exit(1)

# Step 3: Verify by fetching profile again
print("\n3. Verifying profile was saved...")
try:
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if response.status_code == 200:
        profile = response.json()
        print("✓ Profile retrieved successfully")
        print(f"  - Name: {profile['full_name']}")
        print(f"  - Location: {profile['location']}")
        print(f"  - Skills: {profile['skills']}")
        
        # Verify the data matches
        if (profile['full_name'] == "Test User Fixed" and 
            profile['location'] == "San Francisco" and 
            "Python" in profile['skills']):
            print("\n✓✓✓ ALL DATA PERSISTED CORRECTLY! ✓✓✓")
        else:
            print("\n✗ Data did not persist correctly")
    else:
        print(f"✗ Failed to retrieve profile: {response.status_code}")
        exit(1)
except Exception as e:
    print(f"✗ Verification failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("TEST COMPLETED SUCCESSFULLY!")
print("=" * 60)
