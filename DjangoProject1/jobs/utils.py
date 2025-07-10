from analyzer.utils import extract_resume_data_from_text, extract_resume_data
import requests
from io import BytesIO


def calculate_resume_job_match(resume_skills, job_skills):
    """
    Calculate matching score between resume skills and job requirements
    
    Args:
        resume_skills (list): List of skills from resume
        job_skills (list): List of required skills for job
    
    Returns:
        tuple: (match_score, matched_skills)
    """
    if not job_skills:
        return 0.0, []
    
    # Convert to lowercase for case-insensitive matching
    resume_skills_lower = [skill.lower().strip() for skill in resume_skills if skill]
    job_skills_lower = [skill.lower().strip() for skill in job_skills if skill]
    
    # Find matched skills
    matched_skills = []
    for job_skill in job_skills_lower:
        for resume_skill in resume_skills_lower:
            if job_skill in resume_skill or resume_skill in job_skill:
                matched_skills.append(job_skill)
                break
    
    # Remove duplicates
    matched_skills = list(set(matched_skills))
    
    # Calculate score
    if job_skills_lower:
        score = (len(matched_skills) / len(job_skills_lower)) * 100
    else:
        score = 0.0
    
    return round(score, 2), matched_skills


def extract_resume_from_url(resume_url):
    """
    Download and extract resume data from Cloudinary URL
    
    Args:
        resume_url (str): URL of the resume file
    
    Returns:
        dict: Extracted resume data
    """
    try:
        response = requests.get(resume_url, timeout=30)
        if response.status_code == 200:
            # Create a file-like object
            file_content = BytesIO(response.content)
            file_content.name = resume_url.split('/')[-1]
            
            # Extract resume data
            resume_data = extract_resume_data(file_content)
            return resume_data
        else:
            raise Exception(f"Failed to download resume: HTTP {response.status_code}")
    except Exception as e:
        raise Exception(f"Error processing resume: {str(e)}")


def get_application_status(match_score):
    """
    Determine application status based on match score
    
    Args:
        match_score (float): Matching score percentage
    
    Returns:
        str: Application status ('accepted', 'pending', 'rejected')
    """
    if match_score >= 75:
        return 'accepted'
    elif match_score >= 50:
        return 'pending'
    else:
        return 'rejected'


def format_skills_for_display(skills_list):
    """
    Format skills list for better display
    
    Args:
        skills_list (list): List of skills
    
    Returns:
        str: Formatted skills string
    """
    if not skills_list:
        return "No skills specified"
    
    return ", ".join([skill.title() for skill in skills_list])