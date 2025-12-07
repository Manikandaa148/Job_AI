import sqlite3

# Connect to the database
conn = sqlite3.connect('job_ai.db')
cursor = conn.cursor()

try:
    # Check if projects column exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'projects' not in columns:
        print("Adding 'projects' column to users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN projects TEXT DEFAULT '[]'")
        conn.commit()
        print("✓ Column added successfully")
    else:
        print("✓ 'projects' column already exists")
    
    # Verify
    cursor.execute("PRAGMA table_info(users)")
    print("\nCurrent table schema:")
    for column in cursor.fetchall():
        print(f"  - {column[1]} ({column[2]})")
    
except Exception as e:
    print(f"✗ Error: {e}")
finally:
    conn.close()
