from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator, FileExtensionValidator
from django.utils import timezone
from datetime import timedelta


def get_default_expiration():
    """Returns a datetime 10 minutes from now — used as default for OTP expiry."""
    return timezone.now() + timedelta(minutes=10)




class Specialization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fa-stethoscope')
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='doctor_profile')
    name = models.CharField(max_length=100)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)
    qualification = models.CharField(max_length=200)
    designation = models.CharField(max_length=100, default='Resident Medical Officer',
                                   help_text="e.g., Head of Department, Senior Consultant, etc.")
    experience_years = models.IntegerField(validators=[MinValueValidator(0)])
    available_days = models.CharField(max_length=100, help_text="e.g., Mon-Fri")
    available_time = models.CharField(max_length=100, help_text="e.g., 9:00 AM - 5:00 PM")
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    bio = models.TextField(blank=True)
    image = models.CharField(max_length=200, blank=True, default='default-doctor.jpg')
    is_available = models.BooleanField(default=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, 
                                 validators=[MinValueValidator(0), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.specialization}"
    
    def get_appointment_count(self):
        return self.appointment_set.count()

    @property
    def initials(self):
        parts = self.name.split()
        if len(parts) >= 2:
            return f"{parts[0][0]}{parts[-1][0]}".upper()
        elif parts:
            return parts[0][:2].upper()
        return "DR"

    @property
    def experience_level(self):
        years = self.experience_years or 0
        if years <= 9:
            return 'Junior Resident'
        elif years <= 19:
            return 'Consultant'
        else:
            return 'Senior Consultant / HOD'

    @property
    def experience_badge_color(self):
        years = self.experience_years or 0
        if years <= 9:
            return '#22c55e'  # Green for Junior
        elif years <= 19:
            return '#0d6efd'  # Blue for Consultant
        else:
            return '#f97316'  # Orange for Senior

    @property
    def dynamic_available_days(self):
        avails = self.availability.all().order_by('day')
        if not avails.exists():
            return self.available_days or "Not Available"
        
        day_names = [dict(Availability.DAYS_OF_WEEK).get(a.day)[:3] for a in avails]
        if len(day_names) == 7:
            return "Mon - Sun"
        return ", ".join(day_names)

    @property
    def dynamic_available_time(self):
        avails = self.availability.all().order_by('day')
        if not avails.exists():
            return self.available_time or "Not Available"
        
        # Taking the first day's time for simplicity
        first = avails.first()
        return f"{first.start_time.strftime('%I:%M %p')} - {first.end_time.strftime('%I:%M %p')}"

    @property
    def is_currently_available(self):
        from django.utils import timezone
        now = timezone.localtime(timezone.now())
        current_day = now.weekday() # 0 for Monday, 2 for Wednesday, etc.
        current_time = now.time()

        # Check if there is an availability record for TODAY and NOW
        active_shift = self.availability.filter(
            day=current_day,
            start_time__lte=current_time,
            end_time__gte=current_time
        ).exists()

        return active_shift

    class Meta:
        ordering = ['experience_years', 'name']


class Availability(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'),
        (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday'),
    ]
    
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='availability')
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor.name} - {self.get_day_display()} ({self.start_time.strftime('%I:%M %p')} to {self.end_time.strftime('%I:%M %p')})"

    class Meta:
        unique_together = ('doctor', 'day') # Prevents duplicate day entries for one doctor
        ordering = ['day']


class Patient(models.Model):
    # Proof-of-Possession: reject junk numbers before we spend Twilio credits
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be in the format: '+999999999'. Up to 15 digits allowed."
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(validators=[phone_regex], max_length=17)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')], blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    medical_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    def get_age(self):
        if self.date_of_birth:
            today = timezone.now().date()
            return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None

    @property
    def age(self):
        """Template-friendly alias for get_age()."""
        return self.get_age()


