# VitalBook - Hospital Appointment System

## Project Overview
Full-stack hospital appointment system built with **Django 6.0** (Python 3.13) and **SQLite**. Patients book appointments, make payments, and manage healthcare journeys. Admins manage doctors, appointments, and payments.

## Tech Stack
| Backend | Django 6.0.1, Python 3.13, DRF 3.17.1 |
| Frontend | HTML5, CSS3, JavaScript, Bootstrap, Font Awesome |
| Database | SQLite (dev), PostgreSQL/MySQL (production) |
| Integrations | Razorpay (payment), Twilio (SMS), SMTP (email) |
| Deployment | Gunicorn, WhiteNoise, Railway-ready |

## Quick Start
```powershell
.\venv\Scripts\Activate.ps1          # Activate venv
pip install -r requirements.txt      # Install deps
copy .env.example .env               # Configure env vars (set DEBUG=True)
python manage.py migrate             # Run migrations
python populate_db.py                # Seed sample data
python manage.py runserver           # Start dev server → http://127.0.0.1:8000/
```

**Credentials:** Admin: `admin`/`admin123` | Patient: `john_doe`/`password123`

## Project Structure
```
hospital/
├── hospital_project/     # Django config (settings.py, urls.py, wsgi.py)
├── appointment/          # Main app (models, views, urls, templates, static)
│   ├── models.py         # Doctor, Patient, Appointment, Payment, Review, OTP
│   ├── middleware.py     # Admin/user separation middleware
│   └── email_utils.py    # Email/OTP utilities
├── templates/            # Global templates (admin overrides)
├── staticfiles/          # Collected static (production)
├── Procfile              # Gunicorn deployment
└── runtime.txt           # python-3.13.0
```

## Key Commands
```bash
python manage.py makemigrations && migrate  # DB changes
python manage.py collectstatic              # Static files for production
python manage.py test                       # Run tests
gunicorn hospital_project.wsgi:application  # Production server
```

## Database Models
- **Specialization** → **Doctor** (ForeignKey) — doctor profiles with ratings, fees, availability
- **User** → **Patient** (OneToOne) → **Appointment** (ForeignKey) — booking records
- **Appointment** → **Payment** (FK), **Review** (OneToOne), **Prescription** (OneToOne), **Billing** (FK)
- **OTPVerification** — email verification tokens (10-min expiry)
- **ContactMessage** — support inquiries

## Key Workflows
1. **Patient Booking:** Register → OTP verify → Browse doctors → Book → Checkout → Pay → Confirmed
2. **Admin Management:** `/admin/` → Manage doctors → Bulk appointment actions → Monitor payments
3. **Payment Flow:** Book → `/checkout/<id>/` → `/process-payment/<id>/` → `/payment-success/<id>/`

## Environment Variables (.env)
```env
SECRET_KEY=your_secret_key_here
DEBUG=True
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
RAZORPAY_KEY_ID=
TWILIO_ACCOUNT_SID=
```

---

## Frontend Website Rules

### Always Do First
- **Invoke the `frontend-design` skill** before writing any frontend code, every session, no exceptions.

### Reference Images & Screenshots
- If reference image provided: match layout, spacing, typography, color exactly. Do not improve.
- Screenshot workflow: `node serve.mjs` (start server) → `node screenshot.mjs http://localhost:3000` → compare → fix → repeat (min 2 rounds).
- Screenshots saved to `./temporary screenshots/screenshot-N.png`. Read with Read tool to analyze.

### Output Defaults
- Single `index.html`, all styles inline unless specified otherwise
- Tailwind CSS via CDN: `<script src="https://cdn.tailwindcss.com"></script>`
- Placeholder images: `https://placehold.co/WIDTHxHEIGHT`
- Mobile-first responsive

### Anti-Generic Guardrails
- **Colors:** No default Tailwind palette. Pick custom brand colors.
- **Shadows:** No flat `shadow-md`. Use layered, color-tinted shadows.
- **Typography:** Pair display/serif with clean sans. Tight tracking (`-0.03em`) on headings, line-height `1.7` on body.
- **Animations:** Only `transform` and `opacity`. Never `transition-all`. Spring-style easing.
- **Interactive states:** Every clickable element needs hover, focus-visible, active states.
- **Images:** Gradient overlay (`bg-gradient-to-t from-black/60`) + `mix-blend-multiply` layer.

### Hard Rules
- Do not add sections/features not in reference | Do not "improve" reference | Do not stop after one screenshot pass
- Do not use `transition-all` | Do not use default Tailwind blue/indigo as primary color

---

## Important Notes
- Student project for educational purposes | Payment is simulated (ready for Razorpay)
- Email uses console backend in dev (check terminal for OTP) | Timezone: Asia/Kolkata
- Unique constraint: `doctor + date + time` (prevents double-booking) | 24-hr free cancellation window

## Troubleshooting
| Issue | Fix |
|-------|-----|
| OTP not showing | Check terminal console output |
| Admin styling missing | Clear cache (Ctrl+Shift+R) |
| Migration errors | Delete `db.sqlite3` + `migrations/` (keep `__init__.py`), re-run |
| CORS errors | Check `CORS_ALLOW_ALL_ORIGINS` in `.env` |
