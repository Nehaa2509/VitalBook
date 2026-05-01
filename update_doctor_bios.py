"""
Run with: python update_doctor_bios.py
(from inside the hospital project directory, with venv active)

Or via Django shell:
  python manage.py shell < update_doctor_bios.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital.settings')
django.setup()

from appointment.models import Doctor

DOCTOR_BIOS = [
    {
        "name_fragment": "Meera Iyer",
        "bio": (
            "With over 28 years of distinguished experience in advanced cardiac care, "
            "I specialize in complex heart health diagnostics, interventional cardiology, "
            "and the management of critical cardiovascular conditions. "
            "My deepest commitment is to empower every patient with a personalized, "
            "compassionate treatment plan — because a healthier heart means a healthier life."
        ),
    },
    {
        "name_fragment": "Vikram Singh",
        "bio": (
            "Over my 12 years in cardiology, I have developed specialized expertise in "
            "preventive cardiac care, echocardiography, and the management of arrhythmias "
            "and coronary artery disease. "
            "I believe in listening closely to my patients, building trust, and crafting "
            "evidence-based treatment strategies that put their well-being at the center of every decision."
        ),
    },
    {
        "name_fragment": "Sneha Reddy",
        "bio": (
            "With 32 years at the forefront of clinical neurology, I bring deep expertise "
            "in diagnosing and treating complex neurological disorders including epilepsy, "
            "stroke, Parkinson's disease, and multiple sclerosis. "
            "I am passionately dedicated to improving the quality of life for each patient "
            "through precise diagnosis, innovative therapies, and unwavering support "
            "throughout their neurological journey."
        ),
    },
    {
        "name_fragment": "Kabir Khan",
        "bio": (
            "In my 15 years of practice in neurology, I have honed my skills in "
            "neuro-critical care, headache management, and demyelinating disorders, "
            "working with patients across a wide spectrum of neurological conditions. "
            "I am committed to delivering patient-centered care that combines the latest "
            "medical advancements with genuine empathy and clear, transparent communication."
        ),
    },
    {
        "name_fragment": "Arjun Rao",
        "bio": (
            "With 20 years of surgical expertise in orthopedics, I specialize in "
            "joint replacement surgery, sports medicine, and complex musculoskeletal trauma, "
            "helping patients regain mobility and live pain-free lives. "
            "My practice is built on the belief that every patient deserves a swift return "
            "to function, and I am dedicated to guiding each individual through their "
            "recovery with skill, precision, and compassionate follow-up care."
        ),
    },
    {
        "name_fragment": "Rahul Verma",
        "bio": (
            "Over 14 years in orthopedic surgery, I have developed strong expertise "
            "in minimally invasive procedures, spinal care, and arthroscopic techniques "
            "that minimize surgical impact and accelerate patient recovery. "
            "I am deeply committed to providing personalized rehabilitation plans and "
            "ensuring every patient feels heard, supported, and confident throughout "
            "their path back to an active lifestyle."
        ),
    },
    {
        "name_fragment": "Amit Joshi",
        "bio": (
            "With 16 years of comprehensive practice in general medicine, I offer broad "
            "expertise in the diagnosis and management of acute and chronic conditions, "
            "preventive health screenings, and coordinated multidisciplinary care. "
            "I am wholeheartedly dedicated to building long-term relationships with my "
            "patients — understanding their full health picture and partnering with them "
            "to achieve lasting wellness."
        ),
    },
    {
        "name_fragment": "Rohan Sharma",
        "bio": (
            "In my 5 years as a general medicine physician, I have focused on delivering "
            "thorough, evidence-based primary care — from managing infectious diseases "
            "and metabolic conditions to championing preventive health for my patients. "
            "I am committed to making every consultation a comfortable and informative "
            "experience, ensuring patients leave with clarity, confidence, and a clear "
            "plan for their health."
        ),
    },
    {
        "name_fragment": "Pooja Nair",
        "bio": (
            "With 22 years dedicated to pediatric medicine, I specialize in child "
            "development, neonatal care, pediatric infectious diseases, and the management "
            "of chronic childhood conditions — from newborns to adolescents. "
            "My practice is founded on a deep love for children's health; I work tirelessly "
            "to create a warm, reassuring environment where both young patients and their "
            "families feel genuinely cared for and supported."
        ),
    },
    {
        "name_fragment": "Neha Patel",
        "bio": (
            "In my 6 years of pediatric practice, I have cultivated expertise in "
            "well-child care, childhood immunizations, developmental screenings, "
            "and managing common pediatric illnesses with a gentle, family-centered approach. "
            "I am passionate about nurturing healthy futures for every child in my care "
            "and empowering parents with the knowledge and confidence they need at every "
            "stage of their child's growth."
        ),
    },
    {
        "name_fragment": "Priya Desai",
        "bio": (
            "In my 4 years specializing in dermatology, I have developed focused expertise "
            "in medical and cosmetic skin care, including the treatment of acne, eczema, "
            "psoriasis, and early-stage skin malignancies using evidence-based protocols. "
            "I am committed to helping each patient achieve healthy, radiant skin through "
            "personalized treatment plans that address not just the condition, but the "
            "overall well-being and confidence of the individual."
        ),
    },
    {
        "name_fragment": "Deepa Kumar",
        "bio": (
            "With 3 years of dedicated practice in dermatology, I bring a fresh, "
            "research-driven perspective to skin health — specializing in diagnosing "
            "and treating a full range of dermatological conditions alongside aesthetic "
            "dermatology procedures. "
            "I am deeply committed to delivering gentle, patient-first care and educating "
            "each person about their skin, ensuring they feel empowered and confident in "
            "managing their long-term dermatological health."
        ),
    },
]

updated = 0
not_found = []

for entry in DOCTOR_BIOS:
    fragment = entry["name_fragment"]
    bio = entry["bio"]
    # Try exact match first (name contains fragment, case-insensitive)
    qs = Doctor.objects.filter(name__icontains=fragment)
    if qs.exists():
        for doc in qs:
            doc.bio = bio
            doc.save()
            print(f"  ✅ Updated bio for: {doc.name}")
            updated += 1
    else:
        not_found.append(fragment)
        print(f"  ⚠️  Doctor not found in DB: {fragment}")

print(f"\n✅ Done! Updated {updated} doctor(s).")
if not_found:
    print(f"⚠️  Could not find: {not_found}")
    print("   → These names may be stored differently in the database.")
    print("   → Run: python manage.py shell -c \"from appointment.models import Doctor; print(list(Doctor.objects.values_list('name', flat=True)))\"")
