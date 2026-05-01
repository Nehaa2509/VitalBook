import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from appointment.models import Doctor

DOCTORS_DATA = [
    {"name": "Meera Iyer", "designation": "Senior Consultant / HOD", "fee": 800, "bio": "With over 28 years of distinguished experience in advanced cardiac care, I specialize in complex heart health diagnostics and interventional cardiology. My deepest commitment is to empower every patient with a personalized, compassionate treatment plan."},
    {"name": "Vikram Singh", "designation": "Consultant", "fee": 500, "bio": "Over my 12 years in cardiology, I have developed specialized expertise in preventive cardiac care and echocardiography. I believe in listening closely to my patients and crafting evidence-based strategies that put their well-being at the center of every decision."},
    {"name": "Sneha Reddy", "designation": "Senior Consultant / HOD", "fee": 900, "bio": "With 32 years at the forefront of clinical neurology, I bring deep expertise in diagnosing complex neurological disorders including epilepsy and stroke. I am passionately dedicated to improving quality of life through precise diagnosis and innovative therapies."},
    {"name": "Kabir Khan", "designation": "Consultant", "fee": 600, "bio": "In my 15 years of practice, I have honed my skills in neuro-critical care and headache management. I am committed to delivering patient-centered care that combines the latest medical advancements with genuine empathy."},
    {"name": "Arjun Rao", "designation": "Senior Consultant / HOD", "fee": 700, "bio": "With 20 years of surgical expertise, I specialize in joint replacement surgery and sports medicine. My practice is built on the belief that every patient deserves a swift return to function and a pain-free life."},
    {"name": "Rahul Verma", "designation": "Consultant", "fee": 400, "bio": "Over 14 years in orthopedic surgery, I have developed strong expertise in minimally invasive procedures and spinal care. I am committed to providing personalized rehabilitation plans so patients feel supported throughout their recovery."},
    {"name": "Amit Joshi", "designation": "Consultant", "fee": 500, "bio": "With 16 years of comprehensive practice, I offer broad expertise in the diagnosis of acute and chronic conditions. I am wholeheartedly dedicated to building long-term relationships and partnering with patients to achieve lasting wellness."},
    {"name": "Rohan Sharma", "designation": "Junior Resident", "fee": 300, "bio": "In my 5 years as a physician, I have focused on delivering thorough, evidence-based primary care. I am committed to making every consultation a comfortable experience, ensuring patients leave with clarity and a clear health plan."},
    {"name": "Pooja Nair", "designation": "Senior Consultant / HOD", "fee": 600, "bio": "With 22 years dedicated to pediatric medicine, I specialize in child development and neonatal care. I work tirelessly to create a reassuring environment where both young patients and their families feel supported."},
    {"name": "Neha Patel", "designation": "Junior Resident", "fee": 350, "bio": "In my 6 years of practice, I have cultivated expertise in well-child care and developmental screenings. I am passionate about nurturing healthy futures for every child and empowering parents with confidence at every stage."},
    {"name": "Priya Desai", "designation": "Junior Resident", "fee": 400, "bio": "In my 4 years specializing in dermatology, I have developed expertise in medical and cosmetic skin care. I am committed to helping each patient achieve healthy, radiant skin through plans that address both skin health and overall confidence."},
    {"name": "Deepa Kumar", "designation": "Junior Resident", "fee": 250, "bio": "With 3 years of dedicated practice, I bring a fresh, research-driven perspective to skin health and aesthetic procedures. I am committed to delivering patient-first care and ensuring patients feel empowered in managing their long-term health."}
]

updated_count = 0
for data in DOCTORS_DATA:
    qs = Doctor.objects.filter(name__icontains=data["name"])
    if qs.exists():
        for doc in qs:
            doc.bio = data["bio"]
            doc.consultation_fee = data["fee"]
            doc.designation = data["designation"]
            doc.save()
            print(f"Updated: {doc.name} (Fee: {doc.consultation_fee}, Desig: {doc.designation})")
            updated_count += 1
    else:
        print(f"Could not find: {data['name']}")

print(f"\nTotal doctors updated: {updated_count}")
