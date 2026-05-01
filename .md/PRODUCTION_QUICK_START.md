# Production Quick Start Guide

Fast-track guide to deploy VitalBook to production.

---

## ✅ Settings Updated

```python
DEBUG = False
ALLOWED_HOSTS = ['*']
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

---

## 🚀 Deploy in 5 Steps

### Step 1: Update Configuration (5 min)

Generate new SECRET_KEY:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Update `ALLOWED_HOSTS` in settings.py:
```python
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

---

### Step 2: Collect Static Files (1 min)

```bash
python manage.py collectstatic --noinput
```

---

### Step 3: Run Migrations (1 min)

```bash
python manage.py migrate
python manage.py createsuperuser
```

---

### Step 4: Install Gunicorn (1 min)

```bash
pip install gunicorn
```

---

### Step 5: Start Server (1 min)

```bash
gunicorn hospital_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

---

## 🔒 Security (Optional but Recommended)

Add to settings.py:
```python
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
```

---

## 📧 Email Configuration

Update settings.py:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## 🧪 Test Deployment

1. Visit: http://your-domain:8000
2. Check admin: http://your-domain:8000/admin
3. Test booking flow
4. Test email notifications

---

## 📚 Full Documentation

- **PRODUCTION_DEPLOYMENT.md** - Complete guide
- **PRODUCTION_CHECKLIST.md** - Detailed checklist
- **PRODUCTION_SETTINGS_SUMMARY.md** - Settings details

---

## 🆘 Quick Troubleshooting

**Static files not loading?**
```bash
python manage.py collectstatic --clear --noinput
```

**500 Error?**
```bash
# Check logs
tail -f logs/django.log
```

**Email not working?**
```bash
# Test in shell
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Message', 'from@example.com', ['to@example.com'])
```

---

**Status:** ✅ Ready for Production
**Time to Deploy:** ~10 minutes
