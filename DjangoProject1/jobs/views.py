from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q
from django.http import JsonResponse
from analyzer.models import Resume
from analyzer.utils import extract_resume_data_from_text, extract_resume_data
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm
import requests
from io import BytesIO


def admin_required(view_func):
    """Decorator to check if user is admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@method_decorator(admin_required, name='dispatch')
class AdminDashboardView(ListView):
    model = Job
    template_name = 'jobs/admin_dashboard.html'
    context_object_name = 'jobs'
    paginate_by = 10
    
    def get_queryset(self):
        return Job.objects.filter(posted_by=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_jobs'] = self.get_queryset().count()
        context['active_jobs'] = self.get_queryset().filter(is_active=True).count()
        context['total_applications'] = JobApplication.objects.filter(
            job__posted_by=self.request.user
        ).count()
        return context


@method_decorator(admin_required, name='dispatch')
class CreateJobView(CreateView):
    model = Job
    form_class = JobForm
    template_name = 'jobs/create_job.html'
    success_url = reverse_lazy('jobs:admin_dashboard')
    
    def form_valid(self, form):
        form.instance.posted_by = self.request.user
        messages.success(self.request, 'Job posted successfully!')
        return super().form_valid(form)


class JobListView(LoginRequiredMixin, ListView):
    model = Job
    template_name = 'jobs/job_list.html'
    context_object_name = 'jobs'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Job.objects.filter(is_active=True)
        search = self.request.GET.get('search')
        location = self.request.GET.get('location')
        experience = self.request.GET.get('experience')
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(description__icontains=search) |
                Q(skills_required__icontains=search)
            )
        
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        if experience:
            queryset = queryset.filter(experience_level=experience)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('search', '')
        context['location'] = self.request.GET.get('location', '')
        context['experience'] = self.request.GET.get('experience', '')
        context['experience_choices'] = Job.EXPERIENCE_LEVELS
        return context


class JobDetailView(LoginRequiredMixin, DetailView):
    model = Job
    template_name = 'jobs/job_detail.html'
    context_object_name = 'job'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_resumes'] = Resume.objects.filter(name=self.request.user.get_full_name())
        context['has_applied'] = JobApplication.objects.filter(
            job=self.object,
            applicant=self.request.user
        ).exists()
        return context


def calculate_match_score(resume_skills, job_skills):
    """Calculate matching score between resume and job skills"""
    if not job_skills:
        return 0.0, []
    
    resume_skills_set = set([skill.lower().strip() for skill in resume_skills])
    job_skills_set = set([skill.lower().strip() for skill in job_skills])
    
    matched_skills = list(resume_skills_set & job_skills_set)
    score = (len(matched_skills) / len(job_skills_set)) * 100 if job_skills_set else 0
    
    return round(score, 2), matched_skills


@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    
    # Check if user already applied
    if JobApplication.objects.filter(job=job, applicant=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('jobs:job_detail', pk=job_id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        resume_id = request.POST.get('resume_id')
        
        if not resume_id:
            messages.error(request, 'Please select a resume to apply.')
            return redirect('jobs:job_detail', pk=job_id)
        
        try:
            resume = Resume.objects.get(id=resume_id)
        except Resume.DoesNotExist:
            messages.error(request, 'Selected resume not found.')
            return redirect('jobs:job_detail', pk=job_id)
        
        if form.is_valid():
            # Extract resume data for matching
            try:
                if resume.cv_url:
                    # Download file from Cloudinary URL
                    response = requests.get(resume.cv_url)
                    if response.status_code == 200:
                        # Create a file-like object
                        file_content = BytesIO(response.content)
                        file_content.name = resume.cv_url.split('/')[-1]
                        resume_data = extract_resume_data(file_content)
                    else:
                        raise Exception("Could not download resume from URL")
                else:
                    raise Exception("No resume URL found")
                
                resume_skills = resume_data.get('Skills', [])
                job_skills = job.get_skills_list()
                
                # Calculate match score
                match_score, matched_skills = calculate_match_score(resume_skills, job_skills)
                
                # Create application
                application = form.save(commit=False)
                application.job = job
                application.applicant = request.user
                application.resume = resume
                application.match_score = match_score
                application.matched_skills = matched_skills
                
                # Auto-accept if score >= 75%
                if match_score >= 75:
                    application.status = 'accepted'
                    messages.success(request, f'Congratulations! Your application has been automatically accepted with a {match_score}% match!')
                else:
                    application.status = 'pending'
                    messages.success(request, f'Application submitted successfully! Match score: {match_score}%')
                
                application.save()
                return redirect('jobs:my_applications')
                
            except Exception as e:
                messages.error(request, f'Error processing your application: {str(e)}')
                return redirect('jobs:job_detail', pk=job_id)
    
    return redirect('jobs:job_detail', pk=job_id)


@login_required
def my_applications(request):
    applications = JobApplication.objects.filter(applicant=request.user)
    return render(request, 'jobs/my_applications.html', {'applications': applications})


@admin_required
def job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications = JobApplication.objects.filter(job=job)
    
    return render(request, 'jobs/job_applications.html', {
        'job': job,
        'applications': applications
    })


@admin_required
def update_application_status(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(JobApplication, id=application_id)
        new_status = request.POST.get('status')
        
        if new_status in ['pending', 'accepted', 'rejected']:
            application.status = new_status
            application.save()
            messages.success(request, f'Application status updated to {new_status}.')
        
        return redirect('jobs:job_applications', job_id=application.job.id)
    
    return redirect('jobs:admin_dashboard')