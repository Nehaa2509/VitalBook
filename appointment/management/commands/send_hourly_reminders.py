from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, datetime, timedelta
from appointment.models import Appointment
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
class Command(BaseCommand):
    help = 'Send hourly reminders to patients on appointment day'

    def handle(self, *args, **kwargs):
        today = date.today()
        now = timezone.now()
        current_hour = now.hour

        # Get all confirmed appointments for today
        todays_appointments = Appointment.objects.filter(
            date=today,
            status='Confirmed'
        ).select_related('patient__user', 'doctor')

        self.stdout.write(f'Found {todays_appointments.count()} appointments today')

        sent_count = 0

        for appointment in todays_appointments:
            # Calculate hours left until appointment
            appt_time = appointment.time
            appt_datetime = datetime.combine(today, appt_time)
            appt_datetime_aware = timezone.make_aware(appt_datetime)

            hours_diff = (appt_datetime_aware - now).total_seconds() / 3600

            # Send reminders at these intervals: 8h, 6h, 4h, 2h, 1h before
            reminder_hours = [8, 6, 4, 2, 1]

            for remind_at in reminder_hours:
                # Check if we are within 30 minutes of the reminder time
                if abs(hours_diff - remind_at) <= 0.5:
                    context = {
                        'status': 'Reminder',
                        'patient_name': appointment.patient.user.get_full_name() or appointment.patient.user.username,
                        'doctor_name': appointment.doctor.name,
                        'date': appointment.date.strftime('%d %B %Y') if appointment.date else '',
                        'time': appointment.time.strftime('%I:%M %p') if appointment.time else '',
                    }
                    html_content = render_to_string('emails/appointment_email.html', context)
                    
                    try:
                        send_mail(
                            subject=f"⏰ Reminder: Appointment in {remind_at} hour(s) — VitalBook",
                            message=f"Reminder: Your appointment with Dr. {appointment.doctor.name} is in {remind_at} hour(s) at {appointment.time}.",
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[appointment.patient.user.email],
                            html_message=html_content,
                            fail_silently=True,
                        )
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'[ERROR] Reminder email error: {e}'))
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'[OK] Reminder sent to {appointment.patient.user.email} '
                            f'({remind_at}h before appointment)'
                        )
                    )
                    break

        self.stdout.write(
            self.style.SUCCESS(f'\n[Done] Sent {sent_count} reminders.')
        )
