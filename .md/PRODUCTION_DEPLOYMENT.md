# VitalBook - Production Deployment Guide

Complete guide for deploying VitalBook to production.

---

## Production Settings Applied

### settings.py Changes

```python
# Debug mode disabled for security
DEBUG = False

# Allow all hosts (configure specific domains in production)
ALLOWED_HOSTS = ['*']

# Static files configuration
STATIC_ROOT = BASE_DIR / 'staticfiles'
```

---

## Pre-Deployment Checklist

### 1. Security Settings

- [x] `DEBUG = False` - Debug mode disabled
- [ ] Update `SECRET_KEY` - Generate new secret key for production
- [ ] Configure `ALLOWED_HOSTS` - Set specific domain names
- [ ] Enable HTTPS - Configure SSL/TLS certificates
- [ ] Set secure cookies - Add security middleware settings

### 2. Database

- [ ] Migrate to production database (PostgreSQL/MySQL recommended)
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Backup database regularly

### 3. Static Files

- [x] `STATIC_ROOT` configured
- [x] WhiteNoise middleware enabled
- [ ] Collect static files: `python manage.py collectstatic`
- [ ] Verify static files are served correctly

### 4. Email Configuration

- [ ] Configure SMTP settings (replace console backend)
- [ ] Test email delivery
- [ ] Set up email monitoring

### 5. Environment Variables

- [ ] Create `.env` file for sensitive data
- [ ] Set `SECRET_KEY` in environment
- [ ] Set `DATABASE_URL` in environment
- [ ] Set `EMAIL_HOST_PASSWORD` in environment

---

## Deployment Steps

### Step 1: Update SECRET_KEY

Generate a new secret key for production:

```python
# In Python shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

Update settings.py:
```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-new-secret-key-here')
```

Or use environment variable:
```bash
# In .env file
SECRET_KEY=your-new-secret-key-here
```

---

### Step 2: Configure ALLOWED_HOSTS

Update settings.py with your domain:

```python
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    'your-server-ip',
]
```

Or use environment variable:
```bash
# In .env file
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

---

### Step 3: Collect Static Files

Run the collectstatic command:

```bash
python manage.py collectstatic --noinput
```

This will:
- Copy all static files to `staticfiles/` directory
- Compress files using WhiteNoise
- Prepare files for production serving

---

### Step 4: Configure Database (Optional)

For production, use PostgreSQL or MySQL instead of SQLite.

#### PostgreSQL Configuration

Install psycopg2:
```bash
pip install psycopg2-binary
```

Update settings.py:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'vitalbook'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

Or use DATABASE_URL:
```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600
    )
}
```

---

### Step 5: Configure Email (SMTP)

Update settings.py for production email:

```python
# Replace console backend with SMTP
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = 'noreply@vitalbook.in'
```

Environment variables:
```bash
# In .env file
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

### Step 6: Security Settings

Add these security settings to settings.py:

```python
# Security settings for production
if not DEBUG:
    # HTTPS settings
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    
    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Other security settings
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
```

---

### Step 7: Run Migrations

Apply all database migrations:

```bash
python manage.py migrate
```

---

### Step 8: Create Superuser

Create an admin account:

```bash
python manage.py createsuperuser
```

Follow the prompts to set:
- Username
- Email
- Password

---

### Step 9: Test the Application

Start the server:

```bash
python manage.py runserver 0.0.0.0:8000
```

Test:
- [ ] Homepage loads
- [ ] Static files load (CSS, JS, images)
- [ ] Admin panel accessible
- [ ] User registration works
- [ ] Login/logout works
- [ ] Appointment booking works
- [ ] Email notifications work
- [ ] Payment processing works

---

## Production Server Options

### Option 1: Gunicorn (Recommended)

Install Gunicorn:
```bash
pip install gunicorn
```

Run with Gunicorn:
```bash
gunicorn hospital_project.wsgi:application --bind 0.0.0.0:8000
```

With workers:
```bash
gunicorn hospital_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120
```

---

### Option 2: uWSGI

Install uWSGI:
```bash
pip install uwsgi
```

Run with uWSGI:
```bash
uwsgi --http :8000 --module hospital_project.wsgi
```

---

### Option 3: Nginx + Gunicorn

1. Install Nginx
2. Configure Nginx as reverse proxy
3. Run Gunicorn as application server

Nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/vitalbook/staticfiles/;
    }

    location /media/ {
        alias /path/to/vitalbook/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Environment Variables (.env file)

Create a `.env` file in project root:

```bash
# Django settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (if using PostgreSQL)
DB_NAME=vitalbook
DB_USER=postgres
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Other settings
TIME_ZONE=Asia/Kolkata
```

---

## Deployment Platforms

### Option 1: Heroku

1. Install Heroku CLI
2. Create `Procfile`:
```
web: gunicorn hospital_project.wsgi
```

3. Create `runtime.txt`:
```
python-3.13.0
```

4. Deploy:
```bash
heroku create vitalbook
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

