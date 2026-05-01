# Railway Deployment Guide for VitalBook

Complete guide for deploying VitalBook to Railway.

---

## ✅ Deployment Files Created

### 1. Procfile
```
web: gunicorn hospital_project.wsgi:application
```
- **Purpose:** Tells Railway how to start the application
- **Location:** Root directory (same as manage.py)
- **Required:** Yes

### 2. runtime.txt
```
python-3.13.0
```
- **Purpose:** Specifies Python version
- **Location:** Root directory
- **Required:** Recommended

### 3. railway.json
```json
{
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "pip install -r requirements.txt && python manage.py collectstatic --noinput"
  },
  "deploy": {
    "startCommand": "gunicorn hospital_project.wsgi:application --bind 0.0.0.0:$PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```
- **Purpose:** Railway-specific configuration
- **Location:** Root directory
- **Required:** Optional but recommended

### 4. requirements.txt (Updated)
Added:
- `gunicorn==23.0.0` - Production WSGI server
- `whitenoise==6.8.2` - Static file serving
- `django-filter==24.3` - API filtering
- `qrcode==8.0` - QR code generation
- `reportlab==4.0.7` - PDF generation

---

## 🚀 Deployment Steps

### Step 1: Connect to Railway

1. Go to [Railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your VitalBook repository

### Step 2: Configure Environment Variables

Add these in Railway dashboard:

```bash
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app
DATABASE_URL=postgresql://... (Railway provides this)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Step 3: Deploy

Railway will automatically:
1. Detect the Procfile
2. Install dependencies from requirements.txt
3. Run collectstatic
4. Start the application with gunicorn

### Step 4: Run Migrations

In Railway dashboard:
1. Go to your project
2. Click on the service
3. Go to "Settings" → "Deploy"
4. Add a one-time command:
   ```bash
   python manage.py migrate
   ```

Or use Railway CLI:
```bash
railway run python manage.py migrate
```

### Step 5: Create Superuser

Use Railway CLI:
```bash
railway run python manage.py createsuperuser
```

Or use Railway shell:
1. Go to service settings
2. Click "Shell"
3. Run: `python manage.py createsuperuser`

---

## 🔧 Configuration Details

### Gunicorn Configuration

The Procfile uses basic gunicorn configuration. For production, you can customize:

```
web: gunicorn hospital_project.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --timeout 120
```

**Options:**
- `--workers 3` - Number of worker processes (2-4 x CPU cores)
- `--timeout 120` - Request timeout in seconds
- `--log-level info` - Logging level

### Static Files

WhiteNoise is configured in settings.py:
```python
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
```

This automatically:
- Serves static files
- Compresses files
- Adds cache headers

### Database

Railway provides PostgreSQL:
1. Add PostgreSQL plugin in Railway dashboard
2. Railway automatically sets DATABASE_URL
3. Update settings.py to use DATABASE_URL (already configured)

---

## 🔍 Troubleshooting

### Issue: "No start command detected"
**Solution:** ✅ Fixed! Procfile created with correct content.

### Issue: "Module 'gunicorn' not found"
**Solution:** ✅ Fixed! Added gunicorn to requirements.txt.

### Issue: "Static files not loading"
**Solution:** 
- Ensure collectstatic runs during build
- Check STATIC_ROOT in settings.py
- Verify WhiteNoise middleware is enabled

### Issue: "Application error"
**Check:**
1. Railway logs for errors
2. Environment variables are set
3. Database migrations are applied
4. ALLOWED_HOSTS includes Railway domain

### Issue: "Database connection error"
**Solution:**
- Add PostgreSQL plugin in Railway
- Verify DATABASE_URL is set
- Run migrations

---

## 📊 Railway Dashboard

### Viewing Logs
1. Go to your project
2. Click on the service
3. Go to "Deployments"
4. Click on latest deployment
5. View logs in real-time

### Monitoring
Railway provides:
- CPU usage
- Memory usage
- Network traffic
- Request metrics

### Custom Domain
1. Go to service settings
2. Click "Domains"
3. Add custom domain
4. Update DNS records
5. Update ALLOWED_HOSTS

---

## 🔐 Security Checklist

- [x] Procfile created
- [x] Gunicorn added to requirements.txt
- [ ] SECRET_KEY set in Railway environment
- [ ] DEBUG=False in Railway environment
- [ ] ALLOWED_HOSTS configured with Railway domain
- [ ] Database credentials secured
- [ ] Email credentials secured
- [ ] HTTPS enabled (automatic on Railway)

---

## 📝 Post-Deployment

### 1. Test the Application
- Visit your Railway URL
- Test homepage
- Test admin panel
- Test user registration
- Test appointment booking

### 2. Run Migrations
```bash
railway run python manage.py migrate
```

### 3. Create Superuser
```bash
railway run python manage.py createsuperuser
```

### 4. Load Initial Data (Optional)
```bash
railway run python manage.py loaddata initial_data.json
```

### 5. Monitor Logs
```bash
railway logs
```

---

## 🔄 Continuous Deployment

Railway automatically deploys when you push to GitHub:

1. Make changes locally
2. Commit: `git commit -m "Your message"`
3. Push: `git push`
4. Railway automatically deploys

---

## 💰 Railway Pricing

- **Starter Plan:** $5/month
- **Developer Plan:** $20/month
- **Team Plan:** Custom pricing

Free trial available with $5 credit.

---

## 🆘 Support

### Railway Support
- Documentation: https://docs.railway.app
- Discord: https://discord.gg/railway
- Email: team@railway.app

### VitalBook Support
- Email: support@vitalbook.in
- Phone: +91 98765 43210

---

## ✅ Deployment Checklist

- [x] Procfile created
- [x] runtime.txt created
- [x] railway.json created
- [x] requirements.txt updated with gunicorn
- [x] Files committed to Git
- [x] Files pushed to GitHub
- [ ] Railway project created
- [ ] Repository connected
- [ ] Environment variables configured
- [ ] Database plugin added
- [ ] Migrations run
- [ ] Superuser created
- [ ] Application tested

---

## 🎉 Success!

Your VitalBook application is now ready for Railway deployment!

**Next Steps:**
1. Go to Railway.app
2. Create new project from GitHub
3. Configure environment variables
4. Deploy!

**Your app will be live at:** `https://your-app.railway.app`

---

**Status:** ✅ Deployment Files Ready
**Date:** April 3, 2026
**Files Created:** 3 (Procfile, runtime.txt, railway.json)
**Files Updated:** 1 (requirements.txt)
**Pushed to GitHub:** ✅ Yes
