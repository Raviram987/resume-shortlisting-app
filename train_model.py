import sqlite3
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def extract_features(resume):
    # Assume parsed_skills is a comma-separated string
    required_skills = {"Python", "SQL", "Machine Learning", "Flask"}
    
    parsed_skills = set((resume["parsed_skills"] or "").lower().split(","))
    match_count = len(required_skills.intersection(parsed_skills))

    # Assume parsed_experience is something like '2 years' or just '2'
    try:
        exp = float(resume["parsed_experience"].split()[0])
    except:
        exp = 0

    return [match_count, exp]

# Connect to DB
conn = sqlite3.connect('database.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Fetch only rows where shortlisted_label is set
cursor.execute("SELECT * FROM resumes WHERE shortlisted_label IS NOT NULL")
resumes = cursor.fetchall()

# Build dataset
X, y = [], []
for resume in resumes:
    features = extract_features(resume)
    X.append(features)
    y.append(resume["shortlisted_label"])

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

clf = RandomForestClassifier()
clf.fit(X_train, y_train)

# Save model
joblib.dump(clf, 'shortlist_model.pkl')

print("✅ Model trained and saved as shortlist_model.pkl")