---

### Option 2: DigitalOcean

1. Create a Droplet (Ubuntu 22.04)
2. Install Python, PostgreSQL, Nginx
3. Clone repository
4. Set up virtual environment
5. Configure Nginx
6. Set up Gunicorn as systemd service
7. Enable SSL with Let's Encrypt

---

### Option 3: AWS EC2

1. Launch EC2 instance
2. Configure security groups
3. Install dependencies
4. Set up RDS for database
5. Configure S3 for static files
6. Set up Load Balancer
7. Enable CloudFront CDN

---

### Option 4: Railway

1. Connect GitHub repository
2. Configure environment variables
3. Deploy automatically on push

---

### Option 5: Render

1. Connect GitHub repository
2. Configure build command:
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

3. Configure start command:
```bash
gunicorn hospital_project.wsgi:application
```

---

## SSL/HTTPS Configuration

### Option 1: Let's Encrypt (Free)

Install Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
```

Get certificate:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

Auto-renewal:
```bash
sudo certbot renew --dry-run
```

---

### Option 2: Cloudflare (Free)

1. Add domain to Cloudflare
2. Update nameservers
3. Enable SSL/TLS (Full mode)
4. Enable automatic HTTPS rewrites

---

## Monitoring & Logging

### Application Monitoring

Install Sentry:
```bash
pip install sentry-sdk
```

Configure in settings.py:
```python
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
)
```

---

### Server Monitoring

Options:
- New Relic
- Datadog
- Prometheus + Grafana
- AWS CloudWatch

---

### Logging Configuration

Add to settings.py:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
```

---

## Backup Strategy

### Database Backup

Daily backup script:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
python manage.py dumpdata > backup_$DATE.json
```

Or for PostgreSQL:
```bash
pg_dump vitalbook > backup_$DATE.sql
```

---

### Media Files Backup

Sync to S3:
```bash
aws s3 sync media/ s3://vitalbook-media/
```

---

## Performance Optimization

### 1. Enable Caching

Install Redis:
```bash
pip install django-redis
```

Configure in settings.py:
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

### 2. Database Optimization

- Add database indexes
- Use select_related() and prefetch_related()
- Enable connection pooling
- Configure query optimization

---

### 3. CDN for Static Files

Use Cloudflare, AWS CloudFront, or similar for:
- Static files (CSS, JS)
- Media files (images, PDFs)
- Faster global delivery

---

## Maintenance

### Regular Tasks

- [ ] Update dependencies monthly
- [ ] Review security advisories
- [ ] Monitor error logs
- [ ] Check disk space
- [ ] Backup database daily
- [ ] Test email delivery
- [ ] Review user feedback
- [ ] Update documentation

---

## Troubleshooting

### Static files not loading
```bash
python manage.py collectstatic --clear --noinput
```

### Database connection errors
- Check database credentials
- Verify database is running
- Check firewall rules

### Email not sending
- Verify SMTP credentials
- Check email provider settings
- Test with console backend first

### 500 Internal Server Error
- Check error logs
- Enable DEBUG temporarily
- Review recent code changes

---

## Support

For deployment issues:
- Email: support@vitalbook.in
- Phone: +91 98765 43210

---

**Status:** Ready for Production
**Last Updated:** April 3, 2026
**Version:** 1.0
