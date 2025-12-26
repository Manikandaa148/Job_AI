import sqlite3
import os

db_path = 'job_ai.db'

if not os.path.exists(db_path):
    print(f"Database {db_path} not found!")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

print("Migrating database for resume_score...")

try:
    c.execute('ALTER TABLE users ADD COLUMN resume_score INTEGER')
    print("Added resume_score column")
except sqlite3.OperationalError as e:
    print(f"Skipping resume_score: {e}")

conn.commit()
conn.close()
print("Migration complete.")
