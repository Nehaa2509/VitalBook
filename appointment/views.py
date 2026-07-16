import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings as django_settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from .models import Doctor, Patient, Appointment, Specialization, Review, ContactMessage, Billing, Prescription, Payment, OTPVerification, MedicalRecord
from .forms import AppointmentForm
from django.contrib.auth.models import User
from . import email_utils
from . import otp_utils
from .decorators import patient_required
from .upi_utils import create_upi_order, verify_upi_payment, create_cashfree_cancellation_order
import json
import qrcode
import io
import os
import uuid
import threading
import pytz
from django.core.files.base import ContentFile
from .reminder_scheduler import schedule_same_day_reminders, send_final_one_hour_reminder



def generate_qr_code(appointment):
    """Generate a QR code for appointment check-in containing appointment details."""
    qr_data = (
        f"VITALBOOK\n"
        f"Appointment ID: {appointment.id}\n"
        f"Patient: {appointment.patient.name}\n"
        f"Doctor: Dr. {appointment.doctor.name}\n"
        f"Date: {appointment.date.strftime('%d/%m/%Y')}\n"
        f"Time: {appointment.time.strftime('%I:%M %p')}"
    )
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0B3B60", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    filename = f'qr_appointment_{appointment.id}.png'
    appointment.qr_code.save(filename, ContentFile(buffer.read()), save=True)


def send_booking_email(appointment):
    """Send a confirmation email to the patient after booking."""
    try:
        subject = f'VITALBOOK - Appointment Confirmation (#{appointment.id})'
        message = (
            f"Dear {appointment.patient.name},\n\n"
            f"Your appointment has been booked successfully!\n\n"
            f"Details:\n"
            f"  Doctor: Dr. {appointment.doctor.name} ({appointment.doctor.specialization.name})\n"
            f"  Date: {appointment.date.strftime('%d/%m/%Y')}\n"
            f"  Time: {appointment.time.strftime('%I:%M %p')}\n"
            f"  Consultation Fee: ₹{appointment.doctor.consultation_fee}\n\n"
            f"Please arrive 15 minutes before your scheduled time.\n"
            f"You can use the QR code in your dashboard for quick check-in.\n\n"
            f"Cancellation Policy: Free cancellation within 24 hours of booking. "
            f"A ₹500 cancellation fee applies after 24 hours.\n\n"
            f"Thank you for choosing VITALBOOK.\n"
            f"📞 +91 98765 43210\n"
        )
        send_mail(
            subject,
            message,
            django_settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.email],
            fail_silently=True,
        )
    except Exception:
        pass  # Silently fail - email is a nice-to-have, not critical


def home(request):
    specializations = Specialization.objects.all()[:6]
    top_doctors = Doctor.objects.filter(is_available=True).order_by('-rating')[:3]
    total_doctors = Doctor.objects.filter(is_available=True).count()
    total_patients = Patient.objects.count()
    total_appointments = Appointment.objects.count()
    
    context = {
        'specializations': specializations,
        'top_doctors': top_doctors,
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
    }
    return render(request, 'appointment/home.html', context)


def about(request):
    return render(request, 'appointment/about.html')


def services(request):
    specializations = Specialization.objects.all()
    return render(request, 'appointment/services.html', {'specializations': specializations})


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'appointment/contact.html')


def doctor_list(request):
    # ── 1. Base Queryset ─────────────────────────────────────────────────
    doctors = Doctor.objects.select_related('specialization').annotate(
        avg_rating=Avg('reviews__rating'),
        total_reviews=Count('reviews')
    )

    # ── 2. Capture GET Parameters ────────────────────────────────────────
    search_q          = request.GET.get('search', '').strip()
    specialization    = request.GET.get('specialization', '').strip()
    min_fee           = request.GET.get('min_fee', '').strip()
    max_fee           = request.GET.get('max_fee', '').strip()
    min_rating        = request.GET.get('min_rating', '').strip()
    min_exp           = request.GET.get('min_exp', '').strip()
    availability      = request.GET.get('availability', '').strip()

    # ── 3. Apply Dynamic Filters ─────────────────────────────────────────
    if search_q:
        doctors = doctors.filter(
            Q(name__icontains=search_q) |
            Q(specialization__name__icontains=search_q) |
            Q(qualification__icontains=search_q) |
            Q(bio__icontains=search_q)
        )

    if specialization and specialization != 'All Specializations':
        doctors = doctors.filter(specialization__name=specialization)

    if min_fee:
        try:
            doctors = doctors.filter(consultation_fee__gte=float(min_fee))
        except ValueError:
            pass

    if max_fee:
        try:
            doctors = doctors.filter(consultation_fee__lte=float(max_fee))
        except ValueError:
            pass

    if min_rating:
        try:
            doctors = doctors.filter(rating__gte=float(min_rating))
        except ValueError:
            pass

    if min_exp:
        try:
            doctors = doctors.filter(experience_years__gte=int(min_exp))
        except ValueError:
            pass

    if availability:
        day_map = {
            'Mon': 0, 'Tue': 1, 'Wed': 2,
            'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6
        }
        if availability in day_map:
            mapped_day = day_map[availability]
            doctors = doctors.filter(
                Q(availability__day=mapped_day) | 
                Q(available_days__icontains=availability)
            ).distinct()

    # ── 4. Context Memory: pass all params back to template ──────────────
    specializations = Specialization.objects.all()

    context = {
        'doctors':             doctors,
        'specializations':     specializations,
        'total_results':       doctors.count(),
        # Selected filter values (for UI state persistence)
        'sel_search':          search_q,
        'sel_specialization':  specialization,
        'sel_min_fee':         min_fee,
        'sel_max_fee':         max_fee,
        'sel_min_rating':      min_rating,
        'sel_min_exp':         min_exp,
        'sel_availability':    availability,
    }
    return render(request, 'appointment/doctor_list.html', context)


def doctor_detail(request, doctor_id):
    doctor = get_object_or_404(Doctor, id=doctor_id)
    reviews = Review.objects.filter(doctor=doctor).select_related('patient')[:5]
    total_reviews = Review.objects.filter(doctor=doctor).count()
    avg_rating = doctor.rating
    
    context = {
        'doctor': doctor,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
    }
    return render(request, 'appointment/doctor_detail.html', context)


