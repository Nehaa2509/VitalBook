# VitalBook Email Notification System

Complete guide to the email notification system implemented in VitalBook.

---

## Overview

VitalBook sends professional HTML emails for all key events:
- ✅ Appointment confirmation
- 💳 Payment receipt
- ⏰ 24-hour appointment reminder
- ❌ Appointment cancellation (to patient & doctor)
- ⭐ Review thank you
- 👋 Welcome email for new patients

---

## Email Configuration

### Settings (hospital_project/settings.py)

```python
# Email configuration (console backend for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@vitalbook.in'
```

### For Production

Replace with SMTP settings:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # or your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@vitalbook.in'
```

---

## Email Templates

All email templates extend `emails/base_email.html` which provides:
- Professional gradient blue header with VitalBook branding
- Responsive design (mobile-friendly)
- Consistent styling (info cards, buttons, badges)
- Footer with contact information

### Template Files

1. **base_email.html** - Base template with header, footer, and styling
2. **appointment_confirmation.html** - Booking confirmation
3. **payment_receipt.html** - Payment receipt with transaction details
4. **appointment_reminder.html** - 24-hour reminder with preparation tips
5. **appointment_cancelled.html** - Cancellation notice to patient
6. **doctor_cancellation_notice.html** - Cancellation notice to doctor
7. **review_thankyou.html** - Thank you after review submission
8. **welcome_email.html** - Welcome message for new patients

---

## Email Functions

All email functions are in `appointment/email_utils.py`:

### 1. send_appointment_confirmation(appointment)
**When:** After successful payment
**To:** Patient
**Contains:** Doctor details, date, time, booking ID, consultation fee

### 2. send_payment_receipt(appointment, payment)
**When:** After successful payment
**To:** Patient
**Contains:** Transaction ID, amount, payment method, PDF download link

### 3. send_appointment_reminder(appointment)
**When:** 24 hours before appointment (via management command)
**To:** Patient
**Contains:** Appointment details, preparation tips, doctor contact

### 4. send_appointment_cancelled(appointment, cancelled_by='patient')
**When:** Patient cancels appointment
**To:** Patient AND Doctor
**Contains:** Cancellation details, cancellation fee (if applicable)

### 5. send_review_thankyou(review)
**When:** Patient submits a review
**To:** Patient
**Contains:** Review details, rating, link to doctor's reviews

### 6. send_welcome_email(user, patient)
**When:** New patient registration
**To:** Patient
**Contains:** Account details, getting started tips

---

## Integration Points

### Views Integration

#### 1. Registration (register view)
```python
# After creating user and patient
email_utils.send_welcome_email(user, patient)
```

#### 2. Payment Processing (process_payment view)
```python
# After successful payment
email_utils.send_appointment_confirmation(appointment)
email_utils.send_payment_receipt(appointment, payment)
```

#### 3. Appointment Cancellation (cancel_appointment view)
```python
# After cancelling appointment
email_utils.send_appointment_cancelled(appointment, cancelled_by='patient')
```

#### 4. Review Submission (submit_review view)
```python
# After creating review
email_utils.send_review_thankyou(review)
```

---

## Appointment Reminders

### Management Command

Run daily to send 24-hour reminders:

```bash
python manage.py send_reminders
```

### Automated Scheduling

#### Option 1: Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 9:00 AM
4. Action: Start a program
5. Program: `python`
6. Arguments: `manage.py send_reminders`
7. Start in: `C:\path\to\your\project`

#### Option 2: Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 9 AM)
0 9 * * * cd /path/to/project && python manage.py send_reminders
```

#### Option 3: Django-Cron (Cross-platform)

Install:
```bash
pip install django-cron
```

Add to INSTALLED_APPS:
```python
INSTALLED_APPS = [
    ...
    'django_cron',
]
```

Create cron job class:
```python
# appointment/cron.py
from django_cron import CronJobBase, Schedule
from appointment import email_utils
from appointment.models import Appointment
from django.utils import timezone
from datetime import timedelta

class SendRemindersCronJob(CronJobBase):
    RUN_EVERY_MINS = 1440  # Run once per day
    
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'appointment.send_reminders'
    
    def do(self):
        tomorrow = timezone.now().date() + timedelta(days=1)
        appointments = Appointment.objects.filter(
            date=tomorrow,
            status='Confirmed'
        )
        for appointment in appointments:
            email_utils.send_appointment_reminder(appointment)
```

