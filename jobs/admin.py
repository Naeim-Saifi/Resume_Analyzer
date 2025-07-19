from django.contrib import admin
from .models import Job, JobApplication


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company_name', 'experience_level', 'posted_by', 'is_active', 'posted_at', 'created_at']
    list_filter = ['experience_level', 'is_active', 'posted_at', 'created_at']
    search_fields = ['title', 'company_name', 'skills_required']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at', 'posted_at']
    ordering = ['-posted_at']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'company_name', 'description', 'skills_required')
        }),
        ('Job Details', {
            'fields': ('experience_level', 'location', 'salary_range', 'is_active')
        }),
        ('Metadata', {
            'fields': ('posted_by', 'posted_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant_name', 'job_title', 'status', 'match_score', 'applied_at', 'status_updated_at']
    list_filter = ['status', 'applied_at', 'status_updated_at', 'job__experience_level']
    search_fields = ['applicant__email', 'applicant__first_name', 'applicant__last_name', 'job__title']
    readonly_fields = ['applied_at', 'match_score', 'matched_skills', 'status_updated_at']
    list_editable = ['status']
    date_hierarchy = 'applied_at'
    
    fieldsets = (
        ('Application Info', {
            'fields': ('job', 'applicant', 'resume', 'cover_letter')
        }),
        ('Status & Review', {
            'fields': ('status', 'status_updated_by', 'admin_notes', 'interview_date')
        }),
        ('Matching Results', {
            'fields': ('match_score', 'matched_skills'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('applied_at', 'reviewed_at', 'status_updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def applicant_name(self, obj):
        return obj.applicant.get_full_name() or obj.applicant.email
    applicant_name.short_description = 'Applicant'
    
    def job_title(self, obj):
        return obj.job.title
    job_title.short_description = 'Job'
    
    def save_model(self, request, obj, form, change):
        if change and 'status' in form.changed_data:
            obj.status_updated_by = request.user
            from django.utils import timezone
            obj.status_updated_at = timezone.now()
            
            if obj.status in ['accepted', 'rejected'] and not obj.reviewed_at:
                obj.reviewed_at = timezone.now()
        
        super().save_model(request, obj, form, change)