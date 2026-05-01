"""
╔═══════════════════════════════════════════════════════════════╗
║   VITALBOOK — ENTERPRISE-SCALE DATABASE POPULATION v2        ║
║   41 Specializations | 500 Doctors | 10K Patients | 50K      ║
║   Appointments + Realistic Reviews                           ║
╚═══════════════════════════════════════════════════════════════╝

Install:  pip install Faker
Run:      python manage.py populate_massive_db
"""

import random
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker

from appointment.models import Specialization, Doctor, Patient, Appointment, Review

fake = Faker('en_IN')

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════
NUM_DOCTORS = 500
NUM_PATIENTS = 10000
NUM_APPOINTMENTS = 50000
REVIEW_RATE = 0.60  # 60% of completed appointments get a review
BATCH = 2000

SPECIALIZATIONS = [
    ('Anesthesiology',        'Administration of anesthesia for surgeries', 'fa-syringe'),
    ('Bariatric Surgery',     'Weight-loss surgical procedures', 'fa-weight-scale'),
    ('Cardiology',            'Heart & cardiovascular diseases', 'fa-heartbeat'),
    ('Cardiothoracic Surgery','Heart, lung & chest surgery', 'fa-lungs'),
    ('Dermatology',           'Skin, hair & nail disorders', 'fa-allergies'),
    ('Emergency Medicine',    'Urgent & critical care treatment', 'fa-truck-medical'),
    ('Endocrinology',         'Hormonal & metabolic disorders', 'fa-dna'),
    ('ENT',                   'Ear, Nose & Throat specialist', 'fa-ear-listen'),
    ('Family Medicine',       'Comprehensive primary healthcare', 'fa-house-medical'),
    ('Gastroenterology',      'Digestive system & liver disorders', 'fa-stomach'),
    ('General Medicine',      'Primary internal medicine', 'fa-stethoscope'),
    ('General Surgery',       'Broad surgical expertise', 'fa-scalpel'),
    ('Geriatrics',            'Healthcare for elderly patients', 'fa-person-cane'),
    ('Gynecology',            "Women's reproductive health", 'fa-female'),
    ('Hematology',            'Blood disorders & bone marrow', 'fa-vial'),
    ('Hepatology',            'Liver, gallbladder & biliary system', 'fa-liver'),
    ('Immunology',            'Immune system & allergy disorders', 'fa-shield-virus'),
    ('Infectious Disease',    'Bacterial, viral & fungal infections', 'fa-virus'),
    ('Internal Medicine',     'Adult disease diagnosis & treatment', 'fa-user-doctor'),
    ('Nephrology',            'Kidney diseases & dialysis', 'fa-kidneys'),
    ('Neurology',             'Brain & nervous system disorders', 'fa-brain'),
    ('Neurosurgery',          'Surgical brain & spine procedures', 'fa-head-side-brain'),
    ('Nuclear Medicine',      'Radioisotope diagnostic imaging', 'fa-radiation'),
    ('Obstetrics',            'Pregnancy & childbirth care', 'fa-baby-carriage'),
    ('Oncology',              'Cancer diagnosis & treatment', 'fa-ribbon'),
    ('Ophthalmology',         'Eye care & vision correction', 'fa-eye'),
    ('Orthopedics',           'Bones, joints & muscle disorders', 'fa-bone'),
    ('Palliative Care',       'Pain relief & quality of life', 'fa-hand-holding-heart'),
    ('Pathology',             'Laboratory diagnosis & testing', 'fa-microscope'),
    ('Pediatric Surgery',     'Surgical care for children', 'fa-child-reaching'),
    ('Pediatrics',            'Child & adolescent healthcare', 'fa-baby'),
    ('Physical Medicine',     'Rehabilitation & pain management', 'fa-crutch'),
    ('Plastic Surgery',       'Reconstructive & cosmetic surgery', 'fa-face-smile'),
    ('Psychiatry',            'Mental health & behavioural disorders', 'fa-head-side-virus'),
    ('Pulmonology',           'Lung & respiratory system care', 'fa-wind'),
    ('Radiology',             'Medical imaging & diagnostics', 'fa-x-ray'),
    ('Rheumatology',          'Joint & autoimmune disorders', 'fa-hand-holding-medical'),
    ('Sports Medicine',       'Athletic injuries & performance', 'fa-person-running'),
    ('Trauma Surgery',        'Emergency trauma & injury care', 'fa-kit-medical'),
    ('Urology',               'Urinary & male reproductive system', 'fa-droplet'),
    ('Vascular Surgery',      'Artery & vein surgical treatment', 'fa-heart-pulse'),
]

