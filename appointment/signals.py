"""
VitalBook Admin Notification Signals
=====================================
Fires an email to the admin whenever a Payment is saved as 'Completed'
so they can quickly confirm the linked appointment.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .otp_email import send_transactional_email
from django.template.loader import render_to_string
from django.db import transaction
from .models import Appointment, Prescription


@receiver(post_save, sender=Prescription)
def send_prescription_notification(sender, instance, created, **kwargs):
    """
    Send an email to the patient when a digital prescription is issued.
    """
    if created:
        appointment = instance.appointment
        patient_email = appointment.patient.user.email
        
        if patient_email:
            context = {
                'patient_name': appointment.patient.user.get_full_name() or appointment.patient.user.username,
                'doctor_name': appointment.doctor.name,
                'date': appointment.date.strftime('%d %B %Y') if appointment.date else '',
                'medicines': instance.medicines,
                'instructions': instance.instructions,
            }
            
            html_content = render_to_string('emails/prescription_email.html', context)
            subject = f"📝 Your Digital Prescription — VitalBook (VB-{appointment.id})"
            
            def send_email_task():
                send_transactional_email(patient_email, subject, html_content or "Your digital prescription has been issued.", context['patient_name'])
                    
            transaction.on_commit(send_email_task)


@receiver(post_save, sender='appointment.Payment')
def notify_admin_on_payment(sender, instance, created, **kwargs):
    """
    Send an admin notification email when a new completed payment arrives.
    Only fires on INSERT (created=True) to avoid repeat emails on updates.
    """
    if not created:
        return
    if instance.payment_status != 'Completed':
        return

    appointment = instance.appointment
    patient_name = (
        appointment.patient.user.get_full_name()
        or appointment.patient.user.username
    )
    doctor_name = appointment.doctor.name
    admin_email = getattr(settings, 'ADMIN_EMAIL', None)
    
    if appointment.status != 'Pending':
        appointment.status = 'Pending'
        appointment.save(update_fields=['status'])

    if not admin_email:
        return  # Silently skip if admin email is not configured

    confirm_url = (
        f'http://127.0.0.1:8000/appointments/{appointment.id}/confirm-admin/'
    )
    admin_url = 'http://127.0.0.1:8000/admin/appointment/appointment/'

    def send_admin_email_task():
        msg_body = (
            f'New appointment booked and payment received!<br><br>'
            f'Patient:      {patient_name}<br>'
            f'Doctor:       Dr. {doctor_name}<br>'
            f'Date:         {appointment.date}<br>'
            f'Time:         {appointment.time}<br>'
            f'Amount Paid:  ₹{instance.amount}<br><br>'
            f'Please confirm this appointment:<br><a href="{confirm_url}">{confirm_url}</a><br><br>'
            f'Or view all appointments in the admin panel:<br><a href="{admin_url}">{admin_url}</a>'
        )
        html_msg = f"<html><body><p>{msg_body}</p></body></html>"
        send_transactional_email(admin_email, f'🔔 New Booking — VB-{appointment.id} Needs Confirmation', html_msg, "Admin")

    transaction.on_commit(send_admin_email_task)


@receiver(post_save, sender=Appointment)
def send_appointment_notification(sender, instance, created, **kwargs):
    status = instance.status

    # Ensure date/time are proper objects for strftime
    if isinstance(instance.date, str) or isinstance(instance.time, str):
        instance.refresh_from_db()

    # Derive payment status from the Payment model (no redundant field needed)
    is_paid = instance.payments.filter(payment_status='Completed').exists()
    payment_status = 'Paid' if is_paid else 'Unpaid'

    context = {
        'status': status,
        'patient_name': instance.patient.user.get_full_name() or instance.patient.user.username,
        'doctor_name': instance.doctor.name,
        'date': instance.date.strftime('%d %B %Y') if instance.date else '',
        'time': instance.time.strftime('%I:%M %p') if instance.time else '',
        'payment_status': payment_status,  # ← passed to email template
    }

    if status in ['Pending', 'Confirmed', 'Cancelled']:
        html_content = render_to_string('emails/appointment_email.html', context)

        # Determine subject based on status
        if status == 'Pending':
            subject = f"✅ Appointment Booked — VitalBook (VB-{instance.id})"
        elif status == 'Confirmed':
            subject = f"✅ Appointment Confirmed — VitalBook (VB-{instance.id})"
        elif status == 'Cancelled':
            subject = f"❌ Appointment Cancelled — VitalBook (VB-{instance.id})"

        def send_status_email_task():
            send_transactional_email(instance.patient.user.email, subject, html_content or f"Your appointment status is {status}.", context['patient_name'])
                
        transaction.on_commit(send_status_email_task)

