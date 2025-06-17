# matching_utils.py

def match_resumes(job_skills, resumes):
    """
    Matches resumes against job skills using simple keyword matching.

    :param job_skills: List of required job skills
    :param resumes: List of resume rows from the database
    :return: List of resumes with match score added
    """
    job_skills_set = set(skill.strip().lower() for skill in job_skills.split(','))
    
    matched_resumes = []
    for resume in resumes:
        resume_skills_set = set(skill.strip().lower() for skill in resume['parsed_skills'].split(','))
        matched_skills = job_skills_set.intersection(resume_skills_set)
        score = len(matched_skills)
        matched_resumes.append({
            'filename': resume['filename'],
            'parsed_skills': resume['parsed_skills'],
            'parsed_experience': resume['parsed_experience'],
            'upload_date': resume['upload_date'],
            'uploaded_by': resume['uploaded_by'],
            'score': score
        })

    # Sort by match score descending
    matched_resumes.sort(key=lambda x: x['score'], reverse=True)
    return matched_resumes
