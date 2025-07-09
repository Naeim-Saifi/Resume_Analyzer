import spacy
from docx import Document
import re
from io import BytesIO
import io
from pdfminer.high_level import extract_text as extract_pdf_text

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

# Predefined skill set for matching
predefined_skills = [
    'python', 'django', 'java', 'sql', 'c++', 'html', 'css', 'javascript',
    'react', 'node.js', 'android', 'kotlin', 'tensorflow', 'pytorch',
    'machine learning', 'deep learning', 'data analysis', 'pandas', 'numpy',
    'mysql', 'postgresql', 'mongodb'
]


def extract_section_headers(text):
    lines = text.splitlines()
    headers = []

    for line in lines:
        line_clean = line.strip().upper()
        if line_clean and re.match(r'^[A-Z\s]+$', line_clean) and len(line_clean) <= 30:
            headers.append(line_clean)
    return headers

def extract_section(text, section_name, all_headers):
    lines = text.splitlines()
    section_data = []
    capture = False

    for i, line in enumerate(lines):
        stripped_line = line.strip()
        upper_line = stripped_line.upper()

        # Start capturing when we find the right header
        if section_name.upper() in upper_line:
            capture = True
            continue

        # Stop capturing when the next header is encountered
        if capture and any(
            header in upper_line for header in all_headers if header != section_name.upper()
        ):
            break

        if capture:
            # Avoid appending just bullets or empty lines
            if stripped_line and stripped_line != '•':
                section_data.append(stripped_line)

    return '\n'.join(section_data).strip() if section_data else "Not Found"


def extract_name(text):
    contact_keywords = ['linkedin', 'email', 'github', 'phone', 'mobile', 'contact']
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if any(keyword.lower() in line.lower() for keyword in contact_keywords):
            break
        if len(line.split()) <= 4 and not any(char in line for char in ['@', ':']):
            return line
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return 'Not Found'



def split_projects(project_text):
    # Normalize line endings and remove extra spaces
    lines = [line.strip() for line in project_text.splitlines() if line.strip()]

    projects = []
    current = []

    for line in lines:
        # Check if it's a new project (bullet or numbered start)
        if re.match(r"^(\d+\.\s|[-*•●])", line) and current:
            projects.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)

    # Add the last project
    if current:
        projects.append("\n".join(current).strip())

    return projects


def summarize_project(project):
    bullet_chars = ['•', '●', '·', '*', '-', '']
    def clean_line(line):
        line = line.strip()
        for bullet in bullet_chars:
            if line.startswith(bullet):
                line = line[len(bullet):].strip()
        return line

    lines = [clean_line(line) for line in project.splitlines() if clean_line(line)]
    if not lines:
        return ""
    title = lines[0]
    summary_lines = lines[1:4]
    summary = '\n'.join(summary_lines)
    return f"{title}\n{summary}"


def extract_resume_data(uploaded_file):
    text = ""

    # Handle PDF
    if uploaded_file.name.endswith('.pdf'):
        uploaded_file.seek(0)  # Always reset pointer
        pdf_data = uploaded_file.read()
        pdf_stream = io.BytesIO(pdf_data)
        text = extract_pdf_text(pdf_stream)

    # Handle DOCX
    elif uploaded_file.name.endswith('.docx'):
        uploaded_file.seek(0)  
        in_memory_file = io.BytesIO(uploaded_file.read())
        doc = Document(in_memory_file)
        for para in doc.paragraphs:
            text += para.text + '\n'

    # Text Extraction and NLP Processing
    name = extract_name(text)
    doc = nlp(text)
    skills = []
    words = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    for skill in predefined_skills:
        if skill.lower() in words:
            skills.append(skill)

    section_headers = extract_section_headers(text)
    experience_section = extract_section(text, 'Experience', section_headers)
    education_section = extract_section(text, 'Education', section_headers)
    project_section = extract_section(text, 'Projects', section_headers)
    certificates_section = extract_section(text, 'Certificates', section_headers)
    if not certificates_section:
        certificates_section = extract_section(text, 'Certifications', section_headers)

    all_sections = {}
    for header in section_headers:
        all_sections[header] = extract_section(text, header, section_headers)

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
        'AllSections': all_sections,
        'ProjectsSummary': summarized_projects
    }
    return data

def extract_resume_data_from_text(text):
    nlp = spacy.load('en_core_web_sm')
    name = extract_name(text)
    doc = nlp(text)
    skills = []
    words = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    for skill in predefined_skills:
        if skill.lower() in words:
            skills.append(skill)
    section_headers = extract_section_headers(text)
    experience_section = extract_section(text, 'Experience', section_headers)
    education_section = extract_section(text, 'Education', section_headers)
    project_section = extract_section(text, 'Projects', section_headers)
    certificates_section = extract_section(text, 'Certificates', section_headers)
    if not certificates_section:
        certificates_section = extract_section(text, 'Certifications', section_headers)
    all_sections = {}
    for header in section_headers:
        all_sections[header] = extract_section(text, header, section_headers)

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
        'AllSections': all_sections,
        'ProjectsSummary': summarized_projects
    }
    return data
