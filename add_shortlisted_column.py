import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Check if 'shortlisted' column already exists
cursor.execute("PRAGMA table_info(resumes);")
columns = [col[1] for col in cursor.fetchall()]

if 'shortlisted' not in columns:
    cursor.execute("ALTER TABLE resumes ADD COLUMN shortlisted TEXT DEFAULT 'no'")
    conn.commit()
    print("✅ 'shortlisted' column added to resumes table.")
else:
    print("ℹ️ 'shortlisted' column already exists.")

conn.close()