def register(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        date_of_birth = request.POST.get('date_of_birth', '')
        gender = request.POST.get('gender', '')
        blood_group = request.POST.get('blood_group', '')
        address = request.POST.get('address', '').strip()

        # Split name to support User model first/last name
        name_parts = name.split(maxsplit=1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Validations
        if not all([name, username, email, phone, password, confirm_password, gender, blood_group, address]):
            messages.error(request, 'All fields are required!')
            return render(request, 'appointment/register.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'appointment/register.html')

        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters!')
            return render(request, 'appointment/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken!')
            return render(request, 'appointment/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'appointment/register.html')

        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))

        # Store in session
        request.session['reg_otp'] = otp
        request.session['reg_email'] = email
        request.session['reg_username'] = username
        request.session['reg_password'] = password
        request.session['reg_first_name'] = first_name
        request.session['reg_last_name'] = last_name
        request.session['reg_name'] = name
        request.session['reg_phone'] = phone
        request.session['reg_date_of_birth'] = date_of_birth
        request.session['reg_gender'] = gender
        request.session['reg_blood_group'] = blood_group
        request.session['reg_address'] = address
        request.session['otp_created_at'] = str(timezone.now())

        # Send real email
        try:
            send_mail(
                subject='🔐 VitalBook — Your OTP Verification Code',
                message=f'''
Dear {first_name},

Your OTP verification code for VitalBook is:

{otp}

This code is valid for 10 minutes.
Do not share this code with anyone.

If you did not request this, please ignore this email.

Best regards,
Team VitalBook
                ''',
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
                html_message=f'''
<!DOCTYPE html>
<html>
<body style="font-family:Inter,Arial,sans-serif;background:#f4f6f9;padding:40px 0;margin:0;">
<div style="max-width:500px;margin:0 auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#0d6efd,#0056b3);padding:32px;text-align:center;">
        <div style="background:#f97316;width:48px;height:48px;border-radius:12px;margin:0 auto 12px;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:900;color:white;">+</div>
        <h1 style="color:white;margin:0;font-size:22px;font-weight:700;">VitalBook</h1>
        <p style="color:rgba(255,255,255,0.8);margin:6px 0 0;font-size:13px;">Your Health, Our Priority</p>
    </div>

    <!-- Body -->
    <div style="padding:36px 32px;text-align:center;">
        <h2 style="color:#0f172a;font-size:20px;margin:0 0 8px;">Verify Your Email</h2>
        <p style="color:#64748b;font-size:14px;margin:0 0 28px;">
            Hi <strong>{first_name}</strong>, use the code below to verify your account.
        </p>

        <!-- OTP Box -->
        <div style="background:#f0f7ff;border:2px dashed #0d6efd;border-radius:12px;padding:24px;margin:0 0 24px;">
            <p style="color:#64748b;font-size:12px;margin:0 0 8px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Your OTP Code</p>
            <div style="font-size:42px;font-weight:800;color:#0d6efd;letter-spacing:12px;font-family:monospace;">
                {otp}
            </div>
        </div>

        <p style="color:#94a3b8;font-size:13px;margin:0 0 6px;">
            ⏰ This code expires in <strong>10 minutes</strong>
        </p>
        <p style="color:#94a3b8;font-size:12px;margin:0;">
            🔒 Never share this code with anyone
        </p>
    </div>

    <!-- Footer -->
    <div style="background:#f8fafc;padding:20px;text-align:center;border-top:1px solid #e2e8f0;">
        <p style="color:#94a3b8;font-size:12px;margin:0;">
            © 2026 VitalBook. All rights reserved.<br>
            If you didn't create an account, ignore this email.
        </p>
    </div>

</div>
</body>
</html>
                '''
            )
            messages.success(request, f'OTP sent to {email}! Check your inbox.')
        except Exception as e:
            print(f'Email error: {e}')
            messages.warning(request, f'Could not send email. Please verify your SMTP settings.')

        return redirect('verify_otp')

    return render(request, 'appointment/register.html')


def user_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/admin/')
        elif hasattr(request.user, 'doctor_profile'):
            return redirect('doctor_dashboard')
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Smart Routing: Admin -> Admin Panel, Doctor -> Dashboard, Patient -> Home
            if user.is_staff or user.is_superuser:
                return redirect('/admin/')
            elif hasattr(user, 'doctor_profile'):
                return redirect('doctor_dashboard')
            else:
                next_url = request.POST.get('next') or request.GET.get('next') or 'home'
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')

    return render(request, 'appointment/login.html')


def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully!')
    return redirect('home')


@login_required
def profile(request):
    patient, _ = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
    )
    
    if request.method == 'POST':
        patient.name = request.POST.get('name')
        patient.phone = request.POST.get('phone')
        patient.gender = request.POST.get('gender')
        patient.blood_group = request.POST.get('blood_group')
        patient.address = request.POST.get('address')
        patient.emergency_contact = request.POST.get('emergency_contact')
        patient.medical_history = request.POST.get('medical_history')

        # Server-side DOB validation — safety net behind JS checks
        dob_str = request.POST.get('date_of_birth')
        if dob_str:
            try:
                import datetime as dt
                dob = dt.date.fromisoformat(dob_str)
                if dob > dt.date.today():
                    messages.error(request, 'Date of Birth cannot be a future date!')
                    return render(request, 'appointment/profile.html', {'patient': patient})
                if dob.year < 1900:
                    messages.error(request, 'Please enter a valid Date of Birth.')
                    return render(request, 'appointment/profile.html', {'patient': patient})
                patient.date_of_birth = dob
            except ValueError:
                messages.error(request, 'Invalid date format for Date of Birth.')
                return render(request, 'appointment/profile.html', {'patient': patient})
        else:
            patient.date_of_birth = None

        patient.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')

    return render(request, 'appointment/profile.html', {'patient': patient})


@login_required
@patient_required
def book_appointment(request, doctor_id):
    # ── GATEKEEPER: unverified users cannot book ──────────────────────────
    is_verified = OTPVerification.objects.filter(
        user=request.user, is_verified=True
    ).exists()
    if not is_verified:
        messages.error(
            request,
            '⚠️ You must verify your mobile/email OTP before booking an appointment. '
            'Please complete verification first.'
        )
        # Put the user back in session so verify_otp knows who they are
        request.session['user_id'] = request.user.id
        return redirect('verify_otp')

    doctor = get_object_or_404(Doctor, id=doctor_id)
    patient, _ = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
    )
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        form.instance.doctor = doctor

        if form.is_valid():
            try:
                appointment = form.save(commit=False)
                appointment.patient = patient
                appointment.status = 'Pending'
                appointment.save()
            except Exception:
                # Race condition: another user booked the same slot simultaneously
                messages.error(request, 'This time slot was just booked by someone else. Please choose another time.')
                return redirect('book_appointment', doctor_id=doctor_id)

            # Generate QR code for check-in
            try:
                generate_qr_code(appointment)
            except Exception:
                pass  # QR code generation is non-critical

            # Create a Billing record for the consultation fee
            Billing.objects.create(
                appointment=appointment,
                total_amount=doctor.consultation_fee,
                billing_type='Consultation',
                is_paid=False,
            )

            appointment.refresh_from_db()
            # Email handled by post_save signal OR manual send
            # Let's send booking confirmation manually if not relying on signals
            # from .email_utils import send_appointment_booked_email
            # send_appointment_booked_email(appointment)

            today = timezone.now().date()
            IST = pytz.timezone('Asia/Kolkata')
            now = datetime.now(IST)

            if appointment.date == today:
                # Calculate hours until appointment
                appt_datetime = IST.localize(
                    datetime.combine(appointment.date, appointment.time)
                )
                minutes_left = (appt_datetime - now).total_seconds() / 60

                if minutes_left > 60:
                    # More than 1 hour left — start hourly reminders
                    print(f'Starting hourly reminders for VB-{appointment.id}')

                    # Send first immediate reminder
                    hours_left = round(minutes_left / 60, 1)
                    from .email_utils import send_reminder_email
                    send_reminder_email(
                        appointment=appointment,
                        reminder_label=f'Booking Confirmed — {hours_left} Hours Until Appointment',
                        hours_left=hours_left,
                        is_final=False,
                    )

                    # Schedule hourly reminders in background
                    thread = threading.Thread(
                        target=schedule_same_day_reminders,
                        args=(appointment,),
                        daemon=True
                    )
                    thread.start()

                elif 0 < minutes_left <= 60:
                    # Less than 1 hour — send final reminder immediately
                    send_final_one_hour_reminder(appointment)

            messages.success(request, 'Appointment booked! Please complete the payment to confirm.')
            return redirect('checkout', appointment_id=appointment.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
            return redirect('book_appointment', doctor_id=doctor_id)
    
    # Get booked slots for this doctor
    today = timezone.now().date()
    booked_slots = Appointment.objects.filter(
        doctor=doctor,
        date__gte=today
    ).exclude(status='Cancelled').values_list('date', 'time')
    import json
    # Convert dates and times to strings for safe JSON serialization to frontend JS
    booked_slots_list = [[str(slot[0]), str(slot[1])] for slot in booked_slots]
    
    context = {
        'doctor': doctor,
        'booked_slots': json.dumps(booked_slots_list),
        'today': today.isoformat(),
    }
    return render(request, 'appointment/book_appointment.html', context)


@login_required
def my_appointments(request):
    # Redirect to patient dashboard upcoming section
    return redirect('/patient/dashboard/#upcoming-appointments')


@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Ensure patient can only view their own appointments
    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to view this appointment.')
        return redirect('my_appointments')
    
    # Check if review exists
    has_review = hasattr(appointment, 'review')

    # Get billing records
    billings = appointment.billings.all()

    # Get prescription if exists
    prescription_record = None
    try:
        prescription_record = appointment.prescription_record
    except Prescription.DoesNotExist:
        pass
    
    context = {
        'appointment': appointment,
        'has_review': has_review,
        'billings': billings,
        'prescription_record': prescription_record,
    }
    return render(request, 'appointment/appointment_detail.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Cancelled'
    appointment.save()
    messages.success(request, 'Appointment cancelled.')
    return redirect('my_appointments')


@login_required
def request_cancellation(request, appointment_id):
    """
    Handles appointment cancellation with 24-hour business policy.
    - Free cancellation if > 24 hours before appointment.
    - ₹200 Cashfree UPI penalty if < 24 hours before appointment.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Security check
    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to cancel this appointment.')
        return redirect('patient_dashboard')

    # Only Pending or Confirmed appointments can be cancelled
    if appointment.status not in ['Pending', 'Confirmed']:
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('patient_dashboard')

    # Combine date and time into a timezone-aware datetime object
    appt_datetime = timezone.make_aware(
        timezone.datetime.combine(appointment.date, appointment.time)
    )
    now = timezone.now()
    hours_until_appointment = (appt_datetime - now).total_seconds() / 3600

    # FREE Cancellation: more than 24 hours away
    if hours_until_appointment > 24:
        appointment.status = 'Cancelled'
        appointment.cancelled_at = timezone.now()
        appointment.save()
        messages.success(request, 'Appointment cancelled successfully (no fee applied).')
        return redirect('patient_dashboard')

    # PENALTY Cancellation: less than 24 hours — create a Cashfree order
    order_result = create_cashfree_cancellation_order(appointment)

    if not order_result['success']:
        messages.error(request, f'Could not connect to payment gateway: {order_result.get("error", "")}')
        return redirect('patient_dashboard')

    context = {
        'appointment':        appointment,
        'cancellation_fee':   200,
        'hours_remaining':    round(hours_until_appointment, 1),
        'order_id':           order_result['order_id'],
        'payment_session_id': order_result.get('payment_session_id', ''),
        'cashfree_env':       django_settings.CASHFREE_ENV,
    }
    return render(request, 'appointment/cancellation_checkout.html', context)


@login_required
def verify_cancellation_payment(request, appointment_id):
    """
    Cashfree return URL after the ₹200 cancellation fee is paid.
    Verifies the order status with Cashfree, then cancels the appointment.
    """
    order_id = request.GET.get('order_id', '')

    if not order_id:
        messages.error(request, 'Invalid payment verification request.')
        return redirect('patient_dashboard')

    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Security: only the appointment owner can verify
    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to perform this action.')
        return redirect('patient_dashboard')

    # Idempotency guard — never double-cancel
    if appointment.status == 'Cancelled':
        messages.info(request, 'This appointment has already been cancelled.')
        return redirect('patient_dashboard')

    # Ask Cashfree for the real payment status
    result = verify_upi_payment(order_id)

    if result['success']:
        # Cancel the appointment
        appointment.status = 'Cancelled'
        appointment.cancelled_at = timezone.now()
        appointment.cancellation_fee_applied = 200
        appointment.save()

        # Record the cancellation fee payment
        Payment.objects.create(
            appointment=appointment,
            amount=200,
            payment_status='Completed',
            payment_method='UPI',
            transaction_id=order_id,
            razorpay_order_id=order_id,
            razorpay_payment_id=order_id,
            payment_date=timezone.now(),
        )

        # Create billing record
        Billing.objects.create(
            appointment=appointment,
            total_amount=200,
            billing_type='Cancellation Fee',
            is_paid=True,
        )

        messages.success(request, 'Cancellation fee paid. Your appointment has been cancelled.')
    else:
        messages.error(
            request,
            f'Payment not verified (status: {result.get("status", "unknown")}). '
            'Please try again or contact support.'
        )

    return redirect('patient_dashboard')


@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to reschedule this appointment.')
        return redirect('my_appointments')
    
    if request.method == 'POST':
        new_date = request.POST['date']
        new_time = request.POST['time']
        
        # Check if new slot is available
        if Appointment.objects.filter(
            doctor=appointment.doctor,
            date=new_date,
            time=new_time
        ).exclude(id=appointment_id).exclude(status='Cancelled').exists():
            messages.error(request, 'This time slot is already booked. Please choose another time.')
            return redirect('reschedule_appointment', appointment_id=appointment_id)
        
        appointment.date = new_date
        appointment.time = new_time
        appointment.status = 'Pending'
        appointment.save()
        
        messages.success(request, 'Appointment rescheduled successfully!')
        return redirect('my_appointments')
    
    context = {
        'appointment': appointment,
        'today': timezone.now().date().isoformat(),
    }
    return render(request, 'appointment/reschedule_appointment.html', context)


@login_required
def add_review(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to review this appointment.')
        return redirect('my_appointments')
    
    if appointment.status != 'Completed':
        messages.error(request, 'You can only review completed appointments.')
        return redirect('my_appointments')
    
    if hasattr(appointment, 'review'):
        messages.error(request, 'You have already reviewed this appointment.')
        return redirect('my_appointments')
    
    if request.method == 'POST':
        rating = int(request.POST['rating'])
        comment = request.POST.get('comment', '')
        
        # Create review
        Review.objects.create(
            appointment=appointment,
            doctor=appointment.doctor,
            patient=appointment.patient,
            rating=rating,
            comment=comment
        )
        
        # Update doctor's average rating
        doctor = appointment.doctor
        reviews = Review.objects.filter(doctor=doctor)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        doctor.rating = round(avg_rating, 2) if avg_rating else 0
        doctor.save()
        
        messages.success(request, 'Thank you for your review!')
        return redirect('my_appointments')
    
    context = {'appointment': appointment}
    return render(request, 'appointment/add_review.html', context)


@login_required
def submit_review(request, appointment_id):
    """AJAX endpoint to submit review."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    try:
        import json
        data = json.loads(request.body)
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not rating or not (1 <= int(rating) <= 5):
            return JsonResponse({'status': 'error', 'message': 'Invalid rating'}, status=400)
        
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Permission check
        if appointment.patient.user != request.user:
            return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
        
        # Status check
        if appointment.status != 'Completed':
            return JsonResponse({'status': 'error', 'message': 'Can only review completed appointments'}, status=400)
        
        # Duplicate check
        if hasattr(appointment, 'review'):
            return JsonResponse({'status': 'error', 'message': 'Already reviewed'}, status=400)
        
        # Create review
        review = Review.objects.create(
            appointment=appointment,
            doctor=appointment.doctor,
            patient=appointment.patient,
            rating=int(rating),
            comment=comment
        )
        
        # Update doctor's average rating
        doctor = appointment.doctor
        reviews = Review.objects.filter(doctor=doctor)
        avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
        doctor.rating = round(avg_rating, 2) if avg_rating else 0
        doctor.save()
        
        # Send thank you email
        email_utils.send_review_thankyou(review)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Review submitted successfully',
            'new_rating': float(doctor.rating),
            'review_count': reviews.count()
        })
        
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def doctor_reviews(request, doctor_id):
    """Display all reviews for a doctor."""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    reviews = Review.objects.filter(doctor=doctor).select_related('patient', 'appointment')
    
    # Calculate rating distribution
    total_reviews = reviews.count()
    rating_distribution = {
        5: reviews.filter(rating=5).count(),
        4: reviews.filter(rating=4).count(),
        3: reviews.filter(rating=3).count(),
        2: reviews.filter(rating=2).count(),
        1: reviews.filter(rating=1).count(),
    }
    
    # Calculate percentages
    rating_percentages = {}
    for rating, count in rating_distribution.items():
        rating_percentages[rating] = (count / total_reviews * 100) if total_reviews > 0 else 0
    
    context = {
        'doctor': doctor,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'rating_distribution': rating_distribution,
        'rating_percentages': rating_percentages,
        'avg_rating': doctor.rating,
    }
    
    return render(request, 'appointment/doctor_reviews.html', context)


