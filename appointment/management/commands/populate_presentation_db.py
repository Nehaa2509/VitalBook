"""
╔═══════════════════════════════════════════════════════════════╗
║   VITALBOOK — PRESENTATION DATABASE POPULATION               ║
║   10 Doctors | 25 Patients | 100 Appointments + Reviews      ║
╚═══════════════════════════════════════════════════════════════╝

Run:  python manage.py populate_presentation_db
"""

import random
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker

from appointment.models import Specialization, Doctor, Patient, Appointment, Review

fake = Faker('en_IN')

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION — Exact presentation numbers
# ═══════════════════════════════════════════════════════════
NUM_DOCTORS = 12
NUM_PATIENTS = 25
NUM_APPOINTMENTS = 100
REVIEW_RATE = 0.70  # 70% of completed appointments get reviews

# 6 Core specializations for presentation
CORE_SPECIALIZATIONS = [
    ('Cardiology',            'Heart & cardiovascular diseases', 'fa-heartbeat'),
    ('Neurology',             'Brain & nervous system disorders', 'fa-brain'),
    ('Orthopedics',           'Bones, joints & muscle disorders', 'fa-bone'),
    ('General Medicine',      'Primary internal medicine', 'fa-stethoscope'),
    ('Pediatrics',            'Child & adolescent healthcare', 'fa-baby'),
    ('Dermatology',           'Skin, hair & nail disorders', 'fa-allergies'),
]

NAMES_F = [
    'Aarav','Aditi','Akash','Amara','Ananya','Anil','Anjali','Arjun','Arpita','Aryan',
    'Ashok','Ayush','Bhavna','Chaitanya','Chetan','Deepa','Deepak','Devika','Dinesh',
    'Diya','Divya','Ganesh','Garima','Gaurav','Geeta','Hari','Harsha','Isha','Ishita',
    'Jaya','Jitendra','Kajal','Karan','Kavita','Kavya','Kiran','Krishna','Kumar','Kunal',
    'Lakshmi','Lata','Madhav','Mahesh','Mohan','Mukul','Naina','Narendra','Neha','Nikhil',
    'Nirmala','Nisha','Om','Pallavi','Pankaj','Parvati','Pooja','Pranav','Prasad','Priya',
    'Puja','Radha','Raghav','Rahul','Raj','Rajesh','Rakesh','Ram','Ramesh','Rani',
    'Ravi','Rekha','Ritu','Rohan','Rohit','Rukmini','Sachin','Sahil','Sakshi','Sameer',
    'Sandeep','Sanjay','Sapna','Sarita','Shalini','Shanti','Shruti','Shubham','Siddharth','Sita',
    'Sneha','Sonali','Sunita','Suraj','Swati','Tarun','Usha','Vandana','Varun','Ved',
    'Vidya','Vijay','Vikram','Vinay','Vinita','Vishal','Vivek','Yamini','Yogesh',
]
NAMES_L = [
    'Agarwal','Anand','Arora','Banerjee','Bhatt','Bose','Chandra','Chatterjee','Chauhan','Chopra',
    'Das','Deshpande','Dubey','Dutta','Ghosh','Gowda','Gupta','Hegde','Iyer','Jain',
    'Joshi','Kapur','Khanna','Kulkarni','Kumar','Malhotra','Mehta','Menon','Mishra','Mukherjee',
    'Nair','Pandey','Pathak','Patel','Pillai','Rao','Rathore','Reddy','Roy','Sarkar',
    'Sen','Sethi','Shah','Sharma','Singh','Sinha','Tiwari','Trivedi','Verma',
]

