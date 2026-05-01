"""
VitalBook — Smart Appointment Reminder Command
===============================================
Run this every 30 minutes via Task Scheduler (Windows) or cron (Linux/Mac).

Windows Task Scheduler:
    Action:  python manage.py send_reminders
    Trigger: Every 30 minutes, daily

Linux/Mac Cron (crontab -e):
    */30 * * * * cd /path/to/hospital && python manage.py send_reminders

Logic:
  - Sends reminders at fixed hours: midnight (0), 4 AM, 6 AM, 7 AM
  - Sends a "1 hour before" alert when appointment is 50–70 minutes away
  - Sends hourly interval reminders from 8 AM until 1 hour before appointment
  - Uses `last_reminder_hour` on the Appointment model to prevent duplicate
    emails when the script runs multiple times within the same clock hour.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from appointment.models import Appointment
from datetime import timedelta


class Command(BaseCommand):
    help = 'Sends smart, time-aware appointment reminders (run every 30 min)'

    def handle(self, *args, **kwargs):
        now        = timezone.localtime(timezone.now())
        today      = now.date()
        current_hour = now.hour

        self.stdout.write(
            f'\n[{now.strftime("%Y-%m-%d %H:%M:%S")}] Running reminder check '
            f'(current hour: {current_hour:02d}:xx)\n'
        )

        # Fetch all confirmed appointments for TODAY that haven't already been
        # reminded during THIS clock hour.
        appointments = Appointment.objects.filter(
            date=today,
            status='Confirmed',
        ).exclude(
            last_reminder_hour=current_hour,   # skip if already sent this hour
        ).select_related('patient__user', 'doctor')

        if not appointments.exists():
            self.stdout.write(self.style.SUCCESS(
                '  No pending reminders for this hour. All caught up!\n'
            ))
            return

        sent_count   = 0
        skip_count   = 0

        for appt in appointments:
            appt_datetime   = timezone.make_aware(
                timezone.datetime.combine(appt.date, appt.time)
            )
            time_until_appt = appt_datetime - now

            send_now = False
            subject  = ''
            message  = ''

            # ── 1. Fixed early-morning alerts ────────────────────────────────
            if current_hour in [0, 4, 6, 7]:
                # Only send if appointment hasn't passed yet
                if time_until_appt.total_seconds() > 0:
                    send_now = True
                    hour_label = {
                        0: 'Midnight reminder',
                        4: 'Early morning reminder',
                        6: 'Morning reminder',
                        7: 'Morning reminder',
                    }[current_hour]
                    subject = (
                        f'⏰ {hour_label}: Appointment at '
                        f'{appt.time.strftime("%I:%M %p")} — VitalBook'
                    )
                    message = (
                        f'Dear {appt.patient.user.get_full_name() or appt.patient.user.username},\n\n'
                        f'This is your {hour_label.lower()} for your appointment '
                        f'with Dr. {appt.doctor.name} at {appt.time.strftime("%I:%M %p")} today.\n\n'
                        f'Please make sure to arrive on time.\n\n'
                        f'— VitalBook'
                    )

            # ── 2. "1 hour before" alert (50–70 minute window) ───────────────
            if (
                not send_now
                and timedelta(minutes=50) <= time_until_appt <= timedelta(minutes=70)
            ):
                send_now = True
                subject  = (
                    f'🔔 1 Hour Reminder: Your appointment is soon — VitalBook'
                )
                message = (
                    f'Dear {appt.patient.user.get_full_name() or appt.patient.user.username},\n\n'
                    f'Your appointment with Dr. {appt.doctor.name} starts in about '
                    f'1 hour at {appt.time.strftime("%I:%M %p")}.\n\n'
                    f'Please start heading to the clinic now.\n\n'
                    f'— VitalBook'
                )

            # ── 3. Hourly interval reminders (post-7 AM, >1 hour away) ───────
            if (
                not send_now
                and current_hour > 7
                and time_until_appt > timedelta(hours=1)
            ):
                send_now = True
                subject  = (
                    f'📅 Hourly Reminder: Appointment at '
                    f'{appt.time.strftime("%I:%M %p")} — VitalBook'
                )
                message = (
                    f'Dear {appt.patient.user.get_full_name() or appt.patient.user.username},\n\n'
                    f'Hourly reminder: You have an appointment with Dr. {appt.doctor.name} '
                    f'today at {appt.time.strftime("%I:%M %p")}.\n\n'
                    f'Log in to your VitalBook dashboard for details: '
                    f'http://127.0.0.1:8000/patient/dashboard/\n\n'
                    f'— VitalBook'
                )

            # ── 4. Send & update flag ─────────────────────────────────────────
            if send_now:
                patient_email = appt.patient.user.email
                if patient_email:
                    try:
                        send_mail(
                            subject=subject,
                            message=message,
                            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@vitalbook.com'),
                            recipient_list=[patient_email],
                            fail_silently=False,
                        )
                        # Lock this hour — won't send again until next hour
                        appt.last_reminder_hour = current_hour
                        appt.save(update_fields=['last_reminder_hour'])
                        sent_count += 1
                        self.stdout.write(self.style.SUCCESS(
                            f'  ✓ Sent to {patient_email} '
                            f'(appt #{appt.id}, hour={current_hour:02d})'
                        ))
                    except Exception as exc:
                        self.stdout.write(self.style.ERROR(
                            f'  ✗ Failed for {patient_email}: {exc}'
                        ))
                else:
                    self.stdout.write(self.style.WARNING(
                        f'  ⚠ Skipped appt #{appt.id} — patient has no email'
                    ))
                    skip_count += 1
            else:
                skip_count += 1

        # ── Summary ──────────────────────────────────────────────────────────
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'  Done — {sent_count} sent, {skip_count} skipped.\n'
        ))
