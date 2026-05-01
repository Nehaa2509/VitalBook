# Production Deployment Checklist

Quick checklist for deploying VitalBook to production.

---

## ✅ Settings Configuration

- [x] `DEBUG = False` - Debug mode disabled
- [x] `ALLOWED_HOSTS = ['*']` - Configured (update with specific domains)
- [x] `STATIC_ROOT = BASE_DIR / 'staticfiles'` - Static files path set
- [ ] `SECRET_KEY` - Generate new secret key for production
- [ ] `ALLOWED_HOSTS` - Update with specific domain names
- [ ] Security settings - Add HTTPS and security headers

---

## ✅ Database

- [ ] Migrate to production database (PostgreSQL/MySQL)
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Set up database backups
- [ ] Configure connection pooling

---

## ✅ Static Files

- [x] WhiteNoise middleware enabled
- [x] STATIC_ROOT configured
- [ ] Run: `python manage.py collectstatic`
- [ ] Verify static files are accessible
- [ ] Consider CDN for better performance

---

## ✅ Email Configuration

- [x] Email utility functions implemented
- [ ] Configure SMTP settings (replace console backend)
- [ ] Set EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
- [ ] Test email delivery
- [ ] Set up email monitoring

---

## ✅ Security

- [ ] Generate new SECRET_KEY
- [ ] Enable HTTPS (SSL/TLS certificates)
- [ ] Set SECURE_SSL_REDIRECT = True
- [ ] Set SESSION_COOKIE_SECURE = True
- [ ] Set CSRF_COOKIE_SECURE = True
- [ ] Enable HSTS headers
- [ ] Configure CORS properly
- [ ] Review ALLOWED_HOSTS

---

## ✅ Environment Variables

Create `.env` file with:
- [ ] SECRET_KEY
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS
- [ ] DATABASE_URL (if using PostgreSQL)
- [ ] EMAIL_HOST_USER
- [ ] EMAIL_HOST_PASSWORD

---

## ✅ Dependencies

- [ ] Update requirements.txt
- [ ] Install production dependencies
- [ ] Install Gunicorn or uWSGI
- [ ] Install database driver (psycopg2 for PostgreSQL)

---

## ✅ Server Setup

- [ ] Choose hosting platform (Heroku, DigitalOcean, AWS, etc.)
- [ ] Set up server/instance
- [ ] Install Python 3.13
- [ ] Install PostgreSQL/MySQL
- [ ] Install Nginx (if applicable)
- [ ] Configure firewall

---

## ✅ Application Deployment

- [ ] Clone repository
- [ ] Create virtual environment
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Set environment variables
- [ ] Run migrations
- [ ] Collect static files
- [ ] Create superuser
- [ ] Test application

---

## ✅ Web Server

- [ ] Install Gunicorn: `pip install gunicorn`
- [ ] Test Gunicorn: `gunicorn hospital_project.wsgi:application`
- [ ] Configure Nginx as reverse proxy (optional)
- [ ] Set up systemd service for auto-start
- [ ] Configure SSL/HTTPS

---

## ✅ Monitoring & Logging

- [ ] Set up error logging
- [ ] Configure Sentry or similar (optional)
- [ ] Set up server monitoring
- [ ] Configure log rotation
- [ ] Set up uptime monitoring

---

## ✅ Backup & Recovery

- [ ] Set up automated database backups
- [ ] Set up media files backup
- [ ] Test backup restoration
- [ ] Document recovery procedures

---

## ✅ Performance

- [ ] Enable caching (Redis recommended)
- [ ] Configure CDN for static files
- [ ] Optimize database queries
- [ ] Enable gzip compression
- [ ] Configure connection pooling

---

## ✅ Testing

- [ ] Test homepage loads
- [ ] Test static files load (CSS, JS, images)
- [ ] Test admin panel access
- [ ] Test user registration
- [ ] Test login/logout
- [ ] Test appointment booking
- [ ] Test payment processing
- [ ] Test email notifications
- [ ] Test all user roles (admin, doctor, patient)
- [ ] Test on different browsers
- [ ] Test on mobile devices

---

## ✅ DNS & Domain

- [ ] Purchase domain name
- [ ] Configure DNS records
- [ ] Point domain to server IP
- [ ] Set up www subdomain
- [ ] Configure SSL certificate

---

## ✅ Final Steps

- [ ] Review all settings
- [ ] Test all functionality
- [ ] Load test application
- [ ] Set up monitoring alerts
- [ ] Document deployment process
- [ ] Train team on maintenance
- [ ] Announce launch

---

## Quick Commands

### Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Run Migrations
```bash
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Run with Gunicorn
```bash
gunicorn hospital_project.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

### Test Email
```bash
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Test message', 'noreply@vitalbook.in', ['test@example.com'])
```

---

## Environment Variables Template

Create `.env` file:

```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL)
DB_NAME=vitalbook
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Other
TIME_ZONE=Asia/Kolkata
```

---

## Security Settings to Add

Add to `settings.py` when `DEBUG = False`:

```python
# HTTPS settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HSTS settings
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Other security
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
```

---

## Common Issues

### Static files not loading
```bash
python manage.py collectstatic --clear --noinput
```

### Database connection error
- Check credentials in .env
- Verify database is running
- Check firewall rules

### 500 Internal Server Error
- Check error logs
- Verify all migrations applied
- Check file permissions

### Email not sending
- Verify SMTP credentials
- Check email provider settings
- Test with console backend first

---

**Status:** Ready for Production
**Current Settings:**
- DEBUG = False ✅
- ALLOWED_HOSTS = ['*'] ✅ (update with specific domains)
- STATIC_ROOT = BASE_DIR / 'staticfiles' ✅

**Next Steps:**
1. Generate new SECRET_KEY
2. Update ALLOWED_HOSTS with your domain
3. Run collectstatic
4. Configure email SMTP
5. Deploy to server
