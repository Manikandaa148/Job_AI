import requests
import json
import time

BASE_URL = "http://localhost:8000"

def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)

def test_profile_update():
    print_header("COMPREHENSIVE PROFILE UPDATE TEST")
    
    # Test 1: Register a fresh user
    print("\n📝 TEST 1: Register Fresh User")
    print("-" * 70)
    
    register_data = {
        "email": "testuser@example.com",
        "password": "test123",
        "full_name": ""  # Start with empty name
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        if response.status_code == 200:
            print("✓ User registered successfully")
            user = response.json()
            print(f"  - Email: {user['email']}")
            print(f"  - Name: '{user.get('full_name', '')}' (should be empty)")
        else:
            print(f"✗ Registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Registration error: {e}")
        return False
    
    # Test 2: Login
    print("\n🔐 TEST 2: Login")
    print("-" * 70)
    
    login_data = {"username": "testuser@example.com", "password": "test123"}
    try:
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✓ Login successful")
            print(f"  - Token: {token[:30]}...")
        else:
            print(f"✗ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Login error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 3: First Profile Update
    print("\n📊 TEST 3: First Profile Update")
    print("-" * 70)
    
    update_data_1 = {
        "full_name": "John Doe",
        "location": "New York",
        "skills": ["Python", "JavaScript"],
        "experience_level": "Mid-Level"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/users/me", json=update_data_1, headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print("✓ Profile updated successfully")
            print(f"  - Name: {profile['full_name']}")
            print(f"  - Location: {profile['location']}")
            print(f"  - Skills: {profile['skills']}")
            print(f"  - Experience Level: {profile['experience_level']}")
        else:
            print(f"✗ Update failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Update error: {e}")
        return False
    
    time.sleep(1)
    
    # Test 4: Verify First Update
    print("\n🔍 TEST 4: Verify First Update Persisted")
    print("-" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print("✓ Profile retrieved")
            
            # Verify all fields
            checks = [
                (profile['full_name'] == "John Doe", f"Name: {profile['full_name']}"),
                (profile['location'] == "New York", f"Location: {profile['location']}"),
                (profile['skills'] == ["Python", "JavaScript"], f"Skills: {profile['skills']}"),
                (profile['experience_level'] == "Mid-Level", f"Experience: {profile['experience_level']}")
            ]
            
            all_passed = True
            for passed, msg in checks:
                status = "✓" if passed else "✗"
                print(f"  {status} {msg}")
                if not passed:
                    all_passed = False
            
            if not all_passed:
                print("\n✗ Data verification FAILED!")
                return False
        else:
            print(f"✗ Failed to retrieve profile: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Retrieval error: {e}")
        return False
    
    time.sleep(1)
    
    # Test 5: Second Profile Update (Different Data)
    print("\n📊 TEST 5: Second Profile Update (Overwrite)")
    print("-" * 70)
    
    update_data_2 = {
        "full_name": "Jane Smith",
        "location": "San Francisco",
        "address": "123 Market St",
        "skills": ["React", "TypeScript", "Node.js"],
        "experience_level": "Senior",
        "education": [
            {
                "id": "1",
                "school": "MIT",
                "degree": "Bachelor's",
                "field": "Computer Science",
                "startDate": "2018",
                "endDate": "2022",
                "grade": "3.9 GPA"
            }
        ],
        "experience": [
            {
                "id": "1",
                "company": "Google",
                "role": "Software Engineer",
                "location": "Mountain View",
                "startDate": "2022-06-01",
                "endDate": "Present",
                "description": "Building scalable systems"
            }
        ],
        "job_preferences": ["Full Stack Developer", "Tech Lead"]
    }
    
    try:
        response = requests.put(f"{BASE_URL}/users/me", json=update_data_2, headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print("✓ Profile updated successfully")
            print(f"  - Name: {profile['full_name']}")
            print(f"  - Location: {profile['location']}")
            print(f"  - Address: {profile['address']}")
            print(f"  - Skills: {profile['skills']}")
            print(f"  - Education: {len(profile['education'])} entries")
            print(f"  - Experience: {len(profile['experience'])} entries")
            print(f"  - Job Preferences: {profile['job_preferences']}")
        else:
            print(f"✗ Update failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Update error: {e}")
        return False
    
    time.sleep(1)
    
    # Test 6: Verify Second Update
    print("\n🔍 TEST 6: Verify Second Update Persisted")
    print("-" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print("✓ Profile retrieved")
            
            # Verify all fields
            checks = [
                (profile['full_name'] == "Jane Smith", f"Name: {profile['full_name']}"),
                (profile['location'] == "San Francisco", f"Location: {profile['location']}"),
                (profile['address'] == "123 Market St", f"Address: {profile['address']}"),
                (len(profile['skills']) == 3, f"Skills count: {len(profile['skills'])}"),
                (len(profile['education']) == 1, f"Education count: {len(profile['education'])}"),
                (len(profile['experience']) == 1, f"Experience count: {len(profile['experience'])}"),
                (len(profile['job_preferences']) == 2, f"Job prefs count: {len(profile['job_preferences'])}")
            ]
            
            all_passed = True
            for passed, msg in checks:
                status = "✓" if passed else "✗"
                print(f"  {status} {msg}")
                if not passed:
                    all_passed = False
            
            if not all_passed:
                print("\n✗ Data verification FAILED!")
                return False
                
            # Show detailed data
            print("\n📋 Detailed Profile Data:")
            print(f"  Education: {profile['education'][0]['school']} - {profile['education'][0]['degree']}")
            print(f"  Experience: {profile['experience'][0]['role']} at {profile['experience'][0]['company']}")
            
        else:
            print(f"✗ Failed to retrieve profile: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Retrieval error: {e}")
        return False
    
    time.sleep(1)
    
    # Test 7: Partial Update
    print("\n📊 TEST 7: Partial Update (Only Name and Skills)")
    print("-" * 70)
    
    update_data_3 = {
        "full_name": "Updated Name",
        "skills": ["Python", "FastAPI", "PostgreSQL"]
    }
    
    try:
        response = requests.put(f"{BASE_URL}/users/me", json=update_data_3, headers=headers)
        if response.status_code == 200:
            profile = response.json()
            print("✓ Partial update successful")
            print(f"  - Name: {profile['full_name']}")
            print(f"  - Skills: {profile['skills']}")
            print(f"  - Location (should remain): {profile['location']}")
            print(f"  - Education (should remain): {len(profile['education'])} entries")
        else:
            print(f"✗ Update failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Update error: {e}")
        return False
    
    time.sleep(1)
    
    # Test 8: Final Verification
    print("\n🔍 TEST 8: Final Verification")
    print("-" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            profile = response.json()
            
            checks = [
                (profile['full_name'] == "Updated Name", f"Name updated: {profile['full_name']}"),
                (profile['location'] == "San Francisco", f"Location preserved: {profile['location']}"),
                (len(profile['education']) == 1, f"Education preserved: {len(profile['education'])} entries"),
                (len(profile['experience']) == 1, f"Experience preserved: {len(profile['experience'])} entries")
            ]
            
            all_passed = True
            for passed, msg in checks:
                status = "✓" if passed else "✗"
                print(f"  {status} {msg}")
                if not passed:
                    all_passed = False
            
            if not all_passed:
                print("\n✗ Final verification FAILED!")
                return False
        else:
            print(f"✗ Failed to retrieve profile: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Retrieval error: {e}")
        return False
    
    return True

# Run the test
if __name__ == "__main__":
    success = test_profile_update()
    
    print_header("TEST RESULTS")
    if success:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n✓ Profile updates are working correctly")
        print("✓ Data persists across multiple updates")
        print("✓ Partial updates preserve existing data")
        print("✓ Complex data (education, experience) saves properly")
    else:
        print("\n❌ TESTS FAILED!")
        print("\nPlease check the errors above for details.")
    
    print("\n" + "=" * 70)
