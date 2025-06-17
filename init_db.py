# ... Your table creation code

# Check columns in resumes
cursor.execute("PRAGMA table_info(resumes);")
columns = cursor.fetchall()

print("📊 Columns in 'resumes':")
for col in columns:
    print(f" - {col[1]} ({col[2]})")

conn.close()