def search_doctors(request):
    query = request.GET.get('q', '')
    doctors = Doctor.objects.filter(is_available=True)
    
    if query:
        doctors = doctors.filter(
            Q(name__icontains=query) |
            Q(specialization__name__icontains=query) |
            Q(qualification__icontains=query)
        )
    
    context = {
        'doctors': doctors,
        'query': query,
    }
    return render(request, 'appointment/search_results.html', context)



@login_required
def checkout(request, appointment_id):
    """Display Cashfree UPI checkout page — creates a Cashfree payment order."""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Security: patients can only checkout their own appointments
    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('my_appointments')

    # If already fully paid, skip checkout
    if appointment.payments.filter(payment_status='Completed').exists():
        messages.info(request, 'This appointment has already been paid for.')
        return redirect('appointment_detail', appointment_id=appointment_id)

    if request.method == 'POST':
        return redirect('payment_receipt', appointment_id=appointment.id)

    doctor = appointment.doctor

    # Create a Cashfree UPI order
    order_result = create_upi_order(appointment)

    if not order_result['success']:
        messages.error(request, 'Payment setup failed. Please try again.')
        return redirect('my_appointments')

    context = {
        'appointment':         appointment,
        'doctor':              doctor,
        'order_id':            order_result['order_id'],
        'payment_session_id':  order_result.get('payment_session_id', ''),
        'amount':              float(doctor.consultation_fee),
        'cashfree_env':        django_settings.CASHFREE_ENV,
    }
    return render(request, 'appointment/checkout.html', context)


