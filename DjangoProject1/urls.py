from django.contrib import admin
from django.urls import path, include
from analyzer.views import upload_resume
from django.shortcuts import redirect

def home_redirect(request):
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('jobs:admin_dashboard')
        else:
            return redirect('dashboard')
    return redirect('login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('auth/', include('authentication.urls')),
    path('jobs/', include('jobs.urls')),
    path('upload/', upload_resume, name='upload_resume'),
]
