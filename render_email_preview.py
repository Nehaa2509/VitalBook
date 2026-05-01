import os
import django
from django.conf import settings
from django.template.loader import render_to_string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

context = {
    'patient_name': 'John Doe',
    'doctor_name': 'Sarah Smith',
    'date': '24 April 2026',
    'medicines': '1. Amoxicillin 500mg - 1 tablet twice a day for 5 days\n2. Paracetamol 500mg - 1 tablet as needed for fever',
    'instructions': 'Please take the antibiotics after meals. Drink plenty of water and rest well. If symptoms persist, contact the clinic.',
}

html_content = render_to_string('emails/prescription_email.html', context)

with open('preview_email.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("Template rendered successfully to preview_email.html")
