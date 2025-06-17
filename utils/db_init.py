import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        skills TEXT NOT NULL,
        posted_by TEXT NOT NULL,  -- email of the recruiter who posted
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS resumes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        parsed_name TEXT,
        parsed_email TEXT,
        parsed_skills TEXT,
        uploaded_by TEXT NOT NULL,
        upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')



# Safely add the 'shortlisted' column if not already present
try:
    cursor.execute("ALTER TABLE resumes ADD COLUMN shortlisted TEXT DEFAULT 'no'")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column 'shortlisted' already exists.")
    else:
        raise
cursor.execute("SELECT COUNT(*) FROM resumes WHERE shortlisted = 'yes'")

conn.commit()
conn.close()
print("✅ Database initialized.")
