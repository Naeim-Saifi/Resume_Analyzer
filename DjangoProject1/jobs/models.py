from django.db import models
from django.contrib.auth import get_user_model
from analyzer.models import Resume

User = get_user_model()


class Job(models.Model):
    EXPERIENCE_LEVELS = [
        ('entry', 'Entry Level (0-2 years)'),
        ('mid', 'Mid Level (2-5 years)'),
        ('senior', 'Senior Level (5+ years)'),
    ]
    
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills_required = models.TextField(help_text="Comma-separated skills")
    experience_level = models.CharField(max_length=10, choices=EXPERIENCE_LEVELS, default='entry')
    location = models.CharField(max_length=100, blank=True, null=True)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    company_name = models.CharField(max_length=200, default='Company')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def get_skills_list(self):
        return [skill.strip().lower() for skill in self.skills_required.split(",") if skill.strip()]
    
    def __str__(self):
        return f"{self.title} at {self.company_name}"


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='job_applications')
    cover_letter = models.TextField(blank=True, null=True)
    match_score = models.FloatField(default=0.0)
    matched_skills = models.JSONField(default=list)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        unique_together = ['job', 'applicant']
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.first_name} applied for {self.job.title}"