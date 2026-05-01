# Environment Variables Configuration Guide

Complete guide for configuring VitalBook using environment variables.

---

## Overview

VitalBook uses a `.env` file to manage sensitive configuration and environment-specific settings. This keeps secrets out of version control and makes deployment easier.

---

## Files Created

### 1. `.env` (Active Configuration)
- Contains actual secrets and configuration
- **NEVER commit to version control**
- Unique for each environment (dev, staging, production)
- Already added to `.gitignore`

### 2. `.env.example` (Template)
- Template file showing all available variables
- Safe to commit to version control
- Used as reference for setting up new environments

### 3. `.gitignore` (Version Control)
- Ensures `.env` is never committed
- Protects sensitive information

---

## Environment Variables Reference

### Django Core Settings

#### SECRET_KEY
```bash
SECRET_KEY=%qwed-$3gsg7gr-rv--)oml!*n0ph89scm9=+y)c8$kd$tnboq
```
- **Purpose:** Cryptographic signing key for Django
- **Required:** Yes
- **Security:** Keep secret, never share
- **Generate new:** `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

#### DEBUG
```bash
DEBUG=False
```
- **Purpose:** Enable/disable debug mode
- **Values:** `True` or `False`
- **Development:** `True`
- **Production:** `False` (ALWAYS)
- **Impact:** Shows detailed error pages when True

#### ALLOWED_HOSTS
```bash
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```
- **Purpose:** Domains allowed to serve the application
- **Format:** Comma-separated list
- **Development:** `localhost,127.0.0.1`
- **Production:** Your actual domain names
- **Example:** `vitalbook.com,www.vitalbook.com,123.456.789.0`

---

### Database Configuration

#### DATABASE_URL
```bash
# SQLite (Development)
DATABASE_URL=sqlite:///db.sqlite3

# PostgreSQL (Production)
DATABASE_URL=postgresql://username:password@localhost:5432/vitalbook

# MySQL (Production)
DATABASE_URL=mysql://username:password@localhost:3306/vitalbook
```
- **Purpose:** Database connection string
- **Format:** `protocol://user:password@host:port/database`
- **Development:** SQLite (file-based)
- **Production:** PostgreSQL or MySQL (recommended)

**PostgreSQL Example:**
```bash
DATABASE_URL=postgresql://vitalbook_user:secure_password@localhost:5432/vitalbook_db
```

**MySQL Example:**
```bash
DATABASE_URL=mysql://vitalbook_user:secure_password@localhost:3306/vitalbook_db
```

---

### Email Configuration

#### EMAIL_BACKEND
```bash
# Console (Development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# SMTP (Production)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```
- **Purpose:** Email sending method
- **Development:** Console (prints to terminal)
- **Production:** SMTP (sends real emails)

#### EMAIL_HOST
```bash
EMAIL_HOST=smtp.gmail.com
```
- **Purpose:** SMTP server address
- **Gmail:** `smtp.gmail.com`
- **Outlook:** `smtp-mail.outlook.com`
- **SendGrid:** `smtp.sendgrid.net`
- **AWS SES:** `email-smtp.region.amazonaws.com`

#### EMAIL_PORT
```bash
EMAIL_PORT=587
```
- **Purpose:** SMTP server port
- **TLS:** `587` (recommended)
- **SSL:** `465`
- **Unencrypted:** `25` (not recommended)

#### EMAIL_USE_TLS
```bash
EMAIL_USE_TLS=True
```
- **Purpose:** Enable TLS encryption
- **Values:** `True` or `False`
- **Recommended:** `True` for security

#### EMAIL_HOST_USER
```bash
EMAIL_HOST_USER=your-email@gmail.com
```
- **Purpose:** SMTP authentication username
- **Gmail:** Your Gmail address
- **Other:** Provided by email service

#### EMAIL_HOST_PASSWORD
```bash
EMAIL_HOST_PASSWORD=your-app-password
```
- **Purpose:** SMTP authentication password
- **Gmail:** Use App Password (not regular password)
- **Security:** Keep secret, never share
- **Generate Gmail App Password:**
  1. Enable 2-factor authentication
  2. Go to Google Account → Security → App Passwords
  3. Generate password for "Mail"

#### DEFAULT_FROM_EMAIL
```bash
DEFAULT_FROM_EMAIL=noreply@vitalbook.in
```
- **Purpose:** Default sender email address
- **Format:** `name@domain.com`
- **Best Practice:** Use no-reply address

---

### Time Zone

#### TIME_ZONE
```bash
TIME_ZONE=Asia/Kolkata
```
- **Purpose:** Application time zone
- **Format:** IANA time zone name
- **India:** `Asia/Kolkata`
- **US Eastern:** `America/New_York`
- **UK:** `Europe/London`
- **List:** https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

---

### Security Settings (Production)

#### SECURE_SSL_REDIRECT
```bash
SECURE_SSL_REDIRECT=True
```
- **Purpose:** Redirect HTTP to HTTPS
- **Development:** `False`
- **Production:** `True` (if HTTPS enabled)

#### SESSION_COOKIE_SECURE
```bash
SESSION_COOKIE_SECURE=True
```
- **Purpose:** Send session cookies only over HTTPS
- **Development:** `False`
- **Production:** `True` (if HTTPS enabled)