BLOODS = ['A+','A-','B+','B-','AB+','AB-','O+','O-']
GENDERS = ['Male','Female','Other']
DAYS = ['Mon-Fri','Mon-Sat','Tue-Sat','Mon-Thu','Mon-Wed,Fri']
TIMES = ['9:00 AM - 1:00 PM','10:00 AM - 2:00 PM','2:00 PM - 6:00 PM','3:00 PM - 7:00 PM','9:00 AM - 5:00 PM']
STATUSES = ['Pending','Confirmed','Completed','Cancelled']
STATUS_W = [15, 25, 50, 10]
SYMPTOMS = [
    'Fever and body ache','Persistent cough','Headache and dizziness','Stomach pain and nausea',
    'Joint pain and swelling','Skin rash and itching','Breathing difficulty','Chest pain',
    'Back pain','Eye redness','Ear pain','Sore throat','Urinary discomfort',
    'Weight loss and fatigue','High blood pressure','Diabetes management','Allergic reaction',
    'Vomiting and diarrhea','Migraine','Insomnia',
]

REVIEW_COMMENTS = [
    "Excellent doctor, very thorough in examination.",
    "Great experience, felt very comfortable.",
    "Doctor was very professional and explained everything clearly.",
    "Highly recommended, very knowledgeable specialist.",
    "Good consultation, but had to wait a bit long.",
    "Very caring and attentive doctor.",
    "Diagnosed the issue quickly and prescribed effective treatment.",
    "Clean clinic, friendly staff, and excellent doctor.",
    "Doctor listened patiently and gave good advice.",
    "Very experienced doctor, felt confident in the treatment.",
    "Pleasant experience overall. Doctor was very helpful.",
    "Amazing doctor, solved my problem in one visit.",
    "Very professional and courteous. Will visit again.",
    "Good doctor but consultation felt a bit rushed.",
    "Thorough examination, clear diagnosis, reasonable fees.",
    "Doctor was empathetic and took time to explain the condition.",
    "Best doctor I have consulted. Very satisfied.",
    "Efficient and professional service. Highly recommended.",
    "Doctor was friendly and the treatment worked well.",
    "Very good experience, doctor was very patient.",
]


