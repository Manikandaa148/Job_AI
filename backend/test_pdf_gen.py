from fastapi.testclient import TestClient
from main import app
from auth import get_current_user
from models import User
import pytest

# Mock User
def mock_get_current_user():
    return User(
        id=1,
        email="test@example.com",
        full_name="Test User",
        address="123 Test St",
        location="Test City",
        experience_level="Mid-Level",
        _skills='["Python", "React", "FastAPI"]',
        _experience='[{"role": "Software Developer", "company": "Tech Corp", "startDate": "2020", "endDate": "Present", "description": ""}]',
        _education='[{"degree": "B.Tech", "field": "Computer Science", "school": "Tech University", "startDate": "2016", "endDate": "2020", "grade": "8.5"}]'
    )

app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

def test_generate_pdf_modern():
    print("Testing Modern Template PDF Generation...")
    response = client.post(
        "/generate-resume",
        data={"template_id": "modern"}
    )
    if response.status_code == 200:
        print("SUCCESS: Modern PDF Generated. Size:", len(response.content))
        with open("test_modern.pdf", "wb") as f:
            f.write(response.content)
    else:
        print("FAILED: Status", response.status_code)
        print("Response:", response.text)

def test_generate_pdf_classic():
    print("\nTesting Classic Template PDF Generation...")
    response = client.post(
        "/generate-resume",
        data={"template_id": "classic"}
    )
    if response.status_code == 200:
        print("SUCCESS: Classic PDF Generated. Size:", len(response.content))
        with open("test_classic.pdf", "wb") as f:
            f.write(response.content)
    else:
        print("FAILED: Status", response.status_code)
        print("Response:", response.text)

if __name__ == "__main__":
    try:
        test_generate_pdf_modern()
        test_generate_pdf_classic()
    except Exception as e:
        print("An error occurred:", e)
