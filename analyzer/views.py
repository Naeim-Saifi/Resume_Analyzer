from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ResumeForm
from .models import Resume, Job
from .utils import extract_resume_data
import cloudinary.uploader
from jobs.models import Job, JobApplication
from django.utils import timezone  

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





@login_required
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

                # Save resume with cloudinary URL
                resume.cv_url = cloudinary_url
                resume.save()

                # Suggest matching profiles
                suggested_profiles = suggest_profiles(data['SkillsList'])

                # Match resume to active jobs with enhanced categorization
                jobs = Job.objects.filter(is_active=True)
                job_matches = match_resume_to_jobs_with_auto_apply(
                    data['SkillsList'], jobs, resume, request.user
                )

                # Add success messages for auto-applications
                auto_applied_count = len(job_matches['auto_applied'])
                if auto_applied_count > 0:
                    messages.success(
                        request, 
                        f'🎉 Great news! You have been automatically applied and accepted to {auto_applied_count} '
                        f'job{"s" if auto_applied_count > 1 else ""} with 80%+ match scores!'
                    )
                
                high_match_count = len(job_matches['high_match'])
                if high_match_count > 0:
                    messages.info(
                        request,
                        f'🎯 {high_match_count} job{"s" if high_match_count > 1 else ""} with 70%+ match scores '
                        f'are ready for your application!'
                    )

                # All sections and project summaries
                all_sections = data.get('AllSections', {})
                projects_summary = data.get('ProjectsSummary', [])

                return render(request, 'result.html', {
                    'resume': resume,
                    'cv_url': cloudinary_url,
                    'data': data,
                    'profiles': suggested_profiles,
                    'job_matches': job_matches,
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


def match_resume_to_jobs_with_auto_apply(resume_skills, jobs, resume, user):
    """
    Enhanced job matching with auto-application and categorization
    """
    auto_applied_jobs = []
    high_match_jobs = []
    medium_match_jobs = []
    low_match_jobs = []
    
    resume_skills_set = set([s.lower() for s in resume_skills])
    
    for job in jobs:
        job_skills = set(job.get_skills_list())
        matched = resume_skills_set & job_skills
        score = (len(matched) / len(job_skills)) * 100 if job_skills else 0
        
        # Check if user already applied for this job
        existing_application = JobApplication.objects.filter(
            job=job, applicant=user
        ).first()
        
        application_status = None
        if existing_application:
            application_status = existing_application.get_status_display()
        
        job_match = {
            'job': job,
            'score': round(score, 2),
            'matched_skills': list(matched),
            'application_status': application_status,
            'can_apply': not existing_application,
            'application_id': existing_application.id if existing_application else None,
        }
        
        # Auto-apply for very high matches (>=80%) if not already applied
        if score >= 80 and not existing_application:
            try:
                application = JobApplication.objects.create(
                    job=job,
                    applicant=user,
                    resume=resume,
                    match_score=score,
                    matched_skills=list(matched),
                    status='accepted',  # Auto-accept high matches
                    reviewed_at=timezone.now()
                )
                job_match['application_status'] = 'Auto-Applied & Accepted'
                job_match['can_apply'] = False
                job_match['application_id'] = application.id
                auto_applied_jobs.append(job_match)
            except Exception as e:
                # If auto-apply fails, treat as high match
                job_match['auto_apply_error'] = str(e)
                high_match_jobs.append(job_match)
        
        # Categorize remaining jobs
        elif score >= 70:
            high_match_jobs.append(job_match)
        elif score >= 40:
            medium_match_jobs.append(job_match)
        elif score >= 15:
            low_match_jobs.append(job_match)
    
    # Sort each category by score (highest first)
    auto_applied_jobs.sort(key=lambda x: x['score'], reverse=True)
    high_match_jobs.sort(key=lambda x: x['score'], reverse=True)
    medium_match_jobs.sort(key=lambda x: x['score'], reverse=True)
    low_match_jobs.sort(key=lambda x: x['score'], reverse=True)
    
    return {
        'auto_applied': auto_applied_jobs,
        'high_match': high_match_jobs,
        'medium_match': medium_match_jobs,
        'low_match': low_match_jobs,
        'total_matches': len(auto_applied_jobs) + len(high_match_jobs) + len(medium_match_jobs) + len(low_match_jobs)
    }


def match_resume_to_jobs(resume_skills, jobs):
    """
    Legacy function for backward compatibility
    """
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
