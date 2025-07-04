from django.shortcuts import render
from .forms import ResumeForm
from .models import Resume
from .utils import extract_resume_data


def suggest_profiles(skills):
    profiles = {
        'Data Scientist': ['python', 'machine learning', 'data analysis', 'pandas', 'numpy'],
        'Web Developer': ['html', 'css', 'javascript', 'django', 'asp.net', 'angular', 'react'],
        'Android Developer': ['ruby', 'swift', 'kotlin', 'android'],
        'Backend Developer': ['django', 'node.js', 'sql', 'rest api'],
        'Frontend Developer': ['html', 'css', 'javascript', 'react', 'angular'],
        'AI Engineer': ['tensorflow', 'pytorch', 'deep learning', 'machine learning'],
        'Database Administrator': ['sql', 'mysql', 'postgresql', 'mongodb']
    }

    suggested = []
    skills_lower = [skill.lower() for skill in skills]

    for profile, required_skills in profiles.items():
        matched_skills = [skill for skill in required_skills if skill in skills_lower]
        score = (len(matched_skills) / len(required_skills)) * 100  # Calculate percentage

        if matched_skills:
            suggested.append({
                'profile': profile,
                'score': round(score, 2),  # Round to 2 decimal places
                'matched_skills': matched_skills
            })

    # Sort profiles by highest matching score
    suggested = sorted(suggested, key=lambda x: x['score'], reverse=True)

    return suggested


def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save()
            extracted_data = extract_resume_data(resume.file.path)

            # Prepare skills for both display and processing
            extracted_data['SkillsString'] = ', '.join(extracted_data['Skills'])
            extracted_data['SkillsList'] = extracted_data['Skills']

            # Use the list for matching
            suggested_profiles = suggest_profiles(extracted_data['SkillsList'])

            # Pass all detected sections to the template for dynamic display
            all_sections = extracted_data.get('AllSections', {})
            projects_summary = extracted_data.get('ProjectsSummary', [])

            return render(request, 'result.html', {
                'data': extracted_data,
                'profiles': suggested_profiles,
                'all_sections': all_sections,
                'projects_summary': projects_summary
            })
    else:
        form = ResumeForm()

    return render(request, 'upload.html', {'form': form})
