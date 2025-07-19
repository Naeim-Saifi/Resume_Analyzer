from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Job, JobApplication
from analyzer.models import Resume

User = get_user_model()

class JobModelTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        
    def test_job_creation(self):
        job = Job.objects.create(
            title='Python Developer',
            description='Looking for a Python developer',
            skills_required='python, django, sql',
            posted_by=self.admin_user
        )
        self.assertEqual(job.title, 'Python Developer')
        self.assertEqual(len(job.get_skills_list()), 3)
        
    def test_get_skills_list(self):
        job = Job.objects.create(
            title='Test Job',
            description='Test description',
            skills_required='python, django, javascript, react',
            posted_by=self.admin_user
        )
        skills = job.get_skills_list()
        self.assertIn('python', skills)
        self.assertIn('django', skills)
        self.assertEqual(len(skills), 4)


class JobApplicationTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123',
            role='user'
        )
        self.job = Job.objects.create(
            title='Python Developer',
            description='Looking for a Python developer',
            skills_required='python, django, sql',
            posted_by=self.admin_user
        )
        self.resume = Resume.objects.create(
            name='Test User',
            cv_url='https://example.com/resume.pdf'
        )
        
    def test_job_application_creation(self):
        application = JobApplication.objects.create(
            job=self.job,
            applicant=self.regular_user,
            resume=self.resume,
            match_score=85.5,
            matched_skills=['python', 'django']
        )
        self.assertEqual(application.match_score, 85.5)
        self.assertEqual(len(application.matched_skills), 2)
        self.assertEqual(application.status, 'pending')