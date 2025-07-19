# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.contrib import messages
# from django.views.generic import ListView, CreateView, DetailView
# from django.urls import reverse_lazy
# from django.utils.decorators import method_decorator
# from django.db.models import Q
# from django.http import JsonResponse
# from analyzer.models import Resume
# from analyzer.utils import extract_resume_data_from_text, extract_resume_data
# from .models import Job, JobApplication
# from .forms import JobForm, JobApplicationForm
# import requests
# from io import BytesIO


# def admin_required(view_func):
#     """Decorator to check if user is admin"""
#     def wrapper(request, *args, **kwargs):
#         if not request.user.is_authenticated or request.user.role != 'admin':
#             messages.error(request, 'Access denied. Admin privileges required.')
#             return redirect('login')
#         return view_func(request, *args, **kwargs)
#     return wrapper


# @method_decorator(admin_required, name='dispatch')
# class AdminDashboardView(ListView):
#     model = Job
#     template_name = 'jobs/admin_dashboard.html'
#     context_object_name = 'jobs'
#     paginate_by = 10
    
#     def get_queryset(self):
#         return Job.objects.filter(posted_by=self.request.user)
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['total_jobs'] = self.get_queryset().count()
#         context['active_jobs'] = self.get_queryset().filter(is_active=True).count()
#         context['total_applications'] = JobApplication.objects.filter(
#             job__posted_by=self.request.user
#         ).count()
#         return context


# @method_decorator(admin_required, name='dispatch')
# class CreateJobView(CreateView):
#     model = Job
#     form_class = JobForm
#     template_name = 'jobs/create_job.html'
#     success_url = reverse_lazy('jobs:admin_dashboard')
    
#     def form_valid(self, form):
#         form.instance.posted_by = self.request.user
#         messages.success(self.request, 'Job posted successfully!')
#         return super().form_valid(form)


# class JobListView(LoginRequiredMixin, ListView):
#     model = Job
#     template_name = 'jobs/job_list.html'
#     context_object_name = 'jobs'
#     paginate_by = 12
    
#     def get_queryset(self):
#         queryset = Job.objects.filter(is_active=True)
#         search = self.request.GET.get('search')
#         location = self.request.GET.get('location')
#         experience = self.request.GET.get('experience')
        
#         if search:
#             queryset = queryset.filter(
#                 Q(title__icontains=search) | 
#                 Q(description__icontains=search) |
#                 Q(skills_required__icontains=search)
#             )
        
#         if location:
#             queryset = queryset.filter(location__icontains=location)
            
#         if experience:
#             queryset = queryset.filter(experience_level=experience)
            
#         return queryset
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['search'] = self.request.GET.get('search', '')
#         context['location'] = self.request.GET.get('location', '')
#         context['experience'] = self.request.GET.get('experience', '')
#         context['experience_choices'] = Job.EXPERIENCE_LEVELS
#         return context


# class JobDetailView(LoginRequiredMixin, DetailView):
#     model = Job
#     template_name = 'jobs/job_detail.html'
#     context_object_name = 'job'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['user_resumes'] = Resume.objects.filter(name=self.request.user.get_full_name())
#         context['has_applied'] = JobApplication.objects.filter(
#             job=self.object,
#             applicant=self.request.user
#         ).exists()
#         return context


# def calculate_match_score(resume_skills, job_skills):
#     """Calculate matching score between resume and job skills"""
#     if not job_skills:
#         return 0.0, []
    
#     resume_skills_set = set([skill.lower().strip() for skill in resume_skills])
#     job_skills_set = set([skill.lower().strip() for skill in job_skills])
    
#     matched_skills = list(resume_skills_set & job_skills_set)
#     score = (len(matched_skills) / len(job_skills_set)) * 100 if job_skills_set else 0
    
#     return round(score, 2), matched_skills


# @login_required
# def apply_job(request, job_id):
#     job = get_object_or_404(Job, id=job_id, is_active=True)
    
#     # Check if user already applied
#     if JobApplication.objects.filter(job=job, applicant=request.user).exists():
#         messages.warning(request, 'You have already applied for this job.')
#         return redirect('jobs:job_detail', pk=job_id)
    
#     if request.method == 'POST':
#         form = JobApplicationForm(request.POST)
#         resume_id = request.POST.get('resume_id')
        
#         if not resume_id:
#             messages.error(request, 'Please select a resume to apply.')
#             return redirect('jobs:job_detail', pk=job_id)
        
#         try:
#             resume = Resume.objects.get(id=resume_id)
#         except Resume.DoesNotExist:
#             messages.error(request, 'Selected resume not found.')
#             return redirect('jobs:job_detail', pk=job_id)
        
