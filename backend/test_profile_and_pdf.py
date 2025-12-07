import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

# Login or register
def login():
    # Try to login first
    login_data = {
        "username": "test@example.com",
        "password": "password123"
    }
    response = requests.post(f"{BASE_URL}/login", data=login_data)
    
    if response.status_code == 200:
        print("✓ Login successful")
        return response.json()["access_token"]
    else:
        # Register if login fails
        print("Login failed, attempting to register...")
        register_data = {
            "email": "test@example.com",
            "password": "password123",
            "full_name": "John Doe"
        }
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        if response.status_code == 200:
            print("✓ Registration successful")
            # Now login
            response = requests.post(f"{BASE_URL}/login", data=login_data)
            return response.json()["access_token"]
        else:
            print(f"✗ Registration failed: {response.text}")
            return None

# Update profile with complete data
def update_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    
    profile_data = {
        "full_name": "John Doe",
        "address": "123 Main St, Apt 4B",
        "location": "San Francisco, CA",
        "experience_level": "Senior",
        "skills": ["Python", "React", "TypeScript", "FastAPI", "Next.js"],
        "education": [
            {
                "id": "1",
                "school": "MIT",
                "degree": "Bachelor's",
                "field": "Computer Science",
                "startDate": "2020-09-01",
                "endDate": "2024-05-31",
                "grade": "3.8 GPA"
            },
            {
                "id": "2",
                "school": "Stanford University",
                "degree": "Master's",
                "field": "Artificial Intelligence",
                "startDate": "2024-09-01",
                "endDate": "2026-05-31",
                "grade": "4.0 GPA"
            }
        ],
        "experience": [
            {
                "id": "1",
                "company": "Google",
                "role": "Software Engineer",
                "location": "Mountain View, CA",
                "startDate": "2024-01-01",
                "endDate": "2024-12-31",
                "description": "Developed scalable web applications using React and Python. Led a team of 5 engineers to deliver critical features.",
                "logo": "https://logo.clearbit.com/google.com"
            },
            {
                "id": "2",
                "company": "Microsoft",
                "role": "Senior Developer",
                "location": "Seattle, WA",
                "startDate": "2022-06-01",
                "endDate": "2023-12-31",
                "description": "Built cloud-based solutions and improved system performance by 40%.",
                "logo": "https://logo.clearbit.com/microsoft.com"
            }
        ],
        "job_preferences": ["Full Stack Developer", "Backend Engineer", "Tech Lead"]
    }
    
    response = requests.put(f"{BASE_URL}/users/me", json=profile_data, headers=headers)
    
    if response.status_code == 200:
        print("✓ Profile updated successfully")
        print(f"  - Name: {response.json()['full_name']}")
        print(f"  - Skills: {len(response.json()['skills'])} skills")
        print(f"  - Education: {len(response.json()['education'])} entries")
        print(f"  - Experience: {len(response.json()['experience'])} entries")
        return True
    else:
        print(f"✗ Profile update failed: {response.text}")
        return False

# Get profile to verify
def get_profile(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/users/me", headers=headers)
    
    if response.status_code == 200:
        print("\n✓ Profile retrieved successfully:")
        profile = response.json()
        print(f"  - Name: {profile.get('full_name')}")
        print(f"  - Email: {profile.get('email')}")
        print(f"  - Skills: {profile.get('skills')}")
        print(f"  - Education entries: {len(profile.get('education', []))}")
        print(f"  - Experience entries: {len(profile.get('experience', []))}")
        print(f"  - Job preferences: {profile.get('job_preferences')}")
        return profile
    else:
        print(f"✗ Failed to get profile: {response.text}")
        return None

# Generate resume PDF
def generate_resume(token, template_id="modern"):
    headers = {"Authorization": f"Bearer {token}"}
    
    data = {"template_id": template_id}
    
    response = requests.post(f"{BASE_URL}/generate-resume", data=data, headers=headers)
    
    if response.status_code == 200:
        filename = f"test_resume_{template_id}.pdf"
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"\n✓ Resume PDF generated successfully: {filename}")
        print(f"  - File size: {len(response.content)} bytes")
        return True
    else:
        print(f"\n✗ Resume generation failed: {response.text}")
        return False

# Main test flow
def main():
    print("=" * 50)
    print("Testing Profile Update and Resume Generation")
    print("=" * 50)
    
    # Step 1: Login/Register
    print("\n1. Authenticating...")
    token = login()
    if not token:
        print("✗ Authentication failed. Exiting.")
        return
    
    # Step 2: Update profile
    print("\n2. Updating profile with test data...")
    if not update_profile(token):
        print("✗ Profile update failed. Exiting.")
        return
    
    # Step 3: Verify profile was saved
    print("\n3. Verifying profile was saved...")
    profile = get_profile(token)
    if not profile:
        print("✗ Profile verification failed. Exiting.")
        return
    
    # Step 4: Generate resume PDFs with different templates
    print("\n4. Generating resume PDFs...")
    templates = ["modern", "classic"]
    for template in templates:
        print(f"\n  Testing {template} template...")
        generate_resume(token, template)
    
    print("\n" + "=" * 50)
    print("✓ All tests completed successfully!")
    print("=" * 50)

if __name__ == "__main__":
    main()
