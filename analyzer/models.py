from django.db import models
from cloudinary.models import CloudinaryField
import cloudinary.uploader

class Resume(models.Model):
    name = models.CharField(max_length=100)
    cv = models.FileField(upload_to='resumes/', blank=True, null=True)  # changed to FileField
    cv_url = models.URLField(blank=True, null=True)  # Will store the direct URL

    def save(self, *args, **kwargs):
        # If a new file is uploaded
        if self.cv and not self.cv_url:
            uploaded = cloudinary.uploader.upload(
                self.cv,
                resource_type='raw'
            )
            self.cv_url = uploaded.get('secure_url')

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Job(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    skills_required = models.TextField(help_text="Comma-separated skills")

    def get_skills_list(self):
        return [skill.strip().lower() for skill in self.skills_required.split(",") if skill.strip()]

    def __str__(self):
        return self.title
