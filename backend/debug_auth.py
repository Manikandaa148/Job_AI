import auth
try:
    hash = auth.get_password_hash("password123")
    print(f"Hash created: {hash}")
    verify = auth.verify_password("password123", hash)
    print(f"Verify: {verify}")
except Exception as e:
    print(f"Auth error: {e}")
    import traceback
    traceback.print_exc()