#         if form.is_valid():
#             # Extract resume data for matching
#             try:
#                 if resume.cv_url:
#                     # Download file from Cloudinary URL
#                     response = requests.get(resume.cv_url)
#                     if response.status_code == 200:
#                         # Create a file-like object
#                         file_content = BytesIO(response.content)
#                         file_content.name = resume.cv_url.split('/')[-1]
#                         resume_data = extract_resume_data(file_content)
#                     else:
#                         raise Exception("Could not download resume from URL")
#                 else:
#                     raise Exception("No resume URL found")
                
#                 resume_skills = resume_data.get('Skills', [])
#                 job_skills = job.get_skills_list()
                
#                 # Calculate match score
#                 match_score, matched_skills = calculate_match_score(resume_skills, job_skills)
                
#                 # Create application
#                 application = form.save(commit=False)
#                 application.job = job
#                 application.applicant = request.user
#                 application.resume = resume
#                 application.match_score = match_score
#                 application.matched_skills = matched_skills
                
#                 # Auto-accept if score >= 75%
#                 if match_score >= 75:
#                     application.status = 'accepted'
#                     messages.success(request, f'Congratulations! Your application has been automatically accepted with a {match_score}% match!')
#                 else:
#                     application.status = 'pending'
#                     messages.success(request, f'Application submitted successfully! Match score: {match_score}%')
                
#                 application.save()
#                 return redirect('jobs:my_applications')
                
#             except Exception as e:
#                 messages.error(request, f'Error processing your application: {str(e)}')
#                 return redirect('jobs:job_detail', pk=job_id)
    
#     return redirect('jobs:job_detail', pk=job_id)


# @login_required
# def my_applications(request):
#     applications = JobApplication.objects.filter(applicant=request.user)
#     return render(request, 'jobs/my_applications.html', {'applications': applications})


# @admin_required
# def job_applications(request, job_id):
#     job = get_object_or_404(Job, id=job_id, posted_by=request.user)
#     applications = JobApplication.objects.filter(job=job)
    
#     return render(request, 'jobs/job_applications.html', {
#         'job': job,
#         'applications': applications
#     })


# @admin_required
# def update_application_status(request, application_id):
#     if request.method == 'POST':
#         application = get_object_or_404(JobApplication, id=application_id)
#         new_status = request.POST.get('status')
        
#         if new_status in ['pending', 'accepted', 'rejected']:
#             application.status = new_status
#             application.save()
#             messages.success(request, f'Application status updated to {new_status}.')
        
#         return redirect('jobs:job_applications', job_id=application.job.id)
    
#     return redirect('jobs:admin_dashboard')




from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q, Avg
from django.db import models
from django.http import JsonResponse
from django.utils import timezone
from analyzer.models import Resume
from analyzer.utils import extract_resume_data_from_text, extract_resume_data
from .models import Job, JobApplication
from .forms import JobForm, JobApplicationForm, AdminJobForm
import requests
from io import BytesIO


