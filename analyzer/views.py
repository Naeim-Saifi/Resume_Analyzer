from django.shortcuts import render, redirect
from .forms import ResumeForm
from .models import Resume, Job
from .utils import extract_resume_data
import cloudinary.uploader

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
        score = (len(matched_skills) / len(required_skills)) * 100

        if matched_skills:
            suggested.append({
                'profile': profile,
                'score': round(score, 2),
                'matched_skills': matched_skills
            })

    return sorted(suggested, key=lambda x: x['score'], reverse=True)




def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            uploaded_file = request.FILES.get('cv')

            if uploaded_file:
                # Upload to Cloudinary
                result = cloudinary.uploader.upload(uploaded_file, resource_type="raw")
                cloudinary_url = result.get('secure_url', '')

                # Extract resume data from InMemoryUploadedFile
                data = extract_resume_data(uploaded_file)

                # Prepare skill strings
                data['SkillsString'] = ', '.join(data.get('Skills', []))
                data['SkillsList'] = data.get('Skills', [])

                # Suggest matching profiles
                suggested_profiles = suggest_profiles(data['SkillsList'])

                # All sections and project summaries
                all_sections = data.get('AllSections', {})
                projects_summary = data.get('ProjectsSummary', [])

                return render(request, 'result.html', {
                    'resume': resume,
                    'cv_url': cloudinary_url,
                    'data': data,
                    'profiles': suggested_profiles,
                    'all_sections': all_sections,
                    'projects_summary': projects_summary
                })
            else:
                return render(request, 'error.html', {'message': 'File not found or upload failed.'})
    else:
        form = ResumeForm()

    return render(request, 'upload.html', {'form': form})



def post_job(request):
    # Implement a form to post a job
    pass


def job_list(request):
    jobs = Job.objects.all()
    return render(request, 'job_list.html', {'jobs': jobs})


def match_resume_to_jobs(resume_skills, jobs):
    results = []
    resume_skills_set = set([s.lower() for s in resume_skills])
    for job in jobs:
        job_skills = set(job.get_skills_list())
        matched = resume_skills_set & job_skills
        score = (len(matched) / len(job_skills)) * 100 if job_skills else 0
        status = "Accepted" if score >= 75 else "Rejected"
        results.append({
            'job': job,
            'score': round(score, 2),
            'matched_skills': list(matched),
            'status': status
        })
    return results


def resume_list(request):
    resumes = Resume.objects.all().order_by('-id')  # assuming 'uploaded_at' doesn't exist
    return render(request, 'resume_list.html', {'resumes': resumes})
