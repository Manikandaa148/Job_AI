import requests
import json
import os

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_complete_flow():
    """Test complete profile update and PDF generation flow"""
    
    print_section("COMPREHENSIVE TEST: PROFILE UPDATE & PDF GENERATION")
    
    # Step 1: Register/Login
    print("\n1️⃣  AUTHENTICATION")
    print("-" * 70)
    
    # Try to register a new user
    register_data = {
        "email": "testuser@jobai.com",
        "password": "test123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/register", json=register_data)
        if response.status_code == 200:
            print("✓ New user registered successfully")
        else:
            print(f"ℹ User already exists, proceeding to login...")
    except Exception as e:
        print(f"⚠ Registration: {e}")
    
    # Login
    login_data = {"username": "testuser@jobai.com", "password": "test123"}
    try:
        response = requests.post(f"{BASE_URL}/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"✓ Login successful")
            print(f"  Token: {token[:30]}...")
        else:
            print(f"✗ Login failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"✗ Login error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Update Profile with Complete Data
    print("\n2️⃣  PROFILE UPDATE (Complete Data)")
    print("-" * 70)
    
    profile_data = {
        "full_name": "John Doe",
        "location": "San Francisco, CA",
        "address": "123 Tech Street",
        "experience_level": "Senior",
        "skills": ["Python", "JavaScript", "React", "FastAPI", "PostgreSQL"],
        "education": [
            {
                "id": "1",
                "school": "Stanford University",
                "degree": "Bachelor's",
                "field": "Computer Science",
                "startDate": "2015",
                "endDate": "2019",
                "grade": "3.8 GPA"
            }
        ],
        "experience": [
            {
                "id": "1",
                "company": "Google",
                "role": "Senior Software Engineer",
                "location": "Mountain View, CA",
                "startDate": "2019-06-01",
                "endDate": "Present",
                "description": "Led development of scalable microservices architecture serving millions of users"
            }
        ],
        "projects": [
            {
                "id": "1",
                "name": "Job AI Platform",
                "role": "Lead Developer",
                "duration": "Dec 2024 - Present",
                "technologies": ["React", "FastAPI", "PostgreSQL", "Docker"],
                "description": "Built a comprehensive job search platform with AI-powered recommendations and multi-platform aggregation",
                "link": "https://github.com/test/job-ai"
            }
        ],
        "job_preferences": ["Full Stack Developer", "Tech Lead"]
    }
    
    try:
        response = requests.put(f"{BASE_URL}/users/me", json=profile_data, headers=headers)
        if response.status_code == 200:
            user = response.json()
            print("✓ Profile updated successfully")
            print(f"  Name: {user['full_name']}")
            print(f"  Location: {user['location']}")
            print(f"  Skills: {len(user['skills'])} skills")
            print(f"  Education: {len(user['education'])} entries")
            print(f"  Experience: {len(user['experience'])} entries")
            print(f"  Projects: {len(user['projects'])} projects")
        else:
            print(f"✗ Profile update failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Update error: {e}")
        return False
    
    # Step 3: Verify Profile Persistence
    print("\n3️⃣  VERIFY PROFILE PERSISTENCE")
    print("-" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        if response.status_code == 200:
            user = response.json()
            print("✓ Profile retrieved successfully")
            
            # Verify all fields
            checks = [
                (user['full_name'] == "John Doe", f"Name: {user['full_name']}"),
                (user['location'] == "San Francisco, CA", f"Location: {user['location']}"),
                (len(user['skills']) == 5, f"Skills: {len(user['skills'])} items"),
                (len(user['education']) == 1, f"Education: {len(user['education'])} entries"),
                (len(user['experience']) == 1, f"Experience: {len(user['experience'])} entries"),
                (len(user['projects']) == 1, f"Projects: {len(user['projects'])} projects"),
            ]
            
            all_passed = True
            for passed, msg in checks:
                status = "✓" if passed else "✗"
                print(f"  {status} {msg}")
                if not passed:
                    all_passed = False
            
            if not all_passed:
                print("\n✗ Profile verification FAILED!")
                return False
        else:
            print(f"✗ Failed to retrieve profile: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Verification error: {e}")
        return False
    
    # Step 4: Generate PDF Resume (Modern Template)
    print("\n4️⃣  PDF GENERATION - MODERN TEMPLATE")
    print("-" * 70)
    
    try:
        form_data = {
            'template_id': 'modern'
        }
        response = requests.post(
            f"{BASE_URL}/generate-resume",
            data=form_data,
            headers=headers
        )
        
        if response.status_code == 200:
            # Save PDF
            pdf_path = "test_resume_modern.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(pdf_path)
            print(f"✓ Modern template PDF generated successfully")
            print(f"  File: {pdf_path}")
            print(f"  Size: {file_size:,} bytes")
            
            if file_size < 1000:
                print(f"  ⚠ Warning: PDF seems too small ({file_size} bytes)")
                return False
        else:
            print(f"✗ PDF generation failed: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"✗ PDF generation error: {e}")
        return False
    
    # Step 5: Generate PDF Resume (Classic Template)
    print("\n5️⃣  PDF GENERATION - CLASSIC TEMPLATE")
    print("-" * 70)
    
    try:
        form_data = {
            'template_id': 'classic'
        }
        response = requests.post(
            f"{BASE_URL}/generate-resume",
            data=form_data,
            headers=headers
        )
        
        if response.status_code == 200:
            # Save PDF
            pdf_path = "test_resume_classic.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            file_size = os.path.getsize(pdf_path)
            print(f"✓ Classic template PDF generated successfully")
            print(f"  File: {pdf_path}")
            print(f"  Size: {file_size:,} bytes")
            
            if file_size < 1000:
                print(f"  ⚠ Warning: PDF seems too small ({file_size} bytes)")
                return False
        else:
            print(f"✗ PDF generation failed: {response.status_code}")
            print(f"  Response: {response.text[:500]}")
            return False
    except Exception as e:
        print(f"✗ PDF generation error: {e}")
        return False
    
    return True

# Run the test
if __name__ == "__main__":
    success = test_complete_flow()
    
    print_section("TEST RESULTS")
    if success:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("\n✓ Profile updates are working correctly")
        print("✓ Data persists across requests")
        print("✓ PDF generation is working for both templates")
        print("✓ Projects section is included in the data")
        print("\nGenerated files:")
        print("  - test_resume_modern.pdf")
        print("  - test_resume_classic.pdf")
    else:
        print("\n❌ TESTS FAILED!")
        print("\nPlease check the errors above for details.")
    
    print("\n" + "=" * 70)
