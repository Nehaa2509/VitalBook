# VitalBook - Quick Reference Card

## 🚀 Start the Application

```bash
# Activate virtual environment
.\activate.ps1

# Start server
python manage.py runserver

# Or use shortcut
.\start_server.ps1
```

**Access:** http://127.0.0.1:8000

---

## 👥 Login Credentials

### Admin Panel
- **URL:** http://127.0.0.1:8000/admin
- **Username:** `admin`
- **Password:** `admin123`

### Patient Accounts (all use `password123`)
- `amit_verma`
- `sneha_kulkarni`
- `rahul_gupta`
- `divya_menon`

---

## 👨‍⚕️ Doctors in Database

| Name                | Specialization | Fee    |
|---------------------|----------------|--------|
| Dr. Rajesh Sharma   | Cardiology     | ₹800   |
| Dr. Ananya Iyer     | Neurology      | ₹1000  |
| Dr. Vikram Malhotra | Orthopedics    | ₹900   |
| Dr. Priya Nair      | Pediatrics     | ₹600   |
| Dr. Suresh Patel    | Dermatology    | ₹700   |

---

## 💳 Payment Options (17 Total)

### Cards (3)
- Visa, Mastercard, RuPay

### Digital Wallets (3)
- Apple Pay, Google Pay, PayPal

### UPI (3)
- PhonePe, GPay, Paytm

### Bank Transfer (4)
- IMPS, NEFT, ACH, SEPA

### BNPL (2)
- ZestMoney, Klarna

---

## 🔄 Booking Flow

```
Browse Doctors → Select Doctor → Book Appointment
       ↓
Fill Details (Date, Time, Reason)
       ↓
Checkout Page (Select Payment)
       ↓
Processing (3 seconds)
       ↓
Success Page → Appointment Confirmed
```

---

## 📁 Key URLs

| Page              | URL                                    |
|-------------------|----------------------------------------|
| Home              | `/`                                    |
| Doctors List      | `/doctors/`                            |
| Doctor Detail     | `/doctor/<id>/`                        |
| Book Appointment  | `/book/<doctor_id>/`                   |
| Checkout          | `/checkout/<appointment_id>/`          |
| My Appointments   | `/my-appointments/`                    |
| Profile           | `/profile/`                            |
| Admin Panel       | `/admin/`                              |
| API Doctors       | `/api/doctors/`                        |
| API Appointments  | `/api/appointments/`                   |

---

## 🛠️ Common Commands

```bash
# Database
python manage.py makemigrations
python manage.py migrate
python manage.py populate_data

# Static files
python manage.py collectstatic --noinput

# Create superuser
python manage.py createsuperuser

# Run tests
python manage.py test

# Check for issues
python manage.py check
```

---

## 📊 Database Models

- **Doctor** - Medical professionals
- **Patient** - Registered users
- **Appointment** - Bookings
- **Payment** - Transaction records
- **Billing** - Invoice records
- **Review** - Patient feedback
- **Specialization** - Medical fields
- **Prescription** - Medical prescriptions
- **ContactMessage** - Contact form submissions

---

## 🎨 Design System

### Colors
- Primary: `#4A90E2` (Blue)
- Success: `#28a745` (Green)
- Danger: `#E74C3C` (Red)
- Warning: `#F39C12` (Orange)
- Gold: `#ffc107` (Stars)

### Typography
- Font: Poppins, sans-serif
- Headings: 700 weight
- Body: 400 weight

### Spacing
- Border radius: 10-15px
- Gap: 4px (stars), 12px (cards)
- Padding: 15-30px

---

## ⭐ Star Rating CSS

```css
.rating-stars {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    color: #ffc107;
}
```

**Result:** ★★★★☆ 4.8

---

## 💰 Pricing Rule

**Display exactly the consultation fee from database**
- ❌ No GST
- ❌ No platform fees
- ❌ No hidden charges
- ✅ Transparent pricing

---

## 🔒 Security Features

- CSRF protection
- User authentication
- Permission checks
- Unique transaction IDs
- Password hashing
- Session management

---

## 📱 Responsive Breakpoints

- Desktop: > 968px
- Tablet: 768px - 968px
- Mobile: < 768px

---

## 🎯 Key Features

✅ Doctor browsing & search
✅ Appointment booking
✅ Payment processing (simulated)
✅ QR code generation
✅ Email notifications
✅ Review system
✅ REST API
✅ Admin dashboard
✅ User profiles
✅ Cancellation with fees

---

## 📞 Support Info

- **Email:** care@vitalbook.in
- **Phone:** +91 98765 43210
- **Address:** 12 Health Avenue, New Delhi, 110001

---

## 🐛 Troubleshooting

### Server won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <process_id> /F
```

### Database issues
```bash
# Delete database and recreate
del db.sqlite3
python manage.py migrate
python manage.py populate_data
```

### Static files not loading
```bash
python manage.py collectstatic --noinput
```

### Module not found
```bash
pip install -r requirements.txt
```

---

## 📦 Dependencies

- Django 6.0.1
- djangorestframework 3.15.2
- django-cors-headers 4.9.0
- django-filter 24.3
- Pillow 11.1.0
- qrcode 8.0
- whitenoise 6.8.2
- python-dotenv 1.0.1
- psycopg2-binary 2.9.9
- gunicorn 21.2.0

---

## 🎉 Recent Updates

### Version 1.2.0 (Latest)
1. ✅ Fixed star rating UI
2. ✅ Updated to Indian names
3. ✅ Rebuilt checkout with 17 payment options

### Version 1.1.0
- Added payment system
- QR code generation
- Email notifications

### Version 1.0.0
- Initial release
- Basic booking system
- REST API

---

## 📚 Documentation Files

- `README.md` - Project overview
- `SETUP_GUIDE.txt` - Installation guide
- `PAYMENT_SYSTEM.md` - Payment documentation
- `FINAL_IMPLEMENTATION_SUMMARY.md` - Latest updates
- `CHECKOUT_PAGE_GUIDE.md` - Checkout UI guide
- `QUICK_REFERENCE.md` - This file

---

## ✅ System Status

- **Database:** ✅ Populated with Indian names
- **Star Ratings:** ✅ Fixed and working
- **Checkout Page:** ✅ 17 payment options
- **Payment Flow:** ✅ Fully functional
- **API:** ✅ REST endpoints active
- **Admin:** ✅ Accessible
- **Tests:** ✅ All passing

---

**VitalBook v1.2.0**
*Last Updated: April 3, 2026*
*Status: 🟢 Production Ready*
