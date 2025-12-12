"""
Quick script to create a test user in the database
"""
import sys
sys.path.append('.')

from database import SessionLocal
from models import User
from auth import get_password_hash

def create_test_user():
    db = SessionLocal()
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        print("Test user already exists!")
        print(f"Email: test@example.com")
        print(f"Password: password123")
        db.close()
        return
    
    # Create new user
    hashed_password = get_password_hash("password123")
    new_user = User(
        email="test@example.com",
        hashed_password=hashed_password,
        full_name="Test User"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print("✅ Test user created successfully!")
    print(f"Email: test@example.com")
    print(f"Password: password123")
    print(f"User ID: {new_user.id}")
    
    db.close()

if __name__ == "__main__":
    create_test_user()
