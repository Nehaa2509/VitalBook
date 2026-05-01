# Email System Quick Reference

Quick commands and examples for VitalBook email system.

---

## Test Emails in Console

```bash
# Start Django shell
python manage.py shell

# Import modules
from appointment.models import Appointment, Patient, Review, Payment
from appointment import email_utils
from django.contrib.auth.models import User

# Test welcome email
user = User.objects.first()
patient = user.patient
email_utils.send_welcome_email(user, patient)

# Test appointment confirmation
appointment = Appointment.objects.filter(status='Confirmed').first()
email_utils.send_appointment_confirmation(appointment)

# Test payment receipt
payment = Payment.objects.filter(payment_status='Completed').first()
email_utils.send_payment_receipt(payment.appointment, payment)

# Test reminder
email_utils.send_appointment_reminder(appointment)

# Test cancellation
email_utils.send_appointment_cancelled(appointment, cancelled_by='patient')

# Test review thank you
review = Review.objects.first()
email_utils.send_review_thankyou(review)
```

---

## Send Reminders

```bash
# Manual run
python manage.py send_reminders

# Schedule daily (Windows Task Scheduler)
# Program: python
# Arguments: manage.py send_reminders
# Start in: C:\path\to\project
# Trigger: Daily at 9:00 AM
```

---

## Email Triggers

| Event | Function | Triggered From |
|-------|----------|----------------|
| New registration | `send_welcome_email()` | `register()` view |
| Payment completed | `send_appointment_confirmation()` | `process_payment()` view |
| Payment completed | `send_payment_receipt()` | `process_payment()` view |
| Appointment cancelled | `send_appointment_cancelled()` | `cancel_appointment()` view |
| Review submitted | `send_review_thankyou()` | `submit_review()` view |
| 24h before appointment | `send_appointment_reminder()` | `send_reminders` command |

---

## Email Templates Location

```
appointment/templates/emails/
├── base_email.html                    # Base template
├── appointment_confirmation.html      # Booking confirmation
├── payment_receipt.html               # Payment receipt
├── appointment_reminder.html          # 24-hour reminder
├── appointment_cancelled.html         # Patient cancellation
├── doctor_cancellation_notice.html    # Doctor notification
├── review_thankyou.html              # Review thank you
└── welcome_email.html                # New patient welcome
```

---

## Configuration

### Development (Console)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'noreply@vitalbook.in'
```

### Production (SMTP)
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@vitalbook.in'
```

---

## Common Issues

### Emails not appearing in console
- Check that `EMAIL_BACKEND` is set to console backend
- Verify `runserver` is running in terminal
- Check for errors in console output

### Emails not sending in production
- Verify SMTP credentials
- Check firewall/port settings
- Enable "Less secure app access" (Gmail)
- Use app-specific password (Gmail)

### Patient not receiving emails
- Verify patient has email address
- Check patient.user.email is set
- Look for errors in console/logs

---

## Test Script

Run comprehensive tests:

```bash
python manage.py shell < test_email_system.py
```

---

## Email Content

All emails include:
- ✅ Professional VitalBook branding
- 📱 Mobile-responsive design
- 🎨 Gradient blue header
- 📋 Info cards with key details
- 🔘 Call-to-action buttons
- 📞 Contact information in footer

---

## Support

- Email: support@vitalbook.in
- Phone: +91 98765 43210