def staff_required(view_func):
    """Decorator to check if user is admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_staff:
            messages.error(request, 'Access denied. Staff privileges required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to check if user is admin (role-based)"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != 'admin':
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


@staff_required
def post_job(request):
    """Admin view to post a new job"""
    if request.method == 'POST':
        form = AdminJobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect('jobs:admin_job_list')
    else:
        form = AdminJobForm()
    
    return render(request, 'admin/post_job.html', {'form': form})


@staff_required
def admin_job_list(request):
    """Admin view to list all jobs posted by the logged-in admin"""
    jobs = Job.objects.filter(posted_by=request.user).order_by('-posted_at')
    
    context = {
        'jobs': jobs,
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(is_active=True).count(),
        'total_applications': JobApplication.objects.filter(job__posted_by=request.user).count(),
    }
    
    return render(request, 'admin/job_list.html', context)


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
                    application.reviewed_at = timezone.now()
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
    """Enhanced view for users to track their job applications with CV details"""
    applications_queryset = JobApplication.objects.filter(applicant=request.user).select_related(
        'job', 'resume', 'job__posted_by'
    )
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter and status_filter in [choice[0] for choice in JobApplication.STATUS_CHOICES]:
        applications_queryset = applications_queryset.filter(status=status_filter)
    
    # Filter by job title search
    search_query = request.GET.get('search')
    if search_query:
        applications_queryset = applications_queryset.filter(
            Q(job__title__icontains=search_query) | 
            Q(job__company_name__icontains=search_query)
        )
    
    # Sort applications
    sort_by = request.GET.get('sort_by', '-applied_at')
    valid_sorts = ['-applied_at', 'applied_at', '-match_score', 'match_score', 'status', '-status_updated_at']
    if sort_by in valid_sorts:
        applications_queryset = applications_queryset.order_by(sort_by)
    
    applications = applications_queryset
    
    # Calculate statistics
    total_applications = applications_queryset.count()
    status_counts = {}
    for status_choice in JobApplication.STATUS_CHOICES:
        status_counts[status_choice[0]] = applications_queryset.filter(status=status_choice[0]).count()
    
    # Calculate average match score
    avg_match_score = applications_queryset.aggregate(
        avg_score=Avg('match_score')
    )['avg_score'] or 0
    
    context = {
        'applications': applications,
        'total_applications': total_applications,
        'status_counts': status_counts,
        'avg_match_score': round(avg_match_score, 2),
        'status_choices': JobApplication.STATUS_CHOICES,
        'current_status_filter': status_filter,
        'current_search': search_query,
        'current_sort': sort_by,
    }
    
    return render(request, 'jobs/my_applications.html', context)


@admin_required
def job_applications(request, job_id):
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    applications_queryset = JobApplication.objects.filter(job=job)
    
    # Filter by status if provided
    status_filter = request.GET.get('status')
    if status_filter and status_filter in [choice[0] for choice in JobApplication.STATUS_CHOICES]:
        applications_queryset = applications_queryset.filter(status=status_filter)
    
    # Sort by different criteria
    sort_by = request.GET.get('sort_by', '-applied_at')
    if sort_by in ['-applied_at', 'applied_at', '-match_score', 'match_score', 'status']:
        applications_queryset = applications_queryset.order_by(sort_by)
    
    applications = applications_queryset
    
    # Calculate statistics
    total_applications = applications_queryset.count()
    status_counts = {}
    for status_choice in JobApplication.STATUS_CHOICES:
        status_counts[status_choice[0]] = applications_queryset.filter(status=status_choice[0]).count()
    
    return render(request, 'jobs/job_applications.html', {
        'job': job,
        'applications': applications,
        'status_choices': JobApplication.STATUS_CHOICES,
        'current_status_filter': status_filter,
        'current_sort': sort_by,
        'total_applications': total_applications,
        'status_counts': status_counts,
    })


@admin_required
def update_application_status(request, application_id):
    if request.method == 'POST':
        application = get_object_or_404(JobApplication, id=application_id)
        
        # Ensure the admin owns the job
        if application.job.posted_by != request.user:
            messages.error(request, 'You can only update applications for your own job posts.')
            return redirect('jobs:admin_dashboard')
        
        new_status = request.POST.get('status')
        admin_notes = request.POST.get('admin_notes', '')
        interview_date = request.POST.get('interview_date')
        
        valid_statuses = [choice[0] for choice in JobApplication.STATUS_CHOICES]
        
        if new_status in valid_statuses:
            old_status = application.status
            application.status = new_status
            application.status_updated_by = request.user
            application.status_updated_at = timezone.now()
            
            if admin_notes:
                application.admin_notes = admin_notes
            
            if new_status == 'interview_scheduled' and interview_date:
                from datetime import datetime
                try:
                    application.interview_date = datetime.strptime(interview_date, '%Y-%m-%dT%H:%M')
                except ValueError:
                    messages.error(request, 'Invalid interview date format.')
                    return redirect('jobs:job_applications', job_id=application.job.id)
            
            if new_status in ['accepted', 'rejected'] and not application.reviewed_at:
                application.reviewed_at = timezone.now()
            
            application.save()
            
            # Create status change notification
            create_application_notification(application, old_status, new_status)
            
            messages.success(request, f'Application status updated from "{old_status}" to "{new_status}".')
        else:
            messages.error(request, 'Invalid status selected.')
        
        return redirect('jobs:job_applications', job_id=application.job.id)
    
    return redirect('jobs:admin_dashboard')


def create_application_notification(application, old_status, new_status):
    """Create a notification for status change"""
    status_messages = {
        'under_review': 'Your application is now under review.',
        'interview_scheduled': f'Congratulations! An interview has been scheduled for {application.interview_date.strftime("%B %d, %Y at %I:%M %p") if application.interview_date else "soon"}.',
        'accepted': 'Congratulations! Your application has been accepted.',
        'rejected': 'Thank you for your interest. Unfortunately, we have decided to move forward with other candidates.',
        'withdrawn': 'Your application has been withdrawn.',
    }
    
    # In a real application, you might want to send emails or create database notifications
    # For now, we'll just use Django messages when the user logs in next
    pass


@admin_required  
def application_detail(request, application_id):
    """Detailed view of a job application for admin"""
    application = get_object_or_404(JobApplication, id=application_id)
    
    # Ensure the admin owns the job
    if application.job.posted_by != request.user:
        messages.error(request, 'You can only view applications for your own job posts.')
        return redirect('jobs:admin_dashboard')
    
    return render(request, 'jobs/application_detail.html', {
        'application': application,
        'status_choices': JobApplication.STATUS_CHOICES,
    })


@login_required
def application_status_check(request, application_id):
    """Detailed view for users to check their application status with CV details"""
    application = get_object_or_404(JobApplication, id=application_id, applicant=request.user)
    
    # Get resume details and download URL
    resume_details = None
    if application.resume:
        resume_details = {
            'name': application.resume.name,
            'cv_url': application.resume.cv_url,
            'uploaded_at': getattr(application.resume, 'uploaded_at', None),
        }
    
    # Calculate days since application
    from datetime import datetime
    days_since_applied = (timezone.now() - application.applied_at).days
    
    # Status timeline
    status_timeline = []
    status_timeline.append({
        'status': 'Applied',
        'date': application.applied_at,
        'description': f'Application submitted with {application.match_score}% match score'
    })
    
    if application.status_updated_at and application.status != 'pending':
        status_display = dict(JobApplication.STATUS_CHOICES).get(application.status, application.status)
        status_timeline.append({
            'status': status_display,
            'date': application.status_updated_at,
            'description': f'Status updated to {status_display.lower()}'
        })
    
    if application.interview_date:
        status_timeline.append({
            'status': 'Interview Scheduled',
            'date': application.interview_date,
            'description': f'Interview scheduled for {application.interview_date.strftime("%B %d, %Y at %I:%M %p")}'
        })
    
    if application.reviewed_at:
        status_timeline.append({
            'status': 'Reviewed',
            'date': application.reviewed_at,
            'description': 'Application has been reviewed'
        })
    
    # Sort timeline by date
    status_timeline.sort(key=lambda x: x['date'])
    
    context = {
        'application': application,
        'resume_details': resume_details,
        'days_since_applied': days_since_applied,
        'status_timeline': status_timeline,
        'matched_skills_count': len(application.matched_skills) if application.matched_skills else 0,
    }
    
    return render(request, 'jobs/application_status.html', context)


@login_required
def withdraw_application(request, application_id):
    """Allow users to withdraw their application"""
    application = get_object_or_404(JobApplication, id=application_id, applicant=request.user)
    
    # Only allow withdrawal for pending or under_review applications
    if application.status in ['pending', 'under_review']:
        if request.method == 'POST':
            application.status = 'withdrawn'
            application.status_updated_at = timezone.now()
            application.save()
            messages.success(request, f'Your application for "{application.job.title}" has been withdrawn.')
            return redirect('jobs:my_applications')
    else:
        messages.error(request, 'You can only withdraw pending or under review applications.')
        return redirect('jobs:application_status', application_id=application_id)
    
    return render(request, 'jobs/withdraw_application.html', {'application': application})


@login_required
def download_resume(request, application_id):
    """Allow users to download the resume they used for an application"""
    application = get_object_or_404(JobApplication, id=application_id, applicant=request.user)
    
    if application.resume and application.resume.cv_url:
        return redirect(application.resume.cv_url)
    else:
        messages.error(request, 'Resume file not found.')
        return redirect('jobs:application_status', application_id=application_id)


@admin_required
def bulk_update_applications(request, job_id):
    """Bulk update multiple applications"""
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    
    if request.method == 'POST':
        application_ids = request.POST.getlist('application_ids')
        new_status = request.POST.get('bulk_status')
        admin_notes = request.POST.get('bulk_notes', '')
        
        if application_ids and new_status in [choice[0] for choice in JobApplication.STATUS_CHOICES]:
            applications = JobApplication.objects.filter(
                id__in=application_ids, 
                job=job
            )
            
            updated_count = 0
            for application in applications:
                old_status = application.status
                application.status = new_status
                application.status_updated_by = request.user
                application.status_updated_at = timezone.now()
                
                if admin_notes:
                    application.admin_notes = admin_notes
                
                if new_status in ['accepted', 'rejected'] and not application.reviewed_at:
                    application.reviewed_at = timezone.now()
                
                application.save()
                create_application_notification(application, old_status, new_status)
                updated_count += 1
            
            messages.success(request, f'Successfully updated {updated_count} applications to "{new_status}".')
        else:
            messages.error(request, 'Please select applications and a valid status.')
    
    return redirect('jobs:job_applications', job_id=job_id)