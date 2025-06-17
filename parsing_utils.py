import re
from PyPDF2 import PdfReader
import docx

# Extract text from PDF
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Extract text from DOCX
def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

# Extract skills using basic keyword matching
def extract_skills(text):
    known_skills = [
        'Python', 'Java', 'C++', 'JavaScript', 'SQL',
        'HTML', 'CSS', 'Machine Learning', 'Deep Learning',
        'Data Analysis', 'Excel', 'Power BI', 'Flask',
        'Django', 'AWS', 'Azure', 'Git', 'Linux', 'NLP'
    ]
    found_skills = [skill for skill in known_skills if re.search(r'\b' + re.escape(skill) + r'\b', text, re.IGNORECASE)]
    return found_skills

# Extract years of experience from resume text
def extract_experience(text):
    match = re.search(r'(\d+)\s+(?:years?|yrs?)\s+(?:of)?\s*experience', text, re.IGNORECASE)
    if match:
        return match.group(1) + " years"
    return "Not specified"