class Command(BaseCommand):
    help = 'Populate VitalBook with 10 doctors, 25 patients, 100 appointments + reviews'

    def handle(self, *args, **options):
        self.stdout.write('\n ╔══════════════════════════════════════════════════════════════╗')
        self.stdout.write(' ║   VITALBOOK — PRESENTATION DATABASE POPULATION             ║')
        self.stdout.write(' ╚══════════════════════════════════════════════════════════════╝')

        specs = self._specs()
        doctors = self._doctors(specs)
        patients = self._patients()
        appointments = self._appts(doctors, patients)
        self._reviews(appointments)

        self.stdout.write('\n ✅ Done! Database populated for presentation.')

    def _calc_doctor_pricing(self, exp, spec_name):
        """
        Compressed pricing matrix (₹200 - ₹1000 cap):
        1. Base fee by experience bracket
        2. Super-specialist override (premium fields + 15+ years) → ₹1000
        """
        # 1. Base Experience & Fee
        if exp <= 9:
            designation = 'Junior Resident / Medical Officer'
            fee = random.randint(200, 400)
        elif exp <= 19:
            designation = 'Consultant / Specialist (MD/MS)'
            fee = random.randint(400, 700)
        else:
            designation = 'Senior Consultant / HOD'
            fee = random.randint(700, 1000)

        # 2. Super-Specialist Override (max cap ₹1000)
        premium_specs = {'Cardiology', 'Neurosurgery', 'Cardiothoracic Surgery', 'Oncology'}
        if spec_name in premium_specs and exp >= 15:
            fee = 1000

        return designation, fee

    def _specs(self):
        self.stdout.write('\n 📋 Step 1/5 — 4 core specializations...')
        existing = {s.name for s in Specialization.objects.all()}
        new = [Specialization(name=n, description=d, icon=i) for n, d, i in CORE_SPECIALIZATIONS if n not in existing]
        if new:
            Specialization.objects.bulk_create(new, batch_size=10)
        s = list(Specialization.objects.filter(name__in=[sp[0] for sp in CORE_SPECIALIZATIONS]))
        self.stdout.write(f'    ✅ {len(s)} specializations ready.')
        return s

    def _doctors(self, specs):
        self.stdout.write(f'\n 👨‍⚕️  Step 2/5 — {NUM_DOCTORS} doctors...')
        Doctor.objects.all().delete()
        User.objects.filter(username__regex='^[A-Z]{2}$').delete()
        User.objects.filter(username__startswith='dr_').delete()

        # Hardcoded 12 Specific Demo Doctors (2 per specialization)
        demo_doctors = [
            # Cardiology (2)
            {"name": "Vikram Singh", "designation": "Consultant / Specialist (MD/MS)", "spec": "Cardiology", "exp": 12, "fee": 600, "phone": "+919876543210"},
            {"name": "Meera Iyer", "designation": "Senior Consultant / HOD", "spec": "Cardiology", "exp": 28, "fee": 1000, "phone": "+919876543211"},
            # Neurology (2)
            {"name": "Kabir Khan", "designation": "Consultant / Specialist (MD/MS)", "spec": "Neurology", "exp": 15, "fee": 700, "phone": "+919876543212"},
            {"name": "Sneha Reddy", "designation": "Chief Consultant / HOD", "spec": "Neurology", "exp": 32, "fee": 950, "phone": "+919876543213"},
            # Orthopedics (2)
            {"name": "Neha Patel", "designation": "Junior Resident / Medical Officer", "spec": "Orthopedics", "exp": 6, "fee": 350, "phone": "+919876543214"},
            {"name": "Pooja Nair", "designation": "Senior Consultant", "spec": "Orthopedics", "exp": 22, "fee": 850, "phone": "+919876543215"},
            # General Medicine (2)
            {"name": "Rohan Sharma", "designation": "Junior Resident / Medical Officer", "spec": "General Medicine", "exp": 5, "fee": 300, "phone": "+919876543216"},
            {"name": "Rahul Verma", "designation": "Consultant / Specialist (MD/MS)", "spec": "General Medicine", "exp": 14, "fee": 650, "phone": "+919876543217"},
            # Pediatrics (2)
            {"name": "Priya Desai", "designation": "Junior Resident / Medical Officer", "spec": "Pediatrics", "exp": 4, "fee": 280, "phone": "+919876543218"},
            {"name": "Amit Joshi", "designation": "Consultant / Specialist (MD/MS)", "spec": "Pediatrics", "exp": 16, "fee": 750, "phone": "+919876543219"},
            # Dermatology (2)
            {"name": "Deepa Kumar", "designation": "Junior Resident / Medical Officer", "spec": "Dermatology", "exp": 3, "fee": 250, "phone": "+919876543220"},
            {"name": "Arjun Rao", "designation": "Senior Consultant", "spec": "Dermatology", "exp": 20, "fee": 900, "phone": "+919876543221"},
        ]

        spec_map = {s.name: s for s in specs}
        users, docs = [], []

        for i, doc_data in enumerate(demo_doctors):
            first = doc_data['name'].split()[0]
            last = doc_data['name'].split()[-1]
            uname = f'{first[0]}{last[0]}'.upper()  # 2-char initials (e.g., VS)
            email = f'{uname.lower()}@vitalbook.in'
            users.append(User(username=uname, email=email, first_name=first, last_name=last, is_staff=False, is_active=True))

            spec = spec_map.get(doc_data['spec'])
            docs.append(Doctor(
                user=None,
                name=f'{doc_data["name"]}',  # Clean name without "Dr." for avatar matching
                specialization=spec,
                qualification='MBBS, MD' if doc_data['exp'] > 10 else 'MBBS',
                designation=doc_data['designation'],
                experience_years=doc_data['exp'],
                consultation_fee=doc_data['fee'],
                available_days=random.choice(DAYS),
                available_time=random.choice(TIMES),
                email=email,
                phone=doc_data['phone'],
                bio=fake.text(max_nb_chars=150),
                image='default-doctor.jpg',
                is_available=True,
                rating=round(random.uniform(3.5, 5.0), 2),
            ))

        User.objects.bulk_create(users)
        created = {u.username: u for u in User.objects.all() if u.username in [f'{d["name"].split()[0][0]}{d["name"].split()[-1][0]}'.upper() for d in demo_doctors]}
        for u, d in zip(users, docs):
            d.user = created.get(u.username)
        Doctor.objects.bulk_create(docs)
        self.stdout.write(f'    ✅ {len(docs)} doctors created with fixed pricing.')
        return list(Doctor.objects.all())

    def _patients(self):
        self.stdout.write(f'\n 👥 Step 3/5 — {NUM_PATIENTS} patients...')
        Patient.objects.all().delete()
        User.objects.filter(username__startswith='pt_').delete()

        users, pats = [], []
        for i in range(NUM_PATIENTS):
            first = NAMES_F[(i + 10) % len(NAMES_F)]
            last = NAMES_L[(i + 10) % len(NAMES_L)]
            uname = f'pt_{first.lower()}_{last.lower()}'
            email = f'{first.lower()}.{last.lower()}{i}@email.com'
            users.append(User(username=uname, email=email, first_name=first, last_name=last, is_staff=False, is_active=True))
            pats.append(Patient(
                user=None, name=f'{first} {last}', email=email,
                phone=f'+91{random.randint(6000000000,9999999999)}',
                date_of_birth=fake.date_of_birth(minimum_age=5, maximum_age=75),
                gender=random.choice(GENDERS), blood_group=random.choice(BLOODS),
                address=fake.address().replace('\n',', ')[:200],
                emergency_contact=f'+91{random.randint(6000000000,9999999999)}',
                medical_history=fake.text(max_nb_chars=100) if random.random() > 0.5 else '',
            ))

        User.objects.bulk_create(users)
        created = {u.username: u for u in User.objects.filter(username__startswith='pt_')}
        for u, p in zip(users, pats):
            p.user = created.get(u.username)
        Patient.objects.bulk_create(pats)
        self.stdout.write(f'    ✅ {len(pats)} patients created.')
        return list(Patient.objects.all())

    def _appts(self, doctors, patients):
        self.stdout.write(f'\n 📅 Step 4/5 — {NUM_APPOINTMENTS} appointments...')
        Appointment.objects.all().delete()

        today = datetime.date.today()
        objs = []
        for i in range(NUM_APPOINTMENTS):
            d = today - datetime.timedelta(days=random.randint(1, 120))
            h, m = random.randint(8, 17), random.choice([0, 15, 30, 45])
            objs.append(Appointment(
                patient=random.choice(patients), doctor=random.choice(doctors),
                date=d, time=datetime.time(h, m),
                status=random.choices(STATUSES, weights=STATUS_W, k=1)[0],
                reason=random.choice(SYMPTOMS),
                symptoms=fake.text(max_nb_chars=80) if random.random() > 0.4 else '',
            ))
        Appointment.objects.bulk_create(objs)
        self.stdout.write(f'    ✅ {len(objs)} appointments created.')
        return list(Appointment.objects.all())

    def _reviews(self, appointments):
        self.stdout.write('\n ⭐ Step 5/5 — Generating reviews for completed appointments...')
        Review.objects.all().delete()

        completed = [a for a in appointments if a.status == 'Completed']
        if not completed:
            self.stdout.write('    ⏭  No completed appointments found.')
            return

        review_count = int(len(completed) * REVIEW_RATE)
        to_review = random.sample(completed, min(review_count, len(completed)))

        reviews = []
        for appt in to_review:
            rating = random.choices([1, 2, 3, 4, 5], weights=[2, 3, 10, 35, 50], k=1)[0]
            comment = random.choice(REVIEW_COMMENTS)
            reviews.append(Review(
                appointment=appt,
                patient=appt.patient,
                doctor=appt.doctor,
                rating=rating,
                comment=comment,
            ))

        Review.objects.bulk_create(reviews)
        self.stdout.write(f'    ✅ {len(reviews)} reviews generated ({REVIEW_RATE*100:.0f}% of {len(completed)} completed).')

        from django.db.models import Avg
        for doc in Doctor.objects.all():
            avg = Review.objects.filter(doctor=doc).aggregate(a=Avg('rating'))['a']
            if avg:
                doc.rating = round(avg, 2)
                doc.save(update_fields=['rating'])
        self.stdout.write('    ✅ Doctor ratings updated.')
