# 🏥 VitalBook — Hospital Appointment Management System

A full-stack web application for managing hospital appointments, built with **Python 3.13 + Django 6.0**. Patients can register, browse doctors, book appointments, pay online, and download digital prescriptions — all from a single platform.

> 🚀 **Live Demo**: https://vitalbook-1.onrender.com &nbsp;|&nbsp; 👨‍💻 **Tech Stack**: Django 6.0 · SQLite · Cashfree UPI · xhtml2pdf

---

## ✨ Features

### 👤 Patient
- Register & login with secure authentication
- Browse doctors by specialization
- Book, view, and cancel appointments
- Real-time appointment status tracking
- **UPI Payment** via Cashfree Payment Gateway
- **PDF Prescriptions** — download directly from dashboard
- **Automated Email Notifications** for bookings & prescriptions

### 🛠️ Admin
- Add, edit, and delete doctor profiles
- Approve or cancel appointments
- Filter appointments by status, date, and doctor
- Generate digital prescriptions with auto-filled patient details
- **Real-time Online/Offline** user activity tracking

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13, Django 6.0 |
| Database | SQLite |
| Frontend | HTML5, CSS3, JavaScript |
| Authentication | Django built-in auth + session management |
| PDF Generation | `xhtml2pdf` |
| Payments | Cashfree Payment Gateway (UPI) |
| Email | Django SMTP Backend |
| Deployment | Render |

---

## 📁 Project Structure

```
hospital_project/
├── manage.py
├── db.sqlite3
├── hospital_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── appointment/
    ├── models.py           # Doctor, Patient, Appointment models
    ├── views.py            # Business logic & view handlers
    ├── urls.py             # URL routing
    ├── admin.py            # Admin panel configuration
    ├── templates/
    │   └── appointment/
    │       ├── base.html
    │       ├── home.html
    │       ├── doctor_list.html
    │       ├── register.html
    │       ├── login.html
    │       ├── book_appointment.html
    │       └── my_appointments.html
    └── static/
        ├── css/style.css
        └── js/script.js
```

---

## ⚙️ Setup & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Nehaa2509/vitalbook.git
cd vitalbook
```

### 2. Activate Virtual Environment

```powershell
# PowerShell
.\venv\Scripts\Activate.ps1
```
```bash
# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:
```env
SECRET_KEY=your_django_secret_key
DEBUG=True
CASHFREE_APP_ID=your_cashfree_app_id
CASHFREE_SECRET_KEY=your_cashfree_secret_key
CASHFREE_ENV=TEST
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```
> ⚠️ Never commit real credentials to a public repository.

### 5. Apply Migrations & Seed Data
```bash
python manage.py migrate
python manage.py populate_data   # Seeds demo doctors & patients
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

Visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 🔑 Demo Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin123` |
| Patient | `john_doe` | `password123` |
| Patient | `jane_smith` | `password123` |
| Patient | `bob_wilson` | `password123` |

Admin Panel: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🗄️ Database Models

### `Doctor`
- Name, Specialization, Available Time, Email, Phone

### `Patient`
- Linked Django User, Name, Email, Phone, Address

### `Appointment`
- Patient (FK) · Doctor (FK) · Date · Time
- Status: `Pending` → `Confirmed` → `Completed` / `Cancelled`
- Reason, Created Timestamp

---

## 🔄 Application Flow

```
Patient Registers → Logs In → Browses Doctors
    → Books Appointment → Pays via UPI (Cashfree)
        → Receives Email Confirmation
            → Admin Approves → Prescription Generated
                → Patient Downloads PDF
```

---

## 🔒 Security Highlights

- CSRF protection on all forms
- Django session-based authentication
- Environment variables for all secrets
- Server-side & client-side form validation
- Role-based access: patients cannot access admin views

---

## 🚀 Deployment (Railway)

This project is deployed on **Railway** with the following configuration:

- `Procfile` for gunicorn web server
- `requirements.txt` with all dependencies (UTF-8 encoded)
- `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` configured for production

---

## 🔮 Future Enhancements

- [ ] SMS reminders via Twilio
- [ ] Doctor availability calendar view
- [ ] Patient medical history & health records
- [ ] Video consultation integration

---

## 👩‍💻 Developer

**Sneha Rudani** — B.E. Information Technology, GTU  
GitHub: [@Nehaa2509](https://github.com/Nehaa2509) &nbsp;|&nbsp; LinkedIn: [sneha-rudani](https://linkedin.com/in/sneha-rudani)

---

*Built as a capstone project demonstrating full-stack Django development with real-world integrations.*
