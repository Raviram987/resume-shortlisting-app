from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
import sqlite3
import bcrypt
import os
from werkzeug.utils import secure_filename
import pdfkit
from parsing_utils import extract_text_from_pdf, extract_text_from_docx, extract_skills, extract_experience
from matching_utils import match_resumes

app = Flask(__name__)
app.secret_key = 'supersecretkey123'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/landing')
def landing():
    return render_template('landing.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hashed = bcrypt.hashpw(password, bcrypt.gensalt())

        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed))
            conn.commit()
            flash('Registered successfully! Please login.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and bcrypt.checkpw(password, user['password']):
            session['user'] = user['email']
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.')
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    user_email = session['user']
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    total_jobs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM resumes")
    total_resumes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM resumes WHERE shortlisted = 'yes'")
    shortlisted_count = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT 5")
    recent_jobs = cursor.fetchall()
    conn.close()

    return render_template('dashboard.html',
                           user=user_email,
                           total_jobs=total_jobs,
                           total_resumes=total_resumes,
                           shortlisted_count=shortlisted_count,
                           recent_jobs=recent_jobs)

@app.route('/post-job', methods=['GET', 'POST'])
def post_job():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        skills = request.form['skills']
        posted_by = session['user']

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO jobs (title, description, skills, posted_by, created_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (title, description, skills, posted_by))
        conn.commit()
        conn.close()

        flash('Job posted successfully!')
        return redirect(url_for('list_jobs'))

    return render_template('post_job.html')

@app.route('/jobs')
def list_jobs():
    conn = get_db_connection()
    jobs = conn.execute('SELECT * FROM jobs ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('jobs.html', jobs=jobs)

@app.route('/upload', methods=['GET', 'POST'])
def upload_resume():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        uploaded_file = request.files['resume']
        uploaded_by = session.get('user')

        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(filepath)

            if filename.endswith('.pdf'):
                text = extract_text_from_pdf(filepath)
            elif filename.endswith('.docx'):
                text = extract_text_from_docx(filepath)
            else:
                text = ''

            skills = extract_skills(text)
            experience = extract_experience(text)

            conn = get_db_connection()
            conn.execute(
                '''INSERT INTO resumes (filename, parsed_skills, parsed_experience, uploaded_by, upload_date)
                   VALUES (?, ?, ?, ?, datetime('now'))''',
                (filename, ', '.join(skills), experience, uploaded_by))
            conn.commit()
            conn.close()

            flash('Resume uploaded and processed successfully.')
            return redirect(url_for('list_resumes'))

        flash('Invalid file type. Only PDF and DOCX are allowed.')

    return render_template('upload_resume.html')
@app.route('/job/<int:job_id>/matched-resumes')
def matched_resumes(job_id):
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
    if not job:
        flash('Job not found.')
        conn.close()
        return redirect(url_for('list_jobs'))

    resumes = conn.execute('SELECT * FROM resumes ORDER BY upload_date DESC').fetchall()
    conn.close()

    matched = match_resumes(job['skills'], resumes)

    return render_template('matched_resumes.html', job=job, resumes=matched)

from flask import send_from_directory

@app.route('/resumes')
def list_resumes():
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    resumes = conn.execute('SELECT * FROM resumes ORDER BY upload_date DESC').fetchall()
    conn.close()
    return render_template('resumes.html', resumes=resumes)

@app.route('/delete_resume/<int:resume_id>', methods=['POST'])
def delete_resume(resume_id):  # ← include the resume_id here!
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT filename FROM resumes WHERE id = ?", (resume_id,))
    result = cursor.fetchone()

    if result:
        filename = result[0]
        cursor.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
        conn.commit()
        flash(f"Resume '{filename}' has been deleted.")
    else:
        flash("Resume not found.")

    conn.close()
    return redirect(url_for('list_resumes'))


@app.route('/edit-job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    job = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        skills = request.form['skills']

        conn.execute('''
            UPDATE jobs SET title = ?, description = ?, skills = ?
            WHERE id = ?
        ''', (title, description, skills, job_id))
        conn.commit()
        conn.close()

        flash('Job updated successfully.')
        return redirect(url_for('dashboard'))

    conn.close()
    return render_template('edit_job.html', job=job)

@app.route('/delete-job/<int:job_id>')
def delete_job(job_id):
    if 'user' not in session:
        flash('Please login first.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
    conn.commit()
    conn.close()

    flash('Job deleted successfully.')
    return redirect(url_for('dashboard'))



@app.route('/resume-form', methods=['GET', 'POST'])
def resume_form():
    if request.method == 'POST':
        data = request.form.to_dict()
        return render_template('resume_template.html', **data)
    return render_template('resume_form.html')

@app.route('/shortlist_candidates/<int:job_id>', methods=['POST'])
def shortlist_candidates(job_id):
    selected_resume_ids = request.form.getlist('selected_resumes')
    shortlisted_count = len(selected_resume_ids)

    conn = get_db_connection()
    for resume_id in selected_resume_ids:
        conn.execute("UPDATE resumes SET shortlisted = 'yes' WHERE id = ?", (resume_id,))
    conn.commit()
    conn.close()

    session['shortlisted_count'] = shortlisted_count
    flash(f"{shortlisted_count} candidates shortlisted successfully.")
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
