from django.contrib import admin
from django.urls import path
from analyzer.views import upload_resume

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', upload_resume, name='upload_resume'),
]