@login_required
def process_payment(request):
    """Legacy AJAX payment endpoint — kept for backward compatibility."""
    if request.method == 'GET':
        # Handle GET gracefully without blocking to avoid 405s
        return JsonResponse({'status': 'info', 'message': 'Payment endpoint ready for POST'}, status=200)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            appointment_id = data.get('appointment_id')
            payment_method = data.get('payment_method')

            if not appointment_id or not payment_method:
                return JsonResponse({'status': 'error', 'message': 'Missing required fields'}, status=400)

            appointment = get_object_or_404(Appointment, id=appointment_id)

            if appointment.patient.user != request.user:
                return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)

            booking_id = f"VB-{uuid.uuid4().hex[:8].upper()}"

            payment = Payment.objects.create(
                appointment=appointment,
                amount=appointment.doctor.consultation_fee,
                payment_status='Completed',
                payment_method=payment_method,
                transaction_id=booking_id,
                payment_date=timezone.now(),
            )

            billing = appointment.billings.filter(billing_type='Consultation').first()
            if billing:
                billing.is_paid = True
                billing.save()

            email_utils.send_payment_receipt(appointment, payment)

            return JsonResponse({
                'status': 'success',
                'booking_id': booking_id,
                'doctor_name': appointment.doctor.name,
                'appointment_date': appointment.date.strftime('%d %b, %Y'),
                'appointment_time': appointment.time.strftime('%I:%M %p'),
                'amount': str(appointment.doctor.consultation_fee),
                'payment_method': payment_method,
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Unsupported method'}, status=400)


@csrf_exempt
def verify_payment(request):
    """Cashfree return URL — verifies UPI payment status and records the transaction."""
    order_id       = request.GET.get('order_id', '')
    appointment_id = request.GET.get('appointment_id', '')

    if not order_id or not appointment_id:
        messages.error(request, 'Invalid payment verification request.')
        return redirect('my_appointments')

    appointment = get_object_or_404(Appointment, id=appointment_id)

    # Idempotency guard — never double-record
    if appointment.payments.filter(payment_status='Completed').exists():
        return redirect('payment_receipt', appointment_id=appointment.id)

    # Ask Cashfree for the real payment status
    result = verify_upi_payment(order_id)

    if result['success']:
        # Record the payment
        payment = Payment.objects.create(
            appointment=appointment,
            amount=appointment.doctor.consultation_fee,
            payment_status='Completed',
            payment_method='UPI',
            transaction_id=order_id,
            razorpay_order_id=order_id,   # re-use field for CF order id
            razorpay_payment_id=order_id,
            payment_date=timezone.now(),
        )

        # Mark billing as paid
        billing = appointment.billings.filter(billing_type='Consultation').first()
        if billing:
            billing.is_paid = True
            billing.save()

        # Send payment receipt email
        try:
            email_utils.send_payment_receipt(appointment, payment)
        except Exception:
            pass

        messages.success(request, '✅ Payment successful! Your appointment is confirmed.')
        return redirect('payment_receipt', appointment_id=appointment.id)
    else:
        status_text = result.get('status', 'Unknown')
        
        # If still pending/active, don't fail immediately - just tell user it's pending
        if status_text in ['ACTIVE', 'PENDING']:
            messages.info(request, 'Payment is still pending. If you just paid, please wait a moment.')
            return redirect('appointment_detail', appointment_id=appointment.id)
            
        messages.error(request, f'Payment not completed. Status: {status_text}. Please try again.')
        return redirect('payment_failed')


@csrf_exempt
def process_payment(request):
    """Cashfree S2S payment endpoint (replaces JS SDK)"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except:
            data = request.POST

        payment_session_id = data.get('payment_session_id')
        upi_id = data.get('upi_id')

        url = "https://sandbox.cashfree.com/pg/orders/sessions"

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-version": "2023-08-01",
            "x-client-id": getattr(django_settings, 'CASHFREE_APP_ID', ''),
            "x-client-secret": getattr(django_settings, 'CASHFREE_SECRET_KEY', '')
        }

        payload = {
            "payment_session_id": payment_session_id,
            "payment_method": {
                "upi": {
                    "channel": "collect",
                    "upi_id": upi_id if upi_id else None
                }
            }
        }

        import requests
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            return JsonResponse(response.json())
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=500)
    
    return JsonResponse({'message': 'Invalid request'}, status=400)


@csrf_exempt
def payment_webhook(request):
    """Cashfree webhook endpoint — auto-confirms appointments on backend payment events."""
    if request.method != 'POST':
        return JsonResponse({'status': 'method not allowed'}, status=405)

    try:
        payload = json.loads(request.body)
        event_type = payload.get('type', '')

        if event_type == 'PAYMENT_SUCCESS_WEBHOOK':
            order_id = (
                payload.get('data', {})
                       .get('order', {})
                       .get('order_id', '')
            )
            if order_id and order_id.startswith('VB-'):
                parts = order_id.split('-')
                if len(parts) >= 2:
                    try:
                        appt = Appointment.objects.get(id=parts[1])
                        if not appt.payments.filter(payment_status='Completed').exists():
                            Payment.objects.create(
                                appointment=appt,
                                amount=appt.doctor.consultation_fee,
                                payment_status='Completed',
                                payment_method='UPI',
                                transaction_id=order_id,
                                razorpay_order_id=order_id,
                                razorpay_payment_id=order_id,
                                payment_date=timezone.now(),
                            )
                    except Appointment.DoesNotExist:
                        pass

        return JsonResponse({'status': 'ok'})
    except Exception as exc:
        return JsonResponse({'status': 'error', 'message': str(exc)})


@login_required
def payment_receipt(request, appointment_id):
    """Show a clean payment receipt after successful UPI transaction."""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.patient.user != request.user:
        messages.error(request, 'Access denied.')
        return redirect('my_appointments')

    payment = appointment.payments.filter(payment_status='Completed').order_by('-created_at').first()
    if not payment:
        messages.warning(request, 'No completed payment found for this appointment.')
        return redirect('appointment_detail', appointment_id=appointment_id)

    return render(request, 'appointment/payment_receipt.html', {
        'appointment': appointment,
        'payment': payment,
    })


def payment_failed(request):
    """Shown when UPI payment verification fails or is cancelled."""
    return render(request, 'appointment/payment_failed.html')


@login_required
def payment_success(request, appointment_id):
    """Legacy success page — kept for backward compatibility with old flow."""
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.patient.user != request.user:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('my_appointments')

    if request.method == 'POST' or request.method == 'GET':
        payment = appointment.payments.filter(payment_status='Processing').first()

        if payment:
            payment.payment_status = 'Completed'
            payment.payment_date = timezone.now()
            payment.save()

            billing = appointment.billings.filter(billing_type='Consultation').first()
            if billing:
                billing.is_paid = True
                billing.save()

        context = {
            'appointment': appointment,
            'payment': payment,
        }
        return render(request, 'appointment/payment_success.html', context)




@login_required
def patient_dashboard(request):
    """Patient dashboard with appointments, stats, and quick actions."""
    patient, _ = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
    )
    
    # Get all appointments for this patient
    all_appointments = Appointment.objects.filter(patient=patient).select_related('doctor', 'doctor__specialization')
    
    # Categorize appointments
    today = timezone.now().date()
    upcoming = all_appointments.filter(date__gte=today, status__in=['Pending', 'Confirmed']).order_by('date', 'time')
    completed = all_appointments.filter(status='Completed').order_by('-date', '-time')
    cancelled = all_appointments.filter(status='Cancelled').order_by('-date', '-time')
    
    # Calculate stats
    total_appointments = all_appointments.count()
    upcoming_count = upcoming.count()
    completed_count = completed.count()
    cancelled_count = cancelled.count()
    
    # Get payment history
    payments = Payment.objects.filter(
        appointment__patient=patient,
        payment_status='Completed'
    ).select_related('appointment', 'appointment__doctor').order_by('-payment_date')
    
    # Calculate total spent
    total_spent = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    # Get reviews by this patient
    reviews = Review.objects.filter(patient=patient).select_related('doctor', 'appointment')
    
    # Get greeting based on time
    current_hour = timezone.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    # Get patient's uploaded medical records
    medical_records = patient.medical_records.all()

    context = {
        'patient': patient,
        'greeting': greeting,
        'total_appointments': total_appointments,
        'upcoming_count': upcoming_count,
        'completed_count': completed_count,
        'cancelled_count': cancelled_count,
        'upcoming_appointments': upcoming,
        'completed_appointments': completed,
        'cancelled_appointments': cancelled,
        'payments': payments,
        'total_spent': total_spent,
        'reviews': reviews,
        'medical_records': medical_records,
    }
    return render(request, 'appointment/patient_dashboard.html', context)


@login_required
def update_profile(request):
    """Update patient profile information."""
    patient, _ = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'name': request.user.get_full_name() or request.user.username,
            'email': request.user.email
        }
    )
    
    if request.method == 'POST':
        # Update patient info
        patient.name = request.POST.get('name')
        patient.phone = request.POST.get('phone')
        patient.email = request.POST.get('email')
        patient.date_of_birth = request.POST.get('date_of_birth') or None
        patient.gender = request.POST.get('gender')
        patient.blood_group = request.POST.get('blood_group')
        patient.address = request.POST.get('address')
        patient.emergency_contact = request.POST.get('emergency_contact')
        patient.medical_history = request.POST.get('medical_history')
        patient.save()
        
        # Update user email
        request.user.email = patient.email
        request.user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('patient_dashboard')
    
    return redirect('patient_dashboard')



@login_required
def doctor_dashboard(request):
    """Doctor dashboard with appointments, stats, and revenue."""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found. Please contact administrator.')
        return redirect('home')
    
    today = timezone.now().date()
    this_month = today.replace(day=1)
    
    # Appointment stats
    total_appointments = Appointment.objects.filter(doctor=doctor).count()
    today_appointments = Appointment.objects.filter(doctor=doctor, date=today).order_by('time')
    pending_appointments = Appointment.objects.filter(doctor=doctor, status='Pending').count()
    completed_appointments = Appointment.objects.filter(doctor=doctor, status='Completed').count()
    
    # Unique patients count
    total_patients = Appointment.objects.filter(doctor=doctor).values('patient').distinct().count()
    
    # Revenue stats
    monthly_revenue = Payment.objects.filter(
        appointment__doctor=doctor,
        appointment__date__gte=this_month,
        payment_status='Completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_revenue = Payment.objects.filter(
        appointment__doctor=doctor,
        payment_status='Completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Reviews
    avg_rating = doctor.reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    total_reviews = doctor.reviews.count()
    recent_reviews = doctor.reviews.select_related('patient', 'appointment').order_by('-created_at')[:5]
    
    # Recent appointments
    recent_appointments = Appointment.objects.filter(
        doctor=doctor
    ).select_related('patient').order_by('-date', '-time')[:10]
    
    # Pending requests
    pending_requests = Appointment.objects.filter(
        doctor=doctor,
        status='Pending'
    ).select_related('patient').order_by('date', 'time')[:10]
    
    # Weekly appointment chart data
    weekly_data = []
    for i in range(7):
        day = today - timedelta(days=6-i)
        count = Appointment.objects.filter(doctor=doctor, date=day).count()
        weekly_data.append({
            'day': day.strftime('%a'),
            'count': count,
            'date': day.strftime('%Y-%m-%d')
        })
    
    # Get greeting based on time
    current_hour = timezone.now().hour
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 17:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"
    
    context = {
        'doctor': doctor,
        'greeting': greeting,
        'today_appointments': today_appointments,
        'total_appointments': total_appointments,
        'total_patients': total_patients,
        'pending_appointments': pending_appointments,
        'completed_appointments': completed_appointments,
        'monthly_revenue': monthly_revenue,
        'total_revenue': total_revenue,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'total_reviews': total_reviews,
        'recent_reviews': recent_reviews,
        'recent_appointments': recent_appointments,
        'pending_requests': pending_requests,
        'weekly_data': weekly_data,
    }
    return render(request, 'appointment/doctor_dashboard.html', context)


@login_required
def update_appointment_status(request, appointment_id):
    """AJAX endpoint to update appointment status."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
    
    try:
        import json
        data = json.loads(request.body)
        status = data.get('status')
        
        if status not in ['Confirmed', 'Completed', 'Cancelled']:
            return JsonResponse({'success': False, 'message': 'Invalid status'}, status=400)
        
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Check if user is the doctor for this appointment
        try:
            doctor = Doctor.objects.get(user=request.user)
            if appointment.doctor != doctor:
                return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
        except Doctor.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Doctor profile not found'}, status=403)
        
        # Update status
        appointment.status = status
        if status == 'Cancelled':
            appointment.cancelled_at = timezone.now()
        appointment.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Appointment marked as {status}',
            'status': status
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


@login_required
def update_doctor_profile(request):
    """Update doctor profile information."""
    try:
        doctor = Doctor.objects.get(user=request.user)
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        # Update doctor info
        doctor.name = request.POST.get('name')
        doctor.qualification = request.POST.get('qualification')
        doctor.experience_years = request.POST.get('experience_years')
        doctor.consultation_fee = request.POST.get('consultation_fee')
        doctor.available_days = request.POST.get('available_days')
        doctor.available_time = request.POST.get('available_time')
        doctor.phone = request.POST.get('phone')
        doctor.email = request.POST.get('email')
        doctor.bio = request.POST.get('bio')
        doctor.is_available = request.POST.get('is_available') == 'on'
        doctor.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('doctor_dashboard')
    
    return redirect('doctor_dashboard')



def verify_otp(request):
    if not request.session.get('reg_otp'):
        messages.error(request, 'Session expired. Please register again.')
        return redirect('register')

    email = request.session.get('reg_email', '')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        stored_otp = request.session.get('reg_otp')
        otp_created_at = request.session.get('otp_created_at')

        # Check expiry (10 minutes)
        if otp_created_at:
            created_time = datetime.fromisoformat(otp_created_at.replace('+00:00', ''))
            if datetime.utcnow() > created_time.replace(tzinfo=None) + timedelta(minutes=10):
                messages.error(request, '⏰ OTP expired! Please register again.')
                # Clear session
                for key in ['reg_otp','reg_email','reg_username','reg_password','reg_first_name','reg_last_name','otp_created_at']:
                    request.session.pop(key, None)
                return redirect('register')

        if entered_otp == stored_otp:
            reg_username = request.session.get('reg_username')
            
            # Protection against double-click race conditions
            if User.objects.filter(username=reg_username).exists():
                for key in ['reg_otp','reg_email','reg_username','reg_password','reg_first_name',
                            'reg_last_name','reg_name','reg_phone','reg_date_of_birth',
                            'reg_gender','reg_blood_group','reg_address','otp_created_at']:
                    request.session.pop(key, None)
                messages.success(request, '✅ Account verified! Welcome to VitalBook.')
                return redirect('login')

            # Create the user
            try:
                user = User.objects.create_user(
                    username=request.session['reg_username'],
                    email=request.session['reg_email'],
                    password=request.session['reg_password'],
                    first_name=request.session['reg_first_name'],
                    last_name=request.session.get('reg_last_name', ''),
                )
                user.is_active = True
                user.save()

                # Create OTPVerification record so they can book appointments
                OTPVerification.objects.create(user=user, is_verified=True, otp_type='email')

                # Create patient profile and link extra details
                try:
                    patient, created = Patient.objects.get_or_create(user=user)
                    if created or not patient.name:
                        patient.name = request.session.get('reg_name', '')
                        patient.email = request.session.get('reg_email', '')
                        patient.phone = request.session.get('reg_phone', '')
                        dob = request.session.get('reg_date_of_birth', '')
                        if dob:
                            patient.date_of_birth = dob
                        patient.gender = request.session.get('reg_gender', '')
                        patient.blood_group = request.session.get('reg_blood_group', '')
                        patient.address = request.session.get('reg_address', '')
                        patient.save()
                except:
                    pass

                # Clear session
                for key in ['reg_otp','reg_email','reg_username','reg_password',
                            'reg_first_name','reg_last_name','reg_name','reg_phone',
                            'reg_date_of_birth','reg_gender','reg_blood_group','reg_address',
                            'otp_created_at']:
                    request.session.pop(key, None)

                # Send welcome email
                try:
                    send_mail(
                        subject='🎉 Welcome to VitalBook!',
                        message=f'Welcome {user.first_name}! Your account has been verified.',
                        from_email=django_settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                        html_message=f'''
<div style="font-family:Inter,Arial,sans-serif;max-width:500px;margin:0 auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
    <div style="background:linear-gradient(135deg,#0d6efd,#0056b3);padding:32px;text-align:center;">
        <h1 style="color:white;margin:0;">🎉 Welcome to VitalBook!</h1>
    </div>
    <div style="padding:32px;text-align:center;">
        <h2 style="color:#0f172a;">Hi {user.first_name}! 👋</h2>
        <p style="color:#64748b;">Your account has been successfully verified. You can now book appointments with top doctors.</p>
        <a href="http://127.0.0.1:8000/login/" style="background:#0d6efd;color:white;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;">Login Now →</a>
    </div>
</div>
                        '''
                    )
                except:
                    pass

                messages.success(request, '✅ Account verified! Welcome to VitalBook.')
                return redirect('login')

            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, '❌ Invalid OTP! Please try again.')

    # Mask email for display
    masked_email = email[:3] + '****' + email[email.find('@'):]

    return render(request, 'appointment/verify_otp.html', {
        'masked_email': masked_email,
    })



def resend_otp(request):
    email = request.session.get('reg_email')
    first_name = request.session.get('reg_first_name', 'User')

    if not email:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('register')

    # Generate new OTP
    otp = ''.join(random.choices(string.digits, k=6))
    request.session['reg_otp'] = otp
    request.session['otp_created_at'] = str(timezone.now())

    try:
        send_mail(
            subject='🔐 VitalBook — New OTP Code',
            message=f'Your new OTP is: {otp}. Valid for 10 minutes.',
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
            html_message=f'''
<div style="font-family:Arial,sans-serif;max-width:400px;margin:0 auto;padding:32px;text-align:center;">
    <h2 style="color:#0d6efd;">New OTP Code</h2>
    <div style="font-size:42px;font-weight:800;color:#0d6efd;letter-spacing:12px;background:#f0f7ff;padding:20px;border-radius:12px;margin:20px 0;">{otp}</div>
    <p style="color:#64748b;">Valid for 10 minutes. Do not share this code.</p>
</div>
            '''
        )
        messages.success(request, f'✅ New OTP sent to {email}!')
    except Exception as e:
        print(f'Email send error: {e}')
        messages.warning(request, f'Email failed to send.')

    return redirect('verify_otp')

@login_required
def download_prescription_pdf(request, appointment_id):
    """Generate and download a professional PDF prescription."""
    appointment = get_object_or_404(
        Appointment,
        id=appointment_id,
        patient__user=request.user  # patients can only download their own
    )
    prescription = Prescription.objects.filter(appointment=appointment).first()

    if not prescription:
        messages.error(request, 'No prescription found for this appointment.')
        return redirect('appointment_detail', appointment_id=appointment_id)

    from django.template.loader import get_template
    from xhtml2pdf import pisa

    template = get_template('appointment/prescription_pdf.html')
    context = {'appointment': appointment, 'prescription': prescription}
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    safe_name = f"Prescription_{appointment.patient.name.replace(' ', '_')}_{appointment.date}"
    response['Content-Disposition'] = f'attachment; filename="{safe_name}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        messages.error(request, 'Error generating PDF. Please try again.')
        return redirect('appointment_detail', appointment_id=appointment_id)

    return response


@login_required
def view_prescription(request, appointment_id):
    """Anti-Gravity web view for Digital Prescription"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Security check: only patient or doctor/staff can view
    is_patient = hasattr(request.user, 'patient') and appointment.patient.user == request.user
    is_doctor = hasattr(request.user, 'doctor_profile') and appointment.doctor.user == request.user
    if not (is_patient or is_doctor or request.user.is_staff):
        messages.error(request, 'You do not have permission to view this prescription.')
        return redirect('home')

    prescription = Prescription.objects.filter(appointment=appointment).first()
    if not prescription:
        messages.error(request, 'No prescription found for this appointment.')
        return redirect('patient_dashboard')

    # Heuristic: active if appointment was <= 14 days ago (since duration varies)
    days_since = (timezone.now().date() - appointment.date).days
    is_active = days_since <= 14

    # Parse medicines text
    parsed_medicines = []
    lines = prescription.medicines.strip().split('\n')
    for line in lines:
        parts = line.split('-')
        if len(parts) >= 3:
            name = parts[0].strip()
            dosage = parts[1].strip()
            duration = '-'.join(parts[2:]).strip()
            parsed_medicines.append({'name': name, 'dosage': dosage, 'duration': duration})
        elif line.strip(): # Fallback if malformed
            parsed_medicines.append({'name': line.strip(), 'dosage': 'As directed', 'duration': 'As directed'})

    context = {
        'appointment': appointment,
        'prescription': prescription,
        'medicines': parsed_medicines,
        'is_active': is_active,
    }
    return render(request, 'appointment/view_prescription.html', context)

from django.contrib.admin.views.decorators import staff_member_required

# ── Existing admin changelist action views (redirect → changelist) ────────────

@staff_member_required
def confirm_appointment_admin(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Confirmed'
    appointment.save()
    messages.success(request, f'Appointment VB-{appointment_id} confirmed!')
    return redirect('/admin/appointment/appointment/')

@staff_member_required
def cancel_appointment_admin(request, appointment_id):
    """Cancel an appointment from the changelist action button."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Cancelled'
    appointment.cancelled_at = timezone.now()
    appointment.save()
    try:
        email_utils.send_appointment_cancelled(appointment, cancelled_by='admin')
    except Exception:
        pass
    messages.warning(request, f'❌ Appointment #{appointment.id} has been cancelled.')
    return redirect('admin:appointment_appointment_changelist')

@staff_member_required
def complete_appointment_admin(request, appointment_id):
    """Mark an appointment as Completed from the changelist action button."""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    appointment.status = 'Completed'
    appointment.save()
    messages.info(request, f'🏁 Appointment #{appointment.id} marked as completed.')
    return redirect('admin:appointment_appointment_changelist')


# ── Dashboard Approval Workflow views (redirect → admin:index) ────────────────

ADMIN_INDEX = '/admin/'   # fallback direct URL (custom admin site)

@staff_member_required
def admin_approve_appointment(request, appointment_id):
    """
    Approve (Confirm) a Pending appointment from the admin dashboard modal.
    Accepts POST (from the CSRF-protected form) and GET (direct URL access).
    Redirects back to the admin dashboard index.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status != 'Pending':
        messages.warning(
            request,
            f'⚠️ Appointment #{appointment.id} is already {appointment.status} '
            f'and cannot be approved again.'
        )
        return redirect(ADMIN_INDEX)

    appointment.status = 'Confirmed'
    appointment.save()

    # Notify patient by email (silent fail — email is non-critical)
    try:
        email_utils.send_appointment_confirmation(appointment)
    except Exception:
        pass

    messages.success(
        request,
        f'✅ Appointment #{appointment.id} for {appointment.patient.name} '
        f'with Dr. {appointment.doctor.name} confirmed. Patient notified.'
    )
    return redirect(ADMIN_INDEX)


@staff_member_required
def admin_cancel_appointment(request, appointment_id):
    """
    Cancel a Pending/Confirmed appointment from the admin dashboard modal.
    Accepts POST (from the CSRF-protected form) and GET (direct URL access).
    Redirects back to the admin dashboard index.
    """
    appointment = get_object_or_404(Appointment, id=appointment_id)

    if appointment.status not in ('Pending', 'Confirmed'):
        messages.warning(
            request,
            f'⚠️ Appointment #{appointment.id} is already {appointment.status} '
            f'and cannot be cancelled.'
        )
        return redirect(ADMIN_INDEX)

    appointment.status = 'Cancelled'
    appointment.cancelled_at = timezone.now()
    appointment.save()

    # Notify patient by email (silent fail)
    try:
        email_utils.send_appointment_cancelled(appointment, cancelled_by='admin')
    except Exception:
        pass

    messages.warning(
        request,
        f'❌ Appointment #{appointment.id} for {appointment.patient.name} has been cancelled.'
    )
    return redirect(ADMIN_INDEX)


def ajax_load_slots(request):
    """
    AJAX endpoint to load dynamic time slots based on doctor availability.
    """
    from datetime import datetime
    from .slot_utils import get_available_slots

    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    
    if not doctor_id or not date_str:
        return JsonResponse({'slots': [], 'error': 'Missing parameters'})

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        slots = get_available_slots(doctor_id, selected_date)
        return JsonResponse({'slots': slots})
    except Exception as e:
        return JsonResponse({'slots': [], 'error': str(e)})


# ── Medical Records ────────────────────────────────────────────────────────────

@login_required
def upload_medical_record(request):
    """Patient uploads a PDF medical report from their dashboard."""
    patient, _ = Patient.objects.get_or_create(
        user=request.user,
        defaults={
            'name':  request.user.get_full_name() or request.user.username,
            'email': request.user.email,
            'phone': '0000000000',
        }
    )

    if request.method == 'POST':
        report_name = request.POST.get('report_name', '').strip()
        pdf_file    = request.FILES.get('pdf_file')

        if not report_name:
            messages.error(request, 'Please enter a report name.')
            return redirect('patient_dashboard')
        if not pdf_file:
            messages.error(request, 'Please select a PDF file to upload.')
            return redirect('patient_dashboard')
        if not pdf_file.name.lower().endswith('.pdf'):
            messages.error(request, 'Only PDF files are allowed.')
            return redirect('patient_dashboard')
        if pdf_file.size > 10 * 1024 * 1024:          # 10 MB cap
            messages.error(request, 'File is too large. Maximum size is 10 MB.')
            return redirect('patient_dashboard')

        MedicalRecord.objects.create(
            patient=patient,
            report_name=report_name,
            pdf_file=pdf_file,
        )
        messages.success(request, f'"{report_name}" uploaded successfully.')
    else:
        messages.error(request, 'Invalid request.')

    return redirect('patient_dashboard')


@login_required
def delete_medical_record(request, record_id):
    """Patient deletes one of their own medical records."""
    record = get_object_or_404(MedicalRecord, id=record_id)

    # Security: only the owner may delete
    patient = getattr(request.user, 'patient', None)
    if not patient or record.patient != patient:
        messages.error(request, 'You do not have permission to delete this record.')
        return redirect('patient_dashboard')

    if request.method == 'POST':
        name = record.report_name
        # Remove the physical file from disk as well
        if record.pdf_file:
            record.pdf_file.delete(save=False)
        record.delete()
        messages.success(request, f'"{name}" has been removed.')
    else:
        messages.error(request, 'Invalid request method.')

    return redirect('patient_dashboard')


from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_appointment_details(request, appointment_id):
    try:
        appointment = Appointment.objects.select_related('patient', 'doctor', 'doctor__specialization').get(id=appointment_id)
    except Appointment.DoesNotExist:
        return JsonResponse({'error': 'Appointment not found'}, status=404)

    spec_name = appointment.doctor.specialization.name if appointment.doctor.specialization else 'General'

    medicine_mapping = {
        'Cardiologist': 'Aspirin 75mg - 1 tablet daily - 30 Days\nAtorvastatin 10mg - 1 tablet nightly - 30 Days',
        'Dermatologist': 'Cetirizine 10mg - 1 tablet daily - 5 Days\nKetoconazole Cream - Apply twice daily - 14 Days',
        'Pediatrician': 'Paracetamol Syrup 250mg - 5ml as needed - 3 Days\nVitamin C Drops - 5 drops daily - 10 Days',
        'Orthopedist': 'Ibuprofen 400mg - 1 tablet twice daily - 5 Days\nCalcium + Vitamin D3 - 1 tablet daily - 30 Days',
        'Neurologist': 'Pregabalin 50mg - 1 tablet nightly - 14 Days\nVitamin B12 - 1 tablet daily - 30 Days',
        'Dentist': 'Amoxicillin 500mg - 1 tablet 3 times a day - 5 Days\nIbuprofen 400mg - 1 tablet twice daily - 3 Days',
        'Ophthalmologist': 'Refresh Tears - 1 drop 4 times a day - 14 Days\nOlopatadine Eye Drops - 1 drop twice daily - 7 Days',
    }
    
    suggested_medicines = medicine_mapping.get(spec_name, 'Paracetamol 500mg - 1 tablet as needed - 3 Days\nVitamin C - 1 tablet daily - 10 Days')

    return JsonResponse({
        'patient_name': appointment.patient.name,
        'doctor_name': appointment.doctor.name,
        'doctor_specialization': spec_name,
        'suggested_medicines': suggested_medicines
    })


def diagnose(request):
    import sys
    import os
    import traceback
    from django.conf import settings
    from django.db import connection
    from django.test import RequestFactory
    from django.contrib.sessions.middleware import SessionMiddleware
    from django.contrib.messages.storage.fallback import FallbackStorage
    
    views_path = __file__
    
    # Enable query logging temporarily
    old_debug = settings.DEBUG
    settings.DEBUG = True
    connection.queries_log.clear()
    
    # Run a test registration POST locally on the server inside this view!
    factory = RequestFactory()
    post_req = factory.post('/register/', {
        'name': 'Diagnostics Test User',
        'username': 'diag_test_user_unique',
        'email': 'diag_test_user_unique@example.com',
        'phone': '9876543210',
        'password': 'TestPass@123',
        'confirm_password': 'TestPass@123',
        'gender': 'Male',
        'blood_group': 'O+',
        'address': '123 Test Street Bangalore',
        'date_of_birth': '2000-01-01',
    })
    
    # Setup session and messages
    middleware = SessionMiddleware(lambda req: None)
    middleware.process_request(post_req)
    post_req.session.save()
    post_req._messages = FallbackStorage(post_req)
    
    tb_str = ""
    status = ""
    try:
        from appointment.views import register
        response = register(post_req)
        status = f"Redirect to {response.url}" if response.status_code == 302 else f"Status {response.status_code}"
    except Exception as e:
        status = f"Exception: {e}"
        # Format the exception chain explicitly
        exc_lines = traceback.format_exception(type(e), e, e.__traceback__)
        tb_str = "".join(exc_lines)
        
    # Get connection queries
    queries = list(connection.queries)
    
    # Restore DEBUG
    settings.DEBUG = old_debug
    
    otp_lines = []
    try:
        with open(views_path, 'r', encoding='utf-8') as f:
            for ln_num, line in enumerate(f, 1):
                if 'OTPVerification' in line:
                    otp_lines.append(f"{ln_num}: {line.strip()}")
    except Exception as e:
        otp_lines.append(f"Error reading views.py: {e}")
        
    return JsonResponse({
        'views_file': views_path,
        'cwd': os.getcwd(),
        'status': status,
        'traceback': tb_str,
        'otp_lines': otp_lines,
        'queries': queries,
    })





