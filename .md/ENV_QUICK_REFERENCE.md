# Environment Variables Quick Reference

Fast reference for VitalBook environment configuration.

---

## 📁 Files

- `.env` - Active configuration (DO NOT COMMIT)
- `.env.example` - Template (safe to commit)
- `.gitignore` - Protects .env from version control

---

## 🔑 Essential Variables

### Django Core
```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
```

### Database
```bash
# Development
DATABASE_URL=sqlite:///db.sqlite3

# Production
DATABASE_URL=postgresql://user:pass@localhost:5432/vitalbook
```

### Email
```bash
# Development
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Production
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 🚀 Quick Setup

### 1. Copy Template
```bash
cp .env.example .env
```

### 2. Generate SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Edit .env
Update with your values

### 4. Test
```bash
python manage.py runserver
```

---

## 🔒 Security Checklist

- [x] .env in .gitignore
- [ ] SECRET_KEY is unique
- [ ] DEBUG=False in production
- [ ] ALLOWED_HOSTS configured
- [ ] Email password is App Password (Gmail)
- [ ] File permissions: `chmod 600 .env`

---

## 🧪 Test Configuration

```bash
python manage.py shell
```

```python
from django.conf import settings
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
```

---

## 🌍 Environment Presets

### Development
```bash
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Production
```bash
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

---

## 🆘 Common Issues

### .env not loading
```bash
pip install python-dotenv
# Restart server
```

### Email not working
- Use Gmail App Password (not regular password)
- Enable 2FA first
- Generate at: https://myaccount.google.com/apppasswords

### Variables not updating
- Restart Django server after changes

---

## 📚 Full Documentation

See `ENV_CONFIGURATION_GUIDE.md` for complete details.

---

**Quick Start:** Copy `.env.example` to `.env`, generate SECRET_KEY, update values, restart server.
