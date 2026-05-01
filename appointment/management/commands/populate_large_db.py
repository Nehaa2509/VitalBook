"""
Django management command to populate the VitalBook database with real-scale data:
  - 500 Doctors
  - 10,000 Patients
  - 50,000 Appointments

Uses Faker (Indian locale) and bulk_create() for efficient insertion.

Usage:
    pip install Faker
    python manage.py populate_large_db
"""

import random
import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from faker import Faker

from appointment.models import Specialization, Doctor, Patient, Appointment

fake = Faker('en_IN')


class Command(BaseCommand):
    help = 'Populate database with 500 Doctors, 10,000 Patients, and 50,000 Appointments'

    # ── Config ──────────────────────────────────────────────────────────────
    NUM_DOCTORS = 500
    NUM_PATIENTS = 10000
    NUM_APPOINTMENTS = 50000
    BATCH_SIZE = 1000  # bulk_create chunk size

    # Realistic Indian specializations
    SPECIALIZATIONS = [
        ('Cardiology', 'Heart & cardiovascular diseases', 'fa-heartbeat'),
        ('Dermatology', 'Skin, hair & nail disorders', 'fa-allergies'),
        ('Neurology', 'Brain & nervous system disorders', 'fa-brain'),
        ('Orthopedics', 'Bones, joints & muscles', 'fa-bone'),
        ('Pediatrics', 'Child healthcare', 'fa-baby'),
        ('General Medicine', 'Primary healthcare & diagnosis', 'fa-stethoscope'),
        ('Gynecology', 'Women\'s reproductive health', 'fa-female'),
        ('ENT', 'Ear, Nose & Throat specialist', 'fa-ear-listen'),
        ('Ophthalmology', 'Eye care & vision', 'fa-eye'),
        ('Psychiatry', 'Mental health & behavioural disorders', 'fa-head-side-virus'),
        ('Endocrinology', 'Hormonal & metabolic disorders', 'fa-dna'),
        ('Gastroenterology', 'Digestive system disorders', 'fa-stomach'),
        ('Pulmonology', 'Lung & respiratory disorders', 'fa-lungs'),
        ('Urology', 'Urinary & male reproductive system', 'fa-kidneys'),
        ('Rheumatology', 'Joint & autoimmune disorders', 'fa-hand-holding-medical'),
    ]

    INDIAN_FIRST_NAMES = fake.first_names()
    INDIAN_LAST_NAMES = [
        'Sharma', 'Verma', 'Gupta', 'Singh', 'Kumar', 'Patel', 'Shah', 'Joshi',
        'Mehta', 'Reddy', 'Nair', 'Iyer', 'Menon', 'Pillai', 'Das', 'Chatterjee',
        'Mukherjee', 'Banerjee', 'Bose', 'Sarkar', 'Dutta', 'Ghosh', 'Roy',
        'Sen', 'Mishra', 'Dubey', 'Pandey', 'Tiwari', 'Pathak', 'Trivedi',
        'Bhatt', 'Thakur', 'Chauhan', 'Rathore', 'Jain', 'Agarwal', 'Agarwala',
        'Kapoor', 'Malhotra', 'Khanna', 'Arora', 'Sethi', 'Chopra', 'Anand',
        'Chandra', 'Sinha', 'Kulkarni', 'Deshpande', 'Rao', 'Hegde', 'Gowda',
    ]

    QUALIFICATIONS = [
        'MBBS', 'MBBS, MD', 'MBBS, MS', 'MBBS, DNB', 'MBBS, MD, DM',
        'MBBS, MS, MCh', 'MBBS, MD (Internal Medicine)',
        'MBBS, MD (Pediatrics)', 'MBBS, MD (Dermatology)',
        'MBBS, MS (Orthopedics)', 'MBBS, MD (Psychiatry)',
        'MBBS, MS (ENT)', 'MBBS, MS (Ophthalmology)',
    ]

    DAYS_OPTIONS = ['Mon-Fri', 'Mon-Sat', 'Mon-Fri', 'Tue-Sat', 'Mon-Thu', 'Mon-Wed,Fri']
    TIME_OPTIONS = ['9:00 AM - 1:00 PM', '2:00 PM - 6:00 PM', '10:00 AM - 4:00 PM',
                    '9:00 AM - 2:00 PM', '3:00 PM - 7:00 PM', '10:00 AM - 2:00 PM']
    FEE_OPTIONS = [300, 400, 500, 600, 700, 800, 1000, 1200, 1500, 2000]
    BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    GENDERS = ['Male', 'Female', 'Other']
    APPOINTMENT_STATUSES = ['Pending', 'Confirmed', 'Completed', 'Cancelled']
    STATUS_WEIGHTS = [15, 40, 35, 10]  # percentage weights

    COMMON_SYMPTOMS = [
        'Fever and cold', 'Headache and body ache', 'Stomach pain',
        'Skin rash', 'Joint pain', 'Breathing difficulty',
        'Chest pain', 'Back pain', 'Dizziness', 'Fatigue',
        'Cough and sore throat', 'Allergic reaction', 'Eye irritation',
        'Ear pain', 'Dental pain', 'Urinary issues',
    ]

    # ──────────────────────────────────────────────────────────────────────────
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting large-scale database population...'))
        self.stdout.write(f'   Doctors:     {self.NUM_DOCTORS}')
        self.stdout.write(f'   Patients:    {self.NUM_PATIENTS}')
        self.stdout.write(f'   Appointments:{self.NUM_APPOINTMENTS}')
        self.stdout.write('')

        # Step 1: Specializations
        self._create_specializations()

        # Step 2: Users + Doctors
        self._create_doctors()

        # Step 3: Users + Patients
        self._create_patients()

        # Step 4: Appointments
        self._create_appointments()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅ Done! Database populated successfully.'))

    # ── Step 1: Specializations ─────────────────────────────────────────────
    def _create_specializations(self):
        specs = Specialization.objects.all()
        if specs.count() >= len(self.SPECIALIZATIONS):
            self.stdout.write(self.style.WARNING('⏭  Specializations already exist. Skipping.'))
            return
        self.stdout.write('📋 Creating specializations...')
        objs = [Specialization(name=n, description=d, icon=i) for n, d, i in self.SPECIALIZATIONS]
        Specialization.objects.bulk_create(objs, batch_size=50)
        self.stdout.write(self.style.SUCCESS(f'   ✅ {len(objs)} specializations created.'))

    # ── Step 2: Doctors ─────────────────────────────────────────────────────
    def _create_doctors(self):
        self.stdout.write(f'👨‍⚕️ Creating {self.NUM_DOCTORS} doctors...')
        specs = list(Specialization.objects.all())
        if not specs:
            self.stdout.write(self.style.ERROR('❌ No specializations found!'))
            return

        # Check how many already exist
        existing = Doctor.objects.count()
        if existing >= self.NUM_DOCTORS:
            self.stdout.write(self.style.WARNING(f'⏭  {existing} doctors already exist. Skipping.'))
            return
        needed = self.NUM_DOCTORS - existing
        start_idx = existing

        users_to_create = []
        doctors_to_create = []
        used_emails = set()

        for i in range(needed):
            idx = start_idx + i
            first = random.choice(self.INDIAN_FIRST_NAMES)
            last = random.choice(self.INDIAN_LAST_NAMES)
            username = f'dr_{first.lower()}_{last.lower()}_{idx}'
            email = f'{first.lower()}.{last.lower()}@hospital.in'
            # Ensure unique email
            base_email = email
            counter = 1
            while email in used_emails:
                email = f'{first.lower()}.{last.lower()}{counter}@hospital.in'
                counter += 1
            used_emails.add(email)

            users_to_create.append(User(
                username=username,
                email=email,
                first_name=first,
                last_name=last,
                is_staff=False,
                is_active=True,
            ))
        self.stdout.write(f'   Creating {len(users_to_create)} User objects for doctors...')
        # Use bulk_create for users
        User.objects.bulk_create(users_to_create, batch_size=self.BATCH_SIZE)

        # Refresh to get IDs
        created_users = {u.username: u for u in User.objects.filter(
            username__startswith='dr_').order_by('-id')[:needed]}

        for i in range(needed):
            idx = start_idx + i
            username = f'dr_{random.choice(self.INDIAN_FIRST_NAMES).lower()}_{random.choice(self.INDIAN_LAST_NAMES).lower()}_{idx}'
            user = created_users.get(username)
            if not user:
                # fallback: grab any unlinked user
                user = User.objects.filter(username__startswith='dr_').exclude(
                    doctor_profile__isnull=False).first()

            spec = random.choice(specs)
            doctors_to_create.append(Doctor(
                user=user,
                name=f'Dr. {random.choice(self.INDIAN_FIRST_NAMES)} {random.choice(self.INDIAN_LAST_NAMES)}',
                specialization=spec,
                qualification=random.choice(self.QUALIFICATIONS),
                experience_years=random.randint(1, 35),
                available_days=random.choice(self.DAYS_OPTIONS),
                available_time=random.choice(self.TIME_OPTIONS),
                consultation_fee=random.choice(self.FEE_OPTIONS),
                email=user.email,
                phone=fake.phone_number(),
                bio=fake.text(max_nb_chars=200),
                image='default-doctor.jpg',
                is_available=random.choice([True, True, True, False]),
                rating=round(random.uniform(2.5, 5.0), 2),
            ))

        Doctor.objects.bulk_create(doctors_to_create, batch_size=self.BATCH_SIZE)
        self.stdout.write(self.style.SUCCESS(f'   ✅ {len(doctors_to_create)} doctors created.'))

    # ── Step 3: Patients ────────────────────────────────────────────────────
    def _create_patients(self):
        self.stdout.write(f'👥 Creating {self.NUM_PATIENTS} patients...')
        existing = Patient.objects.count()
        if existing >= self.NUM_PATIENTS:
            self.stdout.write(self.style.WARNING(f'⏭  {existing} patients already exist. Skipping.'))
            return
        needed = self.NUM_PATIENTS - existing
        start_idx = existing

        users_to_create = []
        patients_to_create = []
        used_emails = set()

        for i in range(needed):
            idx = start_idx + i
            first = random.choice(self.INDIAN_FIRST_NAMES)
            last = random.choice(self.INDIAN_LAST_NAMES)
            username = f'pt_{first.lower()}_{last.lower()}_{idx}'
            email = f'{first.lower()}.{last.lower()}{idx}@email.com'
            base = email
            c = 1
            while email in used_emails:
                email = f'{first.lower()}.{last.lower()}{idx}_{c}@email.com'
                c += 1
            used_emails.add(email)

            users_to_create.append(User(
                username=username,
                email=email,
                first_name=first,
                last_name=last,
                is_staff=False,
                is_active=True,
            ))

        self.stdout.write(f'   Creating {len(users_to_create)} User objects for patients...')
        User.objects.bulk_create(users_to_create, batch_size=self.BATCH_SIZE)

        created_users = {u.username: u for u in User.objects.filter(
            username__startswith='pt_').order_by('-id')[:needed]}

        for i in range(needed):
            idx = start_idx + i
            username = f'pt_{random.choice(self.INDIAN_FIRST_NAMES).lower()}_{random.choice(self.INDIAN_LAST_NAMES).lower()}_{idx}'
            user = created_users.get(username)
            if not user:
                user = User.objects.filter(username__startswith='pt_').exclude(
                    patient__isnull=False).first()

            patients_to_create.append(Patient(
                user=user,
                name=f'{random.choice(self.INDIAN_FIRST_NAMES)} {random.choice(self.INDIAN_LAST_NAMES)}',
                email=user.email,
                phone=fake.phone_number(),
                date_of_birth=fake.date_of_birth(minimum_age=5, maximum_age=80),
                gender=random.choice(self.GENDERS),
                blood_group=random.choice(self.BLOOD_GROUPS),
                address=fake.address().replace('\n', ', ')[:200],
                emergency_contact=fake.phone_number(),
                medical_history=fake.text(max_nb_chars=150) if random.random() > 0.5 else '',
            ))

        Patient.objects.bulk_create(patients_to_create, batch_size=self.BATCH_SIZE)
        self.stdout.write(self.style.SUCCESS(f'   ✅ {len(patients_to_create)} patients created.'))

    # ── Step 4: Appointments ────────────────────────────────────────────────
    def _create_appointments(self):
        self.stdout.write(f'📅 Creating {self.NUM_APPOINTMENTS} appointments...')
        existing = Appointment.objects.count()
        if existing >= self.NUM_APPOINTMENTS:
            self.stdout.write(self.style.WARNING(f'⏭  {existing} appointments already exist. Skipping.'))
            return
        needed = self.NUM_APPOINTMENTS - existing

        doctors = list(Doctor.objects.all())
        patients = list(Patient.objects.all())
        if not doctors or not patients:
            self.stdout.write(self.style.ERROR('❌ Need doctors and patients first!'))
            return

        today = datetime.date.today()
        appts = []

        for _ in range(needed):
            doctor = random.choice(doctors)
            patient = random.choice(patients)
            # Random date within last 180 days or next 90 days
            day_offset = random.randint(-180, 90)
            appt_date = today + datetime.timedelta(days=day_offset)
            # Random time in 30-min slots
            hour = random.randint(9, 17)
            minute = random.choice([0, 30])
            appt_time = datetime.time(hour, minute)
            status = random.choices(self.APPOINTMENT_STATUSES, weights=self.STATUS_WEIGHTS, k=1)[0]

            appts.append(Appointment(
                patient=patient,
                doctor=doctor,
                date=appt_date,
                time=appt_time,
                status=status,
                reason=random.choice(self.COMMON_SYMPTOMS),
                symptoms=fake.text(max_nb_chars=100) if random.random() > 0.4 else '',
                notes='',
                prescription='',
            ))

        Appointment.objects.bulk_create(appts, batch_size=self.BATCH_SIZE)
        self.stdout.write(self.style.SUCCESS(f'   ✅ {len(appts)} appointments created.'))
