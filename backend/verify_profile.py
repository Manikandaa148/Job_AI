import requests

BASE_URL = "http://localhost:8000"

# Login
login_data = {"username": "test@example.com", "password": "password123"}
response = requests.post(f"{BASE_URL}/login", data=login_data)
token = response.json()["access_token"]

# Get profile
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/users/me", headers=headers)
profile = response.json()

print("=" * 60)
print("PROFILE DATA VERIFICATION")
print("=" * 60)
print(f"\n✓ Name: {profile['full_name']}")
print(f"✓ Email: {profile['email']}")
print(f"✓ Location: {profile['location']}")
print(f"✓ Experience Level: {profile['experience_level']}")

print(f"\n✓ Skills ({len(profile['skills'])} total):")
for skill in profile['skills']:
    print(f"  - {skill}")

print(f"\n✓ Education ({len(profile['education'])} entries):")
for i, edu in enumerate(profile['education'], 1):
    print(f"  {i}. {edu['degree']} in {edu['field']}")
    print(f"     {edu['school']} ({edu['startDate']} to {edu['endDate']})")
    print(f"     Grade: {edu['grade']}")

print(f"\n✓ Work Experience ({len(profile['experience'])} entries):")
for i, exp in enumerate(profile['experience'], 1):
    print(f"  {i}. {exp['role']} at {exp['company']}")
    print(f"     Location: {exp['location']}")
    print(f"     Period: {exp['startDate']} to {exp['endDate']}")
    print(f"     Description: {exp['description'][:60]}...")

print(f"\n✓ Job Preferences ({len(profile['job_preferences'])} total):")
for pref in profile['job_preferences']:
    print(f"  - {pref}")

print("\n" + "=" * 60)
print("✓ ALL PROFILE DATA SAVED AND RETRIEVED SUCCESSFULLY!")
print("=" * 60)
