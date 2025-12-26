import sqlite3
import os

db_path = 'job_ai.db'

if not os.path.exists(db_path):
    print(f"Database {db_path} not found!")
    exit(1)

conn = sqlite3.connect(db_path)
c = conn.cursor()

print("Migrating database...")

try:
    c.execute('ALTER TABLE users ADD COLUMN total_experience TEXT')
    print("Added total_experience column")
except sqlite3.OperationalError as e:
    print(f"Skipping total_experience: {e}")

try:
    c.execute('ALTER TABLE users ADD COLUMN preferred_locations TEXT')
    print("Added preferred_locations column")
except sqlite3.OperationalError as e:
    print(f"Skipping preferred_locations: {e}")

conn.commit()
conn.close()
print("Migration complete.")
