# VitalBook - Full Stack Setup Guide

Complete guide to run the Django backend + React frontend together.

## Architecture

```
VitalBook Hospital Management System
├── Backend (Django REST API)     → http://127.0.0.1:8000
└── Frontend (React + Vite)       → http://localhost:5173
```

---

## Quick Start (Both Servers)

### Terminal 1 - Django Backend

```powershell
# Activate virtual environment and start Django
.\start_server.ps1
```

Or manually:
```powershell
.\venv\Scripts\Activate.ps1
python manage.py runserver
```

**Backend will run at:** http://127.0.0.1:8000

### Terminal 2 - React Frontend

```powershell
# Install dependencies and start React
.\start_frontend.ps1
```

Or manually:
```powershell
cd frontend
npm install
npm run dev
```

**Frontend will run at:** http://localhost:5173

---

## What You'll See

1. **Backend API** (Django)
   - REST API at http://127.0.0.1:8000/api/
   - Admin panel at http://127.0.0.1:8000/admin/
   - API endpoints for doctors, patients, appointments, reviews

2. **Frontend App** (React)
   - Dashboard with floating doctor cards
   - Real-time data from Django API
   - Smooth animations with Framer Motion
   - Anti-gravity floating effect on cards

---

## Features

### Backend (Django REST Framework)
✓ RESTful API with pagination
✓ Authentication & permissions
✓ Filtering, search, and ordering
✓ PostgreSQL support (Docker)
✓ SQLite for local development

### Frontend (React + Framer Motion)
✓ Floating doctor cards with anti-gravity effect
✓ Hover animations with glow effect
✓ Loading states with bubble skeletons
✓ Staggered card entrance animations
✓ Error handling with friendly messages

---

## API Endpoints

### Doctors
- `GET /api/doctors/` - List all doctors
- `GET /api/doctors/{id}/` - Doctor detail
- `GET /api/doctors/{id}/reviews/` - Doctor reviews
- `GET /api/doctors/{id}/available_slots/?date=YYYY-MM-DD` - Available slots

### Appointments
- `GET /api/appointments/` - List appointments
- `POST /api/appointments/` - Create appointment
- `POST /api/appointments/{id}/cancel/` - Cancel appointment
- `POST /api/appointments/{id}/confirm/` - Confirm (admin)

### Reviews
- `GET /api/reviews/` - List reviews
- `POST /api/reviews/` - Create review

### Specializations
- `GET /api/specializations/` - List specializations

### Patients
- `GET /api/patients/` - List patients (own only)
- `POST /api/patients/` - Create patient profile

---

## Login Credentials

### Admin Panel
- URL: http://127.0.0.1:8000/admin/
- Username: `admin`
- Password: `admin123`

### Patient Accounts
- Usernames: `arjun_sharma`, `pooja_verma`, `rohit_kumar`
- Password: `password123`

---

## Tech Stack

### Backend
- Django 6.0.1
- Django REST Framework 3.15.2
- PostgreSQL (Docker) / SQLite (local)
- Gunicorn (production)
- WhiteNoise (static files)

### Frontend
- React 18
- Vite 5
- Framer Motion 11
- Axios

---

## Docker Deployment

To run with Docker (PostgreSQL + Django):

```bash
docker-compose up --build
```

Then populate data:
```bash
docker-compose exec web python manage.py populate_data
```

---

## Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```powershell
# Find and kill process
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process
```

**Module not found:**
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Frontend Issues

**CORS errors:**
Add to Django `settings.py`:
```python
INSTALLED_APPS += ['corsheaders']
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')
CORS_ALLOWED_ORIGINS = ['http://localhost:5173']
```

**Port 5173 in use:**
Edit `frontend/vite.config.js` and change the port.

**Dependencies not installed:**
```bash
cd frontend
npm install
```

---

## Project Structure

```
hospital/
├── appointment/              # Django app
│   ├── models.py            # Database models
│   ├── serializers.py       # DRF serializers
│   ├── api_views.py         # API viewsets
│   ├── views.py             # Template views
│   └── urls.py              # URL routing
├── hospital_project/        # Django project
│   └── settings.py          # Configuration
├── frontend/                # React app
│   ├── src/
│   │   ├── components/
│   │   │   ├── DoctorCard.jsx
│   │   │   └── Dashboard.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── Dockerfile               # Docker image
├── docker-compose.yml       # Docker services
├── requirements.txt         # Python deps
└── .env                     # Environment vars
```

---

## Next Steps

1. **Customize the UI** - Edit `DoctorCard.jsx` and `Dashboard.jsx`
2. **Add more features** - Appointment booking, patient dashboard
3. **Deploy** - Use Docker or deploy to cloud platforms
4. **Add authentication** - JWT tokens for API access

---

**Version:** 1.0.0  
**Last Updated:** April 3, 2026
