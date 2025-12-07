import sys
try:
    from main import app
    from schemas import UserCreate
    from models import User
    from database import SessionLocal, engine
    import auth
    print("Imports successful")
    
    # Test Pydantic
    try:
        u = UserCreate(email="test@example.com", password="password", full_name="Test")
        print("Pydantic model created")
    except Exception as e:
        print(f"Pydantic error: {e}")

    # Test DB
    try:
        db = SessionLocal()
        print("DB Session created")
        db.close()
    except Exception as e:
        print(f"DB error: {e}")

except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
