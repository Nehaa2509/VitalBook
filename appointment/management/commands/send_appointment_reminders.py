from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, datetime, timedelta
from appointment.models import Appointment
from appointment.email_utils import send_reminder_email
import pytz
import sys

# Force UTF-8 output on Windows so emoji in log lines don't crash the console
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf-8-sig'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class Command(BaseCommand):
    help = 'Send reminders every hour for all todays appointments'

    def handle(self, *args, **kwargs):
        IST = pytz.timezone('Asia/Kolkata')
        now = datetime.now(IST)
        today = now.date()

        self.stdout.write(f'\n{"="*50}')
        self.stdout.write(f'Running at: {now.strftime("%d %b %Y %I:%M %p")}')
        self.stdout.write(f'{"="*50}\n')

        # Get ALL confirmed appointments for today
        todays_appointments = Appointment.objects.filter(
            date=today,
            status='Confirmed'
        ).select_related('patient__user', 'doctor', 'doctor__specialization')

        self.stdout.write(f'Found {todays_appointments.count()} appointments today\n')

        sent_count = 0

        for appointment in todays_appointments:
            appt_datetime = IST.localize(
                datetime.combine(today, appointment.time)
            )

            minutes_left = (appt_datetime - now).total_seconds() / 60
            hours_left = minutes_left / 60

            patient_email = appointment.patient.user.email

            self.stdout.write(
                f'\nPatient: {appointment.patient.user.get_full_name()} | '
                f'Time: {appointment.time.strftime("%I:%M %p")} | '
                f'Hours left: {round(hours_left, 1)}'
            )

            # Skip if appointment already passed
            if minutes_left <= 0:
                self.stdout.write('  ⏭️  Already passed. Skipping.')
                continue

            # FINAL REMINDER — between 55 and 65 minutes before
            if 55 <= minutes_left <= 65:
                send_reminder_email(
                    appointment=appointment,
                    reminder_label='⚡ Final Reminder — 1 Hour Before!',
                    hours_left=1.0,
                    is_final=True,
                )
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ⚡ FINAL reminder sent to {patient_email}')
                )

            # HOURLY REMINDERS — every full hour mark (within 5 min window)
            elif minutes_left > 65:
                # Check if we are near an hourly mark
                # e.g. 120 mins left = 2 hours, 180 = 3 hours etc
                minutes_mod = minutes_left % 60
                if minutes_mod <= 5 or minutes_mod >= 55:
                    send_reminder_email(
                        appointment=appointment,
                        reminder_label=f'Hourly Reminder — {round(hours_left, 0):.0f} Hours Before',
                        hours_left=round(hours_left, 1),
                        is_final=False,
                    )
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✅ Hourly reminder sent to {patient_email} '
                            f'({round(hours_left, 1)} hrs left)'
                        )
                    )
                else:
                    self.stdout.write(f'  ⏭️  Not at hourly mark yet. Skipping.')

        self.stdout.write(f'\n{"="*50}')
        self.stdout.write(self.style.SUCCESS(f'✅ Sent {sent_count} reminders'))
        self.stdout.write(f'{"="*50}\n')
