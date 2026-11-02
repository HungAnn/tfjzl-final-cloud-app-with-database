"""Create a local example course and print a temporary admin password."""

import os
import secrets

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

import django

django.setup()

from django.contrib.auth.models import User
from onlinecourse.models import Choice, Course, Enrollment, Instructor, Lesson, Question


password = secrets.token_urlsafe(18)
user, _ = User.objects.get_or_create(username='admin')
user.first_name = 'Demo'
user.is_staff = True
user.is_superuser = True
user.set_password(password)
user.save()

instructor, _ = Instructor.objects.get_or_create(
    user=user, defaults={'full_time': True, 'total_learners': 1}
)
course, _ = Course.objects.get_or_create(name='Learning Django', defaults={
    'description': 'An introduction to the Django web framework.',
    'image': 'course_images/django.png',
    'total_enrollment': 1,
})
course.instructors.add(instructor)
Enrollment.objects.get_or_create(user=user, course=course, defaults={'mode': 'honor'})
Lesson.objects.get_or_create(course=course, order=0, defaults={
    'title': 'What is Django?',
    'content': 'Django is a Python web framework for building applications.'
})
Lesson.objects.get_or_create(course=course, order=1, defaults={
    'title': 'Models and views',
    'content': 'Models store data; views handle requests and return responses.'
})
question, _ = Question.objects.get_or_create(
    course=course, content='Is Django a Python web framework?', defaults={'grade': 50}
)
Choice.objects.get_or_create(question=question, content='Yes', defaults={'is_correct': True})
Choice.objects.get_or_create(question=question, content='No', defaults={'is_correct': False})
question, _ = Question.objects.get_or_create(
    course=course, content='Which parts belong to a Django application?', defaults={'grade': 50}
)
Choice.objects.get_or_create(question=question, content='Models', defaults={'is_correct': True})
Choice.objects.get_or_create(question=question, content='Views', defaults={'is_correct': True})
Choice.objects.get_or_create(question=question, content='Spreadsheet macros', defaults={'is_correct': False})

print('Local admin username: admin')
print(f'Temporary password: {password}')
