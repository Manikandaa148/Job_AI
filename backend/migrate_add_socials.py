import sqlite3

def migrate():
    print("Migrating social media columns...")
    conn = sqlite3.connect('job_ai.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN linkedin_url TEXT")
        print("Added linkedin_url column")
    except sqlite3.OperationalError:
        print("linkedin_url column already exists")
        
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN github_url TEXT")
        print("Added github_url column")
    except sqlite3.OperationalError:
        print("github_url column already exists")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN portfolio_url TEXT")
        print("Added portfolio_url column")
    except sqlite3.OperationalError:
        print("portfolio_url column already exists")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