# Designation hierarchy: (title, exp_range, weight, fee_range)
DESIGNATIONS = [
    ('Head of Department',         (20, 35), 5,  (1500, 2500)),
    ('Senior Consultant',          (15, 20), 15, (1000, 1400)),
    ('Attending Specialist',       (8, 15),  30, (700, 900)),
    ('Junior Consultant',          (4, 8),   30, (400, 600)),
    ('Resident Medical Officer',   (1, 3),   20, (200, 300)),
]

QUAL_MAP = {
    'Head of Department':       ['MBBS, MD, DM', 'MBBS, MS, MCh', 'MBBS, MD, DNB'],
    'Senior Consultant':        ['MBBS, MD', 'MBBS, MS', 'MBBS, DNB'],
    'Attending Specialist':     ['MBBS, MD', 'MBBS, MS', 'MBBS, DNB'],
    'Junior Consultant':        ['MBBS, MD', 'MBBS, MS'],
    'Resident Medical Officer': ['MBBS'],
}

NAMES_F = [
    'Aarav','Aditi','Aisha','Akash','Amara','Ananya','Anil','Anjali','Arjun','Arpita',
    'Aryan','Ashok','Ayush','Bhavna','Chaitanya','Chetan','Deepa','Deepak','Devika','Dinesh',
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
STATUS_W = [12,38,40,10]
SYMPTOMS = [
    'Fever and body ache','Persistent cough','Headache and dizziness','Stomach pain and nausea',
    'Joint pain and swelling','Skin rash and itching','Breathing difficulty','Chest pain',
    'Back pain','Eye redness','Ear pain','Sore throat','Urinary discomfort',
    'Weight loss and fatigue','High blood pressure','Diabetes management','Allergic reaction',
    'Vomiting and diarrhea','Migraine','Insomnia',
]

# Realistic review comments pool
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
    help = 'Populate VitalBook with 41 specializations, 500 doctors, 10K patients, 50K appointments + reviews'

    def handle(self, *args, **options):
        self.stdout.write('\n ╔══════════════════════════════════════════════════════════════╗')
        self.stdout.write(' ║   VITALBOOK — ENTERPRISE DATABASE POPULATION v2            ║')
        self.stdout.write(' ╚══════════════════════════════════════════════════════════════╝')

        specs = self._specs()
        doctors = self._doctors(specs)
        patients = self._patients()
        self._appts(doctors, patients)
        self._reviews()

        self.stdout.write('\n ✅ Done! Database fully populated.')

    # ── helpers ──────────────────────────────────────────────
    def _calc_doctor_pricing(self, exp, spec_name):
        """
        Real-world pricing matrix:
        1. Designation & Base Fee by Experience Bracket
        2. Super-Specialist Override (Premium fields + 15+ years exp)
        """
        if exp <= 9:
            designation, fee = 'Junior Resident / Medical Officer', random.randint(200, 600)
        elif exp <= 19:
            designation, fee = 'Consultant / Specialist (MD/MS)', random.randint(500, 1000)
        elif exp <= 34:
            designation, fee = 'Senior Consultant', random.randint(800, 1800)
        else:
            designation, fee = 'Chief Consultant / HOD', random.randint(1200, 2500)

        # Super-Specialist Override
        if spec_name in ('Cardiology', 'Neurosurgery', 'Cardiothoracic Surgery', 'Oncology') and exp >= 15:
            fee = random.randint(2000, 5000)
        return designation, fee

    # ── Step 1: Specializations ────────────────────────────
    def _specs(self):
        self.stdout.write('\n 📋 Step 1/5 — 41 specializations (A→Z)...')
        existing = {s.name for s in Specialization.objects.all()}
        new = [Specialization(name=n, description=d, icon=i) for n, d, i in SPECIALIZATIONS if n not in existing]
        if new:
            Specialization.objects.bulk_create(new, batch_size=50)
        s = list(Specialization.objects.all())
        self.stdout.write(f'    ✅ {len(s)} specializations ready.')
        return s

    # ── Step 2: 500 Doctors (no 'Dr. Dr.' bug) ─────────────
    def _doctors(self, specs):
        self.stdout.write(f'\n 👨‍⚕️  Step 2/5 — {NUM_DOCTORS} doctors...')
        existing = Doctor.objects.count()
        if existing >= NUM_DOCTORS:
            self.stdout.write(f'    ⏭  {existing} exist — skipping.')
            return list(Doctor.objects.all())

        needed = NUM_DOCTORS - existing
        users, docs = [], []
        for i in range(needed):
            # FIX #1: Use first_name + last_name directly (no fake.name() prefix)
            first = random.choice(NAMES_F)
            last = random.choice(NAMES_L)
            idx = existing + i
            uname = f'dr_{first.lower()}_{last.lower()}_{idx}'
            email = f'{first.lower()}.{last.lower()}{idx}@vitalbook.in'
            
            # Real-world pricing matrix logic
            exp = random.randint(3, 40)
            spec = random.choice(specs)
            des, fee = self._calc_doctor_pricing(exp, spec.name)
            
            users.append(User(username=uname, email=email, first_name=first, last_name=last, is_staff=False, is_active=True))
            docs.append(Doctor(
                user=None,
                name=f'Dr. {first} {last}',  # Prefix stored in DB, templates use {{ doctor.name }}
                specialization=spec,
                qualification=random.choice(QUAL_MAP.get(des, ['MBBS'])),
                designation=des,
                experience_years=exp,
                consultation_fee=fee,
                available_days=random.choice(DAYS),
                available_time=random.choice(TIMES),
                email=email,
                phone=f'+91{random.randint(6000000000,9999999999)}',
                bio=fake.text(max_nb_chars=150),
                image='default-doctor.jpg',
                is_available=random.choices([True]*85 + [False]*15, k=1)[0],
                rating=round(random.uniform(3.0, 5.0), 2),
            ))

        self.stdout.write(f'    → Creating {len(users)} users...')
        User.objects.bulk_create(users, batch_size=BATCH)
        created = {u.username: u for u in User.objects.filter(username__startswith='dr_').order_by('-id')[:needed]}
        for u, d in zip(users, docs):
            d.user = created.get(u.username)
        Doctor.objects.bulk_create(docs, batch_size=BATCH)
        self.stdout.write(f'    ✅ {len(docs)} doctors created with market-rate fees.')
        return list(Doctor.objects.all())

    # ── Step 3: 10,000 Patients ────────────────────────────
    def _patients(self):
        self.stdout.write(f'\n 👥 Step 3/5 — {NUM_PATIENTS} patients...')
        existing = Patient.objects.count()
        if existing >= NUM_PATIENTS:
            self.stdout.write(f'    ⏭  {existing} exist — skipping.')
            return list(Patient.objects.all())

        needed = NUM_PATIENTS - existing
        users, pats = [], []
        for i in range(needed):
            first = random.choice(NAMES_F)
            last = random.choice(NAMES_L)
            idx = existing + i
            uname = f'pt_{first.lower()}_{last.lower()}_{idx}'
            email = f'{first.lower()}.{last.lower()}{idx}@email.com'
            users.append(User(username=uname, email=email, first_name=first, last_name=last, is_staff=False, is_active=True))
            pats.append(Patient(
                user=None, name=f'{first} {last}', email=email,
                phone=f'+91{random.randint(6000000000,9999999999)}',
                date_of_birth=fake.date_of_birth(minimum_age=3, maximum_age=85),
                gender=random.choice(GENDERS), blood_group=random.choice(BLOODS),
                address=fake.address().replace('\n',', ')[:200],
                emergency_contact=f'+91{random.randint(6000000000,9999999999)}',
                medical_history=fake.text(max_nb_chars=100) if random.random() > 0.4 else '',
            ))

        self.stdout.write(f'    → Creating {len(users)} users...')
        User.objects.bulk_create(users, batch_size=BATCH)
        created = {u.username: u for u in User.objects.filter(username__startswith='pt_').order_by('-id')[:needed]}
        for u, p in zip(users, pats):
            p.user = created.get(u.username)
        Patient.objects.bulk_create(pats, batch_size=BATCH)
        self.stdout.write(f'    ✅ {len(pats)} patients created.')
        return list(Patient.objects.all())

    # ── Step 4: 50,000 Appointments ────────────────────────
    def _appts(self, doctors, patients):
        self.stdout.write(f'\n 📅 Step 4/5 — {NUM_APPOINTMENTS} appointments...')
        existing = Appointment.objects.count()
        if existing >= NUM_APPOINTMENTS:
            self.stdout.write(f'    ⏭  {existing} exist — skipping.')
            return

        needed = NUM_APPOINTMENTS - existing
        today = datetime.date.today()
        objs = []
        for _ in range(needed):
            d = today + datetime.timedelta(days=random.randint(-365, 180))
            h, m = random.randint(8, 17), random.choice([0, 15, 30, 45])
            objs.append(Appointment(
                patient=random.choice(patients), doctor=random.choice(doctors),
                date=d, time=datetime.time(h, m),
                status=random.choices(STATUSES, weights=STATUS_W, k=1)[0],
                reason=random.choice(SYMPTOMS),
                symptoms=fake.text(max_nb_chars=80) if random.random() > 0.35 else '',
            ))
        Appointment.objects.bulk_create(objs, batch_size=BATCH, ignore_conflicts=True)
        created = Appointment.objects.count() - existing
        self.stdout.write(f'    ✅ {created} appointments created.')

    # ── Step 5: Realistic Reviews for Completed Appointments ─
    def _reviews(self):
        self.stdout.write('\n ⭐ Step 5/5 — Generating reviews for completed appointments...')
        existing_reviews = Review.objects.count()
        if existing_reviews > 0:
            self.stdout.write(f'    ⏭  {existing_reviews} reviews exist — skipping.')
            return

        completed = list(Appointment.objects.filter(status='Completed').select_related('patient', 'doctor'))
        if not completed:
            self.stdout.write('    ⏭  No completed appointments found.')
            return

        # Pick 60% of completed appointments for reviews
        review_count = int(len(completed) * REVIEW_RATE)
        to_review = random.sample(completed, review_count)

        reviews = []
        for appt in to_review:
            # Weighted rating: most reviews are 4-5 stars, some 3, few 1-2
            rating = random.choices([1, 2, 3, 4, 5], weights=[3, 5, 15, 35, 42], k=1)[0]
            comment = random.choice(REVIEW_COMMENTS)
            if rating <= 2:
                comment = random.choice([
                    "Not satisfied with the consultation.",
                    "Had to wait too long, doctor seemed rushed.",
                    "Expected better service for the fee paid.",
                    "Doctor didn\'t listen properly to my concerns.",
                ])
            reviews.append(Review(
                appointment=appt,
                patient=appt.patient,
                doctor=appt.doctor,
                rating=rating,
                comment=comment,
            ))

        Review.objects.bulk_create(reviews, batch_size=BATCH, ignore_conflicts=True)
        self.stdout.write(f'    ✅ {len(reviews)} reviews generated ({REVIEW_RATE*100:.0f}% of {len(completed)} completed appointments).')

        # Recalculate doctor ratings
        self.stdout.write('    📊 Recalculating doctor ratings...')
        from django.db.models import Avg
        for doc in Doctor.objects.all():
            avg = Review.objects.filter(doctor=doc).aggregate(a=Avg('rating'))['a']
            if avg:
                doc.rating = round(avg, 2)
                doc.save(update_fields=['rating'])
        self.stdout.write('    ✅ Doctor ratings updated.')
