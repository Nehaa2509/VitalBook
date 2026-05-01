import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from appointment.models import Doctor

for d in Doctor.objects.all():
    uname = d.user.username if d.user else "NO USER"
    print(f"{d.name} -> {uname}")