class Appointment(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    reason = models.TextField(blank=True)
    symptoms = models.TextField(blank=True)
    notes = models.TextField(blank=True, help_text="Doctor's notes")
    prescription = models.TextField(blank=True)
    cancellation_fee_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.patient.name} - {self.doctor.name} on {self.date}"
    
    def is_upcoming(self):
        appointment_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return appointment_datetime > timezone.now() and self.status in ['Pending', 'Confirmed']

    def can_cancel_free(self):
        """Returns True if the appointment is more than 24 hours away (free cancellation window)."""
        appt_datetime = timezone.make_aware(
            timezone.datetime.combine(self.date, self.time)
        )
        return (appt_datetime - timezone.now()).total_seconds() > 24 * 3600

    @property
    def has_completed_payment(self):
        """Returns True if this appointment has a completed payment."""
        return self.payments.filter(payment_status='Completed').exists()

    last_reminder_hour = models.IntegerField(
        default=-1,
        help_text="Tracks the last hour (0-23) a reminder email was sent. -1 means never sent."
    )

    class Meta:
        ordering = ['-date', '-time']
        unique_together = ['doctor', 'date', 'time']


class Billing(models.Model):
    BILLING_TYPE_CHOICES = [
        ('Consultation', 'Consultation'),
        ('Cancellation Fee', 'Cancellation Fee'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='billings')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    billing_type = models.CharField(max_length=50, choices=BILLING_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.billing_type} - ₹{self.total_amount} for {self.appointment}"

    class Meta:
        ordering = ['-created_at']


class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('UPI', 'UPI'),
        ('Card', 'Debit/Credit Card'),
        ('NetBanking', 'Net Banking'),
        ('Wallet', 'Wallet'),
        ('Razorpay', 'Razorpay'),
    ]
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True)
    # Razorpay-specific fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, default='')
    razorpay_payment_id = models.CharField(max_length=100, blank=True, default='')
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment #{self.transaction_id} - ₹{self.amount} ({self.payment_status})"
    
    class Meta:
        ordering = ['-created_at']


class Prescription(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='prescription_record')
    medicines = models.TextField(help_text="Format: Medicine Name - Dosage - Duration")
    instructions = models.TextField(blank=True)
    issued_on = models.DateTimeField(auto_now_add=True)

    def clean(self):
        """Enforce that prescriptions are only issued for Completed, paid appointments."""
        if not self.appointment_id:
            return
        appt = self.appointment
        if appt.status != 'Completed':
            raise ValidationError({
                'appointment': (
                    f"Prescriptions can only be issued for Completed appointments. "
                    f"This appointment is currently '{appt.status}'."
                )
            })
        has_paid = appt.payments.filter(payment_status='Completed').exists()
        if not has_paid:
            raise ValidationError({
                'appointment': (
                    "Prescriptions can only be issued after a completed payment has been recorded "
                    "for this appointment."
                )
            })

    def save(self, *args, **kwargs):
        """Run full validation (including clean()) before saving."""
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Prescription for {self.appointment.patient.name} by {self.appointment.doctor.name}"

    class Meta:
        ordering = ['-issued_on']


class Review(models.Model):
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews', null=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='reviews', null=True)
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        patient_name = self.patient.name if self.patient else self.appointment.patient.name
        doctor_name = self.doctor.name if self.doctor else self.appointment.doctor.name
        return f"Review by {patient_name} for {doctor_name} - {self.rating}★"
    
    def save(self, *args, **kwargs):
        # Auto-populate doctor and patient from appointment if not set
        if not self.doctor:
            self.doctor = self.appointment.doctor
        if not self.patient:
            self.patient = self.appointment.patient
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('appointment', 'patient')


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
    
    class Meta:
        ordering = ['-created_at']


class MedicalRecord(models.Model):
    """Stores uploaded PDF medical reports for a patient."""
    patient     = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='medical_records')
    report_name = models.CharField(max_length=200, help_text="e.g. Blood Test, MRI Scan")
    pdf_file    = models.FileField(
        upload_to='medical_reports/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Upload a PDF file only."
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient.name} — {self.report_name}"

    class Meta:
        ordering = ['-uploaded_at']


import random

class OTPVerification(models.Model):
    OTP_TYPE_CHOICES = [
        ('email', 'Email'),
        ('mobile', 'Mobile'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_verifications')
    otp = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=10, choices=OTP_TYPE_CHOICES, default='email')
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=get_default_expiration)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        # Automatically set expiry to 10 minutes from now if not provided
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.expires_at = timezone.now() + timedelta(minutes=10)
        self.save()
        return self.otp
    
    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp_type} - {'Verified' if self.is_verified else 'Pending'}"
    
    class Meta:
        ordering = ['-created_at']
