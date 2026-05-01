"""
Email utility functions for VitalBook.
Sends professional HTML emails for all key events.
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_appointment_confirmation(appointment):
    """Send booking confirmation email to patient."""
    try:
        if not appointment.patient.user or not appointment.patient.user.email:
            return False
        
        subject = f'✅ Appointment Confirmed – VitalBook (#{appointment.id})'
        context = {
            'appointment': appointment,
            'patient': appointment.patient,
            'doctor': appointment.doctor,
        }
        
        html_content = render_to_string('emails/appointment_confirmation.html', context)
        text_content = f'Your appointment with Dr. {appointment.doctor.name} is confirmed for {appointment.date} at {appointment.time}.'
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.user.email]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending confirmation email: {e}")
        return False


def send_appointment_cancelled(appointment, cancelled_by='patient'):
    """Send cancellation email to both patient and doctor."""
    try:
        # Email to patient
        if appointment.patient.user and appointment.patient.user.email:
            subject = f'❌ Appointment Cancelled – VitalBook (#{appointment.id})'
            context = {
                'appointment': appointment,
                'cancelled_by': cancelled_by,
            }
            
            html_content = render_to_string('emails/appointment_cancelled.html', context)
            text_content = f'Your appointment with Dr. {appointment.doctor.name} on {appointment.date} has been cancelled.'
            
            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [appointment.patient.user.email]
            )
            email.attach_alternative(html_content, 'text/html')
            email.send(fail_silently=True)
        
        # Email to doctor (if doctor has user account)
        if appointment.doctor.user and appointment.doctor.user.email:
            subject_doctor = f'📋 Appointment Cancelled by Patient – VitalBook'
            html_doctor = render_to_string('emails/doctor_cancellation_notice.html', context)
            
            email2 = EmailMultiAlternatives(
                subject_doctor,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [appointment.doctor.user.email]
            )
            email2.attach_alternative(html_doctor, 'text/html')
            email2.send(fail_silently=True)
        
        return True
    except Exception as e:
        print(f"Error sending cancellation email: {e}")
        return False


def send_appointment_reminder(appointment):
    """Send 24-hour reminder to patient."""
    try:
        if not appointment.patient.user or not appointment.patient.user.email:
            return False
        
        subject = f'⏰ Reminder: Appointment Tomorrow – VitalBook'
        context = {'appointment': appointment}
        
        html_content = render_to_string('emails/appointment_reminder.html', context)
        text_content = f'Reminder: You have an appointment with Dr. {appointment.doctor.name} tomorrow at {appointment.time}.'
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.user.email]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending reminder email: {e}")
        return False


def send_payment_receipt(appointment, payment):
    """Send payment receipt to patient."""
    try:
        if not appointment.patient.user or not appointment.patient.user.email:
            return False
        
        subject = f'💳 Payment Receipt – VitalBook (Booking #{appointment.id})'
        context = {
            'appointment': appointment,
            'payment': payment,
        }
        
        html_content = render_to_string('emails/payment_receipt.html', context)
        text_content = f'Payment of ₹{payment.amount} received for your appointment with Dr. {appointment.doctor.name}.'
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [appointment.patient.user.email]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending payment receipt email: {e}")
        return False


def send_review_thankyou(review):
    """Send thank you email after patient submits review."""
    try:
        if not review.patient.user or not review.patient.user.email:
            return False
        
        subject = '⭐ Thank You for Your Review – VitalBook'
        context = {'review': review}
        
        html_content = render_to_string('emails/review_thankyou.html', context)
        text_content = f'Thank you for reviewing Dr. {review.doctor.name} on VitalBook.'
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [review.patient.user.email]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending review thank you email: {e}")
        return False


def send_welcome_email(user, patient):
    """Send welcome email to new patients."""
    try:
        if not user.email:
            return False
        
        subject = '👋 Welcome to VitalBook!'
        context = {
            'user': user,
            'patient': patient,
        }
        
        html_content = render_to_string('emails/welcome_email.html', context)
        text_content = f'Welcome to VitalBook, {patient.name}! Your account has been created successfully.'
        
        email = EmailMultiAlternatives(
            subject,
            text_content,
            settings.DEFAULT_FROM_EMAIL,
            [user.email]
        )
        email.attach_alternative(html_content, 'text/html')
        email.send(fail_silently=True)
        return True
    except Exception as e:
        print(f"Error sending welcome email: {e}")
        return False



def send_reminder_email(appointment, reminder_label, hours_left, is_final=False):
    """
    Send an appointment-day reminder email with dynamic content based on timing.

    Args:
        appointment:    Appointment model instance.
        reminder_label: Human-readable label for this reminder slot.
        hours_left:     Approximate hours remaining until the appointment.
        is_final:       True when this is the 1-hour-before final reminder.
    """
    patient_name  = (
        appointment.patient.user.get_full_name()
        or appointment.patient.user.username
    )
    patient_email = appointment.patient.user.email
    doctor_name   = appointment.doctor.name
    appt_date     = appointment.date.strftime('%A, %d %B %Y')
    appt_time_str = appointment.time.strftime('%I:%M %p')

    # ── Colour / text theme based on urgency ──────────────────────────────────
    if is_final:
        subject          = '\u26a1 FINAL REMINDER: Appointment in 1 Hour \u2014 VitalBook'
        header_color     = '#dc2626'
        header_bg        = 'linear-gradient(135deg,#dc2626,#b91c1c)'
        urgency_text     = '\u26a1 Your appointment is in just 1 hour!'
        urgency_color    = '#fee2e2'
        urgency_border   = '#ef4444'
        urgency_txtcolor = '#991b1b'
        icon             = '\u26a1'
    elif hours_left <= 3:
        subject          = f'\u23f0 Reminder: Appointment in {round(hours_left, 0):.0f} Hours \u2014 VitalBook'
        header_color     = '#f97316'
        header_bg        = 'linear-gradient(135deg,#f97316,#ea580c)'
        urgency_text     = f'\u23f0 Your appointment is approaching in {round(hours_left, 0):.0f} hours!'
        urgency_color    = '#fff7ed'
        urgency_border   = '#f97316'
        urgency_txtcolor = '#92400e'
        icon             = '\u23f0'
    else:
        subject          = '\U0001f4c5 Appointment Reminder Today \u2014 VitalBook'
        header_color     = '#0d6efd'
        header_bg        = 'linear-gradient(135deg,#0d6efd,#0056b3)'
        urgency_text     = '\U0001f4c5 You have an appointment scheduled today!'
        urgency_color    = '#eff6ff'
        urgency_border   = '#0d6efd'
        urgency_txtcolor = '#1e40af'
        icon             = '\U0001f4c5'

    # Safely fetch optional related fields
    try:
        spec_name = appointment.doctor.specialization.name
    except Exception:
        spec_name = 'General'

    try:
        fee = appointment.doctor.consultation_fee
    except Exception:
        fee = '--'

    html_message = f"""<!DOCTYPE html>
