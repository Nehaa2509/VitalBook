import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from appointment.models import Doctor, Specialization

DOCTORS_SPECS = [
    {"name": "Meera Iyer", "spec": "Cardiology"},
    {"name": "Vikram Singh", "spec": "Cardiology"},
    {"name": "Sneha Reddy", "spec": "Neurology"},
    {"name": "Kabir Khan", "spec": "Neurology"},
    {"name": "Arjun Rao", "spec": "Orthopedics"},
    {"name": "Rahul Verma", "spec": "Orthopedics"},
    {"name": "Amit Joshi", "spec": "General Medicine"},
    {"name": "Rohan Sharma", "spec": "General Medicine"},
    {"name": "Pooja Nair", "spec": "Pediatrics"},
    {"name": "Neha Patel", "spec": "Pediatrics"},
    {"name": "Priya Desai", "spec": "Dermatology"},
    {"name": "Deepa Kumar", "spec": "Dermatology"},
]

updated_count = 0

for data in DOCTORS_SPECS:
    # Get or create the specialization
    spec_obj, created = Specialization.objects.get_or_create(name=data["spec"])
    
    # Update doctors matching the name
    qs = Doctor.objects.filter(name__icontains=data["name"])
    for doc in qs:
        doc.specialization = spec_obj
        doc.save()
        print(f"Updated {doc.name} specialization to {spec_obj.name}")
        updated_count += 1

print(f"\nTotal doctors updated with new specializations: {updated_count}")
