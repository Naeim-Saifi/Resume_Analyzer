from django.contrib import admin
from .models import Job, JobApplication


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'experience_level', 'posted_by', 'is_active', 'created_at']
    list_filter = ['experience_level', 'is_active', 'created_at']
    search_fields = ['title', 'company_name', 'skills_required']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant', 'job', 'status', 'match_score', 'applied_at']
    list_filter = ['status', 'applied_at', 'job__experience_level']
    search_fields = ['applicant__email', 'job__title']
    readonly_fields = ['applied_at', 'match_score', 'matched_skills']