Add to settings:
```python
CRON_CLASSES = [
    'appointment.cron.SendRemindersCronJob',
]
```

Run:
```bash
python manage.py runcrons
```

---

## Testing Emails

### Console Backend (Development)

Emails are printed to console. Check your terminal where `python manage.py runserver` is running.

### Test Individual Functions

```python
# In Django shell
python manage.py shell

from appointment.models import Appointment, Patient, Review
from appointment import email_utils
from django.contrib.auth.models import User

# Test welcome email
user = User.objects.first()
patient = user.patient
email_utils.send_welcome_email(user, patient)

# Test appointment confirmation
appointment = Appointment.objects.first()
email_utils.send_appointment_confirmation(appointment)

# Test payment receipt
payment = appointment.payments.first()
email_utils.send_payment_receipt(appointment, payment)

# Test reminder
email_utils.send_appointment_reminder(appointment)

# Test cancellation
email_utils.send_appointment_cancelled(appointment, cancelled_by='patient')

# Test review thank you
review = Review.objects.first()
email_utils.send_review_thankyou(review)
```

### Test Management Command

```bash
# Send reminders for tomorrow's appointments
python manage.py send_reminders
```

---

## Email Design Features

### Professional Styling
- Gradient blue header (#0d6efd to #0056b3)
- Clean white background
- Rounded corners and shadows
- Responsive design

### Info Cards
- Organized key-value pairs
- Color-coded status badges
- Highlighted important information

### Call-to-Action Buttons
- Blue gradient buttons
- Clear action text
- Direct links to relevant pages

### Status Badges
- ✅ Confirmed (green)
- ❌ Cancelled (red)
- 💳 Paid (green)

### Highlight Boxes
- Important notes (yellow)
- Success messages (green)
- Information (blue)

---

## Customization

### Change Brand Colors

Edit `emails/base_email.html`:

```css
.email-header {
    background: linear-gradient(135deg, #YOUR_COLOR_1, #YOUR_COLOR_2);
}

.btn {
    background: #YOUR_BUTTON_COLOR;
}
```

### Change Email Domain

Edit `hospital_project/settings.py`:

```python
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'
```

Update footer in `emails/base_email.html`:

```html
<p>Need help? Contact us at <a href="mailto:support@yourdomain.com">support@yourdomain.com</a></p>
```

### Add Logo Image

Add to email header in `base_email.html`:

```html
<div class="email-header">
    <img src="https://yourdomain.com/logo.png" alt="VitalBook" style="max-width: 150px; margin-bottom: 16px;">
    <h1>💊 VitalBook</h1>
    <p>Your Health, Our Priority</p>
</div>
```

---

## Error Handling

All email functions use `fail_silently=True` to prevent email errors from breaking the application flow.

Errors are logged to console:
```python
except Exception as e:
    print(f"Error sending email: {e}")
    return False
```

---

## Production Checklist

- [ ] Configure SMTP settings in settings.py
- [ ] Update DEFAULT_FROM_EMAIL to your domain
- [ ] Test all email templates
- [ ] Set up automated reminder scheduling
- [ ] Add logo images (if desired)
- [ ] Update contact information in footer
- [ ] Test email deliverability
- [ ] Configure SPF/DKIM records for your domain
- [ ] Monitor email sending logs
- [ ] Set up email bounce handling

---

## Troubleshooting

### Emails not sending

1. Check EMAIL_BACKEND setting
2. Verify SMTP credentials (if using SMTP)
3. Check console output for errors
4. Ensure patient has valid email address
5. Check spam folder

### Emails look broken

1. Test in multiple email clients
2. Validate HTML structure
3. Check inline CSS
4. Test responsive design on mobile

### Reminders not working

1. Verify management command runs successfully
2. Check appointment status is 'Confirmed'
3. Verify appointment date is tomorrow
4. Check patient email addresses
5. Review cron job/task scheduler logs

---

## Support

For issues or questions:
- Email: support@vitalbook.in
- Phone: +91 98765 43210

---

**Last Updated:** April 3, 2026
**Version:** 1.0
