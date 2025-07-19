# from django.urls import path
# from . import views

# app_name = 'jobs'

# urlpatterns = [
#     # Admin URLs
#     path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
#     path('admin/create/', views.CreateJobView.as_view(), name='create_job'),
#     path('admin/job/<int:job_id>/applications/', views.job_applications, name='job_applications'),
#     path('admin/application/<int:application_id>/update/', views.update_application_status, name='update_application_status'),
    
#     # User URLs
#     path('', views.JobListView.as_view(), name='job_list'),
#     path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
#     path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
#     path('my-applications/', views.my_applications, name='my_applications'),
# ]




from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # New Admin URLs (staff-only)
    path('admin/post-job/', views.post_job, name='post_job'),
    path('admin/jobs/', views.admin_job_list, name='admin_job_list'),
    
    # Admin URLs
    path('admin/dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin/create/', views.CreateJobView.as_view(), name='create_job'),
    path('admin/job/<int:job_id>/applications/', views.job_applications, name='job_applications'),
    path('admin/application/<int:application_id>/update/', views.update_application_status, name='update_application_status'),
    path('admin/application/<int:application_id>/detail/', views.application_detail, name='application_detail'),
    path('admin/job/<int:job_id>/bulk-update/', views.bulk_update_applications, name='bulk_update_applications'),
    
    # User URLs
    path('', views.JobListView.as_view(), name='job_list'),
    path('<int:pk>/', views.JobDetailView.as_view(), name='job_detail'),
    path('<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('application/<int:application_id>/status/', views.application_status_check, name='application_status'),
    path('application/<int:application_id>/withdraw/', views.withdraw_application, name='withdraw_application'),
    path('application/<int:application_id>/download-resume/', views.download_resume, name='download_resume'),
]