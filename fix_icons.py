import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from appointment.models import Specialization

icon_map = {
    "Cardiology": "fa-heartbeat",
    "Neurology": "fa-brain",
    "Orthopedics": "fa-bone",
    "General Medicine": "fa-stethoscope",
    "Pediatrics": "fa-baby",
    "Dermatology": "fa-allergies"
}

for spec in Specialization.objects.all():
    if spec.name in icon_map:
        spec.icon = icon_map[spec.name]
        spec.save()
        print(f"Fixed {spec.name} icon to {spec.icon}")
