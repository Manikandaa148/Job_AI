"""
Delete and recreate test user with proper password hashing
"""
import sys
sys.path.append('.')

from database import SessionLocal
from models import User
from auth import get_password_hash

def reset_test_user():
    db = SessionLocal()
    
    # Delete existing test user
    existing_user = db.query(User).filter(User.email == "test@example.com").first()
    if existing_user:
        db.delete(existing_user)
        db.commit()
        print("✅ Deleted old test user")
    
    # Create new user with proper password hashing
    hashed_password = get_password_hash("password123")
    new_user = User(
        email="test@example.com",
        hashed_password=hashed_password,
        full_name="Test User"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print("✅ Test user recreated successfully!")
    print(f"Email: test@example.com")
    print(f"Password: password123")
    print(f"User ID: {new_user.id}")
    print(f"Hash length: {len(hashed_password)}")
    
    db.close()

if __name__ == "__main__":
    reset_test_user()