<html>
<body style="font-family:Inter,Arial,sans-serif;background:#f4f6f9;padding:40px 0;margin:0;">
<div style="max-width:560px;margin:0 auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
    <div style="background:{header_bg};padding:28px 32px;text-align:center;">
        <div style="font-size:48px;margin-bottom:8px;">{icon}</div>
        <h1 style="color:white;margin:0;font-size:20px;font-weight:700;">\U0001f48a VitalBook</h1>
        <p style="color:rgba(255,255,255,0.85);margin:6px 0 0;font-size:13px;">{reminder_label}</p>
    </div>
    <div style="padding:32px;">
        <h2 style="color:#0f172a;margin:0 0 6px;font-size:18px;font-weight:700;">Appointment Reminder!</h2>
        <p style="color:#64748b;margin:0 0 20px;font-size:14px;">
            Dear <strong style="color:#0f172a;">{patient_name}</strong>,
            this is a reminder for your upcoming appointment.
        </p>
        <div style="background:{urgency_color};border-left:4px solid {urgency_border};border-radius:8px;padding:14px 16px;margin-bottom:20px;">
            <p style="margin:0;font-size:13px;font-weight:600;color:{urgency_txtcolor};">{urgency_text}</p>
        </div>
        <div style="background:#f8fafc;border-radius:10px;padding:20px;margin-bottom:20px;border:1px solid #e2e8f0;">
            <h4 style="margin:0 0 14px;color:#0f172a;font-size:14px;font-weight:600;border-bottom:1px solid #e2e8f0;padding-bottom:10px;">
                \U0001f4cb Appointment Details
            </h4>
            <table style="width:100%;border-collapse:collapse;">
                <tr>
                    <td style="padding:8px 0;color:#64748b;font-size:13px;width:130px;">\U0001f468 Doctor</td>
                    <td style="padding:8px 0;font-weight:600;color:#0f172a;font-size:13px;">Dr. {doctor_name}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#64748b;font-size:13px;">\U0001f3e5 Specialization</td>
                    <td style="padding:8px 0;color:#0f172a;font-size:13px;">{spec_name}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#64748b;font-size:13px;">\U0001f4c5 Date</td>
                    <td style="padding:8px 0;font-weight:600;color:#0f172a;font-size:13px;">{appt_date}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#64748b;font-size:13px;">\u23f0 Time</td>
                    <td style="padding:8px 0;font-size:16px;font-weight:800;color:{header_color};">{appt_time_str}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#64748b;font-size:13px;">\U0001f4cb Booking ID</td>
                    <td style="padding:8px 0;font-weight:600;color:#0f172a;font-size:13px;">VB-{appointment.id}</td>
                </tr>
                <tr>
                    <td style="padding:8px 0;color:#64748b;font-size:13px;">\U0001f4b0 Fee</td>
                    <td style="padding:8px 0;font-weight:700;color:#0d6efd;font-size:13px;">Rs.{fee}</td>
                </tr>
            </table>
        </div>
        <div style="background:#fef9c3;border-radius:8px;padding:14px 16px;margin-bottom:24px;">
            <p style="margin:0 0 6px;font-size:13px;font-weight:600;color:#854d0e;">\U0001f4a1 Preparation Tips:</p>
            <ul style="margin:0;padding-left:16px;color:#92400e;font-size:12px;line-height:1.8;">
                <li>Arrive <strong>10-15 minutes early</strong></li>
                <li>Carry any <strong>previous prescriptions or reports</strong></li>
                <li>Bring a valid <strong>government-issued ID</strong></li>
                <li>Note down your <strong>symptoms and questions</strong> for the doctor</li>
            </ul>
        </div>
        <div style="text-align:center;">
            <a href="http://127.0.0.1:8000/patient/dashboard/#upcoming-appointments"
               style="background:{header_bg};color:white;padding:13px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:14px;display:inline-block;">
                View Appointment Details
            </a>
        </div>
    </div>
    <div style="background:#f8fafc;padding:20px 32px;text-align:center;border-top:1px solid #e2e8f0;">
        <p style="color:#94a3b8;font-size:12px;margin:0 0 4px;">&copy; 2026 VitalBook &middot; Your Health, Our Priority</p>
        <p style="color:#cbd5e1;font-size:11px;margin:0;">support@vitalbook.in &middot; This is an automated reminder</p>
    </div>
</div>
</body>
</html>"""

    plain_message = f"""Appointment Reminder -- VitalBook

Dear {patient_name},

{urgency_text}

Appointment Details:
  Doctor        : Dr. {doctor_name}
  Specialization: {spec_name}
  Date          : {appt_date}
  Time          : {appt_time_str}
  Booking ID    : VB-{appointment.id}
  Fee           : Rs. {fee}

Please arrive 10-15 minutes early and carry any previous prescriptions or reports.

VitalBook Team
support@vitalbook.in
"""

    try:
        from django.core.mail import send_mail
        from django.conf import settings as django_settings
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[patient_email],
            html_message=html_message,
            fail_silently=True,
        )
        print(f'[OK] Reminder [{reminder_label}] sent to {patient_email}')
        return True
    except Exception as e:
        print(f'[ERROR] Reminder email error: {e}')
        return False
