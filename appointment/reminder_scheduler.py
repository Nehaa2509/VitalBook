import threading
import time
from datetime import datetime, date
import pytz

def schedule_same_day_reminders(appointment):
    """
    When appointment is booked TODAY,
    send reminder every 1 hour until 1 hour before appointment.
    Runs in a background thread.
    """
    from .email_utils import send_reminder_email

    IST = pytz.timezone('Asia/Kolkata')

    while True:
        try:
            now = datetime.now(IST)
            today = now.date()

            # Stop if appointment date has passed
            if appointment.date < today:
                print(f'Appointment VB-{appointment.id} date passed. Stopping reminders.')
                break

            # Combine appointment date and time
            appt_datetime = IST.localize(
                datetime.combine(appointment.date, appointment.time)
            )

            # Calculate minutes left
            minutes_left = (appt_datetime - now).total_seconds() / 60
            hours_left = minutes_left / 60

            # Stop if less than 1 hour left (final reminder already sent)
            if minutes_left <= 60:
                print(f'Less than 1 hour left for VB-{appointment.id}. Stopping hourly reminders.')
                break

            # Stop if appointment already passed
            if minutes_left <= 0:
                print(f'Appointment VB-{appointment.id} has passed.')
                break

            # Send hourly reminder
            label = f'Hourly Reminder — {round(hours_left, 1)} Hours Before'
            send_reminder_email(
                appointment=appointment,
                reminder_label=label,
                hours_left=round(hours_left, 1),
                is_final=False,
            )
            print(f'✅ Hourly reminder sent for VB-{appointment.id} — {round(hours_left, 1)}hrs left')

            # Wait 1 hour before sending next reminder
            time.sleep(3600)  # 3600 seconds = 1 hour

        except Exception as e:
            print(f'❌ Reminder scheduler error: {e}')
            break


def send_final_one_hour_reminder(appointment):
    """
    Send the FINAL reminder exactly 1 hour before appointment.
    Call this from the hourly scheduler or management command.
    """
    from .email_utils import send_reminder_email

    send_reminder_email(
        appointment=appointment,
        reminder_label='⚡ Final Reminder — 1 Hour Before Your Appointment!',
        hours_left=1.0,
        is_final=True,
    )
    print(f'⚡ Final 1-hour reminder sent for VB-{appointment.id}')
