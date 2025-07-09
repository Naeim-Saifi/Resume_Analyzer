from django import forms
from .models import Resume

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['name', 'cv']  

# Optional: if you want to keep a raw upload form
class UploadFileForm(forms.Form):
    file = forms.FileField()
