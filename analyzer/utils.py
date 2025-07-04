import spacy
from pdfminer.high_level import extract_text
from docx import Document
import re


nlp = spacy.load('en_core_web_sm')

# Predefined skill set for matching
predefined_skills = [
    'python', 'django', 'java', 'sql', 'c++', 'html', 'css', 'javascript',
    'react', 'node.js', 'android', 'kotlin', 'tensorflow', 'pytorch',
    'machine learning', 'deep learning', 'data analysis', 'pandas', 'numpy',
    'mysql', 'postgresql', 'mongodb'
]

def extract_section_headers(text):
    """
    Extracts possible section headers from resume text.
    Returns a list of unique section headers found.
    """
    headers = set()
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        # Exclude lines with emails, URLs, or numbers (likely contact info)
        if re.search(r'[@:/\d]', line):
            continue
        # Heuristic: 1-4 words, all words are uppercase or title case, not too long
        if (1 <= len(line.split()) <= 4 and
            (line.isupper() or re.match(r'^([A-Z][a-zA-Z]+(\s|$)){1,4}:?$', line))):
            headers.add(line.rstrip(':'))
    return list(headers)

def extract_section(text, section_name, stop_sections=None):
    if stop_sections is None:
        stop_sections = extract_section_headers(text)
    stop_sections = [s for s in stop_sections if s.lower() != section_name.lower()]
    # Allow partial match for section headers (e.g., "Work Experience" for "Experience")
    start_pattern = re.compile(rf'^{section_name}', re.IGNORECASE)
    stop_pattern = re.compile(rf'^({"|".join(map(re.escape, stop_sections))})', re.IGNORECASE)
    lines = text.splitlines()
    section_text = []
    capture = False
    for idx, line in enumerate(lines):
        if idx < 3:
            continue
        if start_pattern.search(line.strip()):
            capture = True
            continue
        if capture and stop_pattern.search(line.strip()):
            break
        if capture:
            section_text.append(line)
    return '\n'.join(section_text).strip()

def extract_name(text):
    """
    Improved name extractor: Scans the top of the resume, skips contact lines, and falls back to spaCy NER.
    """
    contact_keywords = ['linkedin', 'email', 'github', 'phone', 'mobile', 'contact']
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if any(keyword.lower() in line.lower() for keyword in contact_keywords):
            break  # Stop if contact info starts
        if len(line.split()) <= 4 and not any(char in line for char in ['@', ':']):  # Likely a name
            return line
    # Fallback: Use spaCy NER if no valid line found
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return 'Not Found'

def split_projects(project_text):
    """
    Splits the project section into individual projects based on blank lines.
    """
    projects = []
    current = []
    for line in project_text.splitlines():
        if not line.strip():
            if current:
                projects.append('\n'.join(current).strip())
                current = []
        else:
            current.append(line)
    if current:
        projects.append('\n'.join(current).strip())
    return projects

def summarize_project(project):
    """
    Returns a short summary for a project: title + up to 3 lines.
    """
    lines = [line.strip() for line in project.splitlines() if line.strip()]
    if not lines:
        return ""
    title = lines[0]
    summary = ' '.join(lines[1:4])  # Take up to 3 lines after the title
    return f"{title}\n{summary}"

def extract_resume_data(file_path):
    text = ""
    if file_path.endswith('.pdf'):
        text = extract_text(file_path)
    elif file_path.endswith('.docx'):
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + '\n'
    name = extract_name(text)
    doc = nlp(text)
    skills = []
    words = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    for skill in predefined_skills:
        if skill.lower() in words:
            skills.append(skill)
    section_headers = extract_section_headers(text)
    # Try to extract common sections dynamically
    experience_section = extract_section(text, 'Experience', section_headers)
    education_section = extract_section(text, 'Education', section_headers)
    project_section = extract_section(text, 'Projects', section_headers)
    certificates_section = extract_section(text, 'Certificates', section_headers)
    if not certificates_section:
        certificates_section = extract_section(text, 'Certifications', section_headers)
    # Optionally, return all detected sections
    all_sections = {}
    for header in section_headers:
        all_sections[header] = extract_section(text, header, section_headers)

    # Summarize projects
    summarized_projects = []
    if project_section and project_section != "Not Found":
        for proj in split_projects(project_section):
            summary = summarize_project(proj)
            if summary:
                summarized_projects.append(summary)

    data = {
        'Name': name,
        'Skills': list(set(skills)),
        'Experience': experience_section if experience_section else 'Not Found',
        'Education': education_section if education_section else 'Not Found',
        'Projects': project_section if project_section else 'Not Found',
        'Certificates': certificates_section if certificates_section else 'Not Found',
        'AllSections': all_sections,  # Optional: all detected sections
        'ProjectsSummary': summarized_projects  # List of summarized projects
    }
    return data
