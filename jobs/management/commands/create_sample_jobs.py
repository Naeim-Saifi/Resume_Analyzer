from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from jobs.models import Job

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample job postings for testing'

    def handle(self, *args, **options):
        # Get or create an admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@example.com',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: admin@example.com / admin123')
            )

        # Sample job data
        sample_jobs = [
            {
                'title': 'Senior Python Developer',
                'description': '''We are looking for an experienced Python developer to join our team.
                
Responsibilities:
- Develop and maintain web applications using Django
- Write clean, maintainable code
- Collaborate with cross-functional teams
- Participate in code reviews

Requirements:
- 5+ years of Python experience
- Strong knowledge of Django framework
- Experience with SQL databases
- Knowledge of REST APIs''',
                'skills_required': 'python, django, sql, rest api, git',
                'experience_level': 'senior',
                'location': 'San Francisco, CA',
                'salary_range': '$120,000 - $160,000',
                'company_name': 'TechCorp Inc.'
            },
            {
                'title': 'Frontend React Developer',
                'description': '''Join our frontend team to build amazing user interfaces.
                
What you'll do:
- Build responsive web applications using React
- Collaborate with designers and backend developers
- Optimize applications for performance
- Write unit tests

What we're looking for:
- 3+ years of React experience
- Strong JavaScript and CSS skills
- Experience with modern frontend tools''',
                'skills_required': 'javascript, react, html, css, git',
                'experience_level': 'mid',
                'location': 'New York, NY',
                'salary_range': '$90,000 - $120,000',
                'company_name': 'WebSolutions LLC'
            },
            {
                'title': 'Data Scientist',
                'description': '''We're seeking a data scientist to help drive data-driven decisions.
                
Responsibilities:
- Analyze large datasets to extract insights
- Build machine learning models
- Create data visualizations
- Present findings to stakeholders

Requirements:
- Strong Python and SQL skills
- Experience with machine learning libraries
- Knowledge of statistics and data analysis''',
                'skills_required': 'python, machine learning, sql, pandas, numpy, data analysis',
                'experience_level': 'mid',
                'location': 'Remote',
                'salary_range': '$100,000 - $140,000',
                'company_name': 'DataTech Solutions'
            },
            {
                'title': 'Junior Web Developer',
                'description': '''Great opportunity for a junior developer to grow their skills.
                
What you'll learn:
- Full-stack web development
- Working with databases
- Version control with Git
- Agile development practices

Requirements:
- Basic knowledge of HTML, CSS, JavaScript
- Familiarity with at least one backend language
- Eagerness to learn and grow''',
                'skills_required': 'html, css, javascript, python, git',
                'experience_level': 'entry',
                'location': 'Austin, TX',
                'salary_range': '$60,000 - $80,000',
                'company_name': 'StartupXYZ'
            },
            {
                'title': 'DevOps Engineer',
                'description': '''Looking for a DevOps engineer to help scale our infrastructure.
                
Responsibilities:
- Manage cloud infrastructure
- Implement CI/CD pipelines
- Monitor system performance
- Ensure security best practices

Skills needed:
- Experience with cloud platforms (AWS, Azure, GCP)
- Knowledge of containerization (Docker, Kubernetes)
- Scripting and automation skills''',
                'skills_required': 'aws, docker, kubernetes, python, linux, git',
                'experience_level': 'senior',
                'location': 'Seattle, WA',
                'salary_range': '$130,000 - $170,000',
                'company_name': 'CloudFirst Technologies'
            }
        ]

        created_count = 0
        for job_data in sample_jobs:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                posted_by=admin_user,
                defaults=job_data
            )
            if created:
                created_count += 1
                self.stdout.write(f'Created job: {job.title}')

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} sample jobs')
        )