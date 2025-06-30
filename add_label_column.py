import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE resumes ADD COLUMN shortlisted_label INTEGER DEFAULT NULL")
    print("✅ 'shortlisted_label' column added.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("ℹ️ Column already exists.")
    else:
        raise

conn.commit()
conn.close()