#### CSRF_COOKIE_SECURE
```bash
CSRF_COOKIE_SECURE=True
```
- **Purpose:** Send CSRF cookies only over HTTPS
- **Development:** `False`
- **Production:** `True` (if HTTPS enabled)

---

### CORS Configuration

#### CORS_ALLOW_ALL_ORIGINS
```bash
CORS_ALLOW_ALL_ORIGINS=True
```
- **Purpose:** Allow all origins for API access
- **Development:** `True`
- **Production:** `False` (use specific origins)

#### CORS_ALLOWED_ORIGINS
```bash
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```
- **Purpose:** Specific allowed origins
- **Format:** Comma-separated URLs
- **Use when:** CORS_ALLOW_ALL_ORIGINS=False

---

## Environment-Specific Configurations

### Development (.env)
```bash
SECRET_KEY=dev-secret-key-not-for-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
CORS_ALLOW_ALL_ORIGINS=True
```

### Production (.env)
```bash
SECRET_KEY=%qwed-$3gsg7gr-rv--)oml!*n0ph89scm9=+y)c8$kd$tnboq
DEBUG=False
ALLOWED_HOSTS=vitalbook.com,www.vitalbook.com
DATABASE_URL=postgresql://user:pass@localhost:5432/vitalbook
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@vitalbook.com
EMAIL_HOST_PASSWORD=your-app-password
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://vitalbook.com,https://www.vitalbook.com
```

---

## Setup Instructions

### 1. Initial Setup

Copy the example file:
```bash
cp .env.example .env
```

### 2. Generate SECRET_KEY

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste into `.env`:
```bash
SECRET_KEY=your-generated-key-here
```

### 3. Configure Database

For development (SQLite):
```bash
DATABASE_URL=sqlite:///db.sqlite3
```

For production (PostgreSQL):
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/vitalbook
```

### 4. Configure Email

For development (console):
```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

For production (Gmail):
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 5. Update ALLOWED_HOSTS

Development:
```bash
ALLOWED_HOSTS=localhost,127.0.0.1
```

Production:
```bash
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com,server-ip
```

---

## Testing Configuration

### Test Environment Variables

```bash
python manage.py shell
```

```python
from django.conf import settings

# Check DEBUG
print(f"DEBUG: {settings.DEBUG}")

# Check SECRET_KEY (first 10 chars only)
print(f"SECRET_KEY: {settings.SECRET_KEY[:10]}...")

# Check ALLOWED_HOSTS
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")

# Check EMAIL_BACKEND
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")

# Check DATABASE
print(f"DATABASE: {settings.DATABASES['default']['ENGINE']}")
```

### Test Email Configuration

```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test message.',
    'noreply@vitalbook.in',
    ['test@example.com'],
    fail_silently=False,
)
```

---

## Security Best Practices

### 1. Never Commit .env
- Always in `.gitignore`
- Never share publicly
- Never commit to version control

### 2. Use Strong SECRET_KEY
- Generate new for each environment
- Minimum 50 characters
- Random and unpredictable

### 3. Rotate Secrets Regularly
- Change SECRET_KEY periodically
- Update email passwords
- Rotate database credentials

### 4. Use Environment-Specific Files
- `.env.development`
- `.env.staging`
- `.env.production`

### 5. Secure File Permissions
```bash
chmod 600 .env
```

### 6. Use Secret Management (Production)
- AWS Secrets Manager
- Azure Key Vault
- HashiCorp Vault
- Google Secret Manager

---

## Troubleshooting

### .env not loading

**Check:**
1. File is named `.env` (not `env` or `.env.txt`)
2. File is in project root (same directory as `manage.py`)
3. `python-dotenv` is installed: `pip install python-dotenv`
4. Settings.py has `load_dotenv()` call

**Fix:**
```bash
pip install python-dotenv
```

### Variables not updating

**Solution:**
Restart Django server after changing `.env`:
```bash
# Stop server (Ctrl+C)
# Start again
python manage.py runserver
```

### Email not working

**Check:**
1. EMAIL_BACKEND is set to SMTP
2. EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are correct
3. For Gmail, use App Password (not regular password)
4. EMAIL_USE_TLS is True
5. Port is 587 (for TLS)

### Database connection error

**Check:**
1. DATABASE_URL format is correct
2. Database server is running
3. Credentials are correct
4. Database exists
5. User has permissions

---

## Platform-Specific Configuration

### Heroku

Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=yourapp.herokuapp.com
```

### Railway

Add environment variables in dashboard or `railway.json`:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn hospital_project.wsgi:application",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

### DigitalOcean App Platform

Add environment variables in app settings or `.env` file.

### AWS Elastic Beanstalk

Use `.ebextensions/environment.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    SECRET_KEY: your-secret-key
    DEBUG: False
```

---

## Backup and Recovery

### Backup .env

```bash
# Encrypt and backup
gpg -c .env
# Creates .env.gpg (encrypted)
```

### Restore .env

```bash
# Decrypt
gpg .env.gpg
# Enter passphrase
```

---

## Support

For configuration issues:
- Email: support@vitalbook.in
- Phone: +91 98765 43210

---

**Status:** ✅ Environment Configuration Complete
**Files Created:**
- `.env` (active configuration)
- `.env.example` (template)
- `.gitignore` (version control)
- `ENV_CONFIGURATION_GUIDE.md` (this file)

**Last Updated:** April 3, 2026
