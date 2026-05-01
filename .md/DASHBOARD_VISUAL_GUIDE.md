# VitalBook - Patient Dashboard Visual Guide

## 📐 Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                     VITALBOOK PATIENT DASHBOARD                  │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┬──────────────────────────────────────────────────┐
│   SIDEBAR    │              MAIN CONTENT                         │
│   (260px)    │                                                   │
│              │                                                   │
│  ┌────────┐  │  ┌──────────────────────────────────────────┐   │
│  │   AV   │  │  │  Good Morning, Amit 👋                   │   │
│  └────────┘  │  │  Welcome to your VitalBook dashboard     │   │
│  Amit Verma  │  └──────────────────────────────────────────┘   │
│  amit@...    │                                                   │
│              │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐              │
│ 🏠 Dashboard │  │ 📅  │ │ ⏰  │ │ ✅  │ │ ❌  │              │
│ 📅 My Appts  │  │  5  │ │  2  │ │  2  │ │  1  │              │
│ 👨‍⚕️ Doctors   │  │Total│ │ Up  │ │Comp │ │Canc │              │
│ 💳 Payments  │  └─────┘ └─────┘ └─────┘ └─────┘              │
│ ⭐ Reviews   │                                                   │
│ ⚙️ Settings  │  ┌──────────────────────────────────────────┐   │
│ 🚪 Logout    │  │  Upcoming Appointments        View All → │   │
│              │  ├──────────────────────────────────────────┤   │
│              │  │ 👨‍⚕️ Dr. Rajesh Sharma                    │   │
│              │  │ 🏥 Cardiology                            │   │
│              │  │ 📅 Jan 15, 2025  ⏰ 10:30 AM  ₹500      │   │
│              │  │ [View] [Reschedule] [Cancel]            │   │
│              │  └──────────────────────────────────────────┘   │
│              │                                                   │
│              │  ┌──────────────────────────────────────────┐   │
│              │  │  Completed Appointments       View All → │   │
│              │  ├──────────────────────────────────────────┤   │
│              │  │ 👨‍⚕️ Dr. Ananya Iyer                      │   │
│              │  │ 🏥 Pediatrics                            │   │
│              │  │ 📅 Jan 10, 2025  ₹800                   │   │
│              │  │ [📄 Receipt] [⭐ Review]                 │   │
│              │  └──────────────────────────────────────────┘   │
│              │                                                   │
│              │  ┌──────────────────────────────────────────┐   │
│              │  │  Payment History                          │   │
│              │  ├──────────────────────────────────────────┤   │
│              │  │ Date    Doctor    Amount  Method  Status │   │
│              │  │ Jan 15  Sharma    ₹500    UPI     ✅ Paid│   │
│              │  │ Jan 10  Iyer      ₹800    Card    ✅ Paid│   │
│              │  │                                           │   │
│              │  │ ┌───────────────────────────────────┐    │   │
│              │  │ │   Total Spent: ₹1,300             │    │   │
│              │  │ └───────────────────────────────────┘    │   │
│              │  └──────────────────────────────────────────┘   │
│              │                                                   │
│              │  ┌──────────────────────────────────────────┐   │
│              │  │  My Reviews                               │   │
│              │  ├──────────────────────────────────────────┤   │
│              │  │ 👨‍⚕️ Dr. Ananya Iyer                      │   │
│              │  │ ⭐⭐⭐⭐⭐                                  │   │
│              │  │ "Very professional and helpful doctor."  │   │
│              │  └──────────────────────────────────────────┘   │
└──────────────┴──────────────────────────────────────────────────┘
```

---

## 🎨 Color Scheme

### Sidebar
- **Background**: #0d6efd (Blue)
- **Text**: White
- **Active Item**: rgba(255,255,255,0.2)
- **Hover**: rgba(255,255,255,0.1)

### Stat Cards
- **Blue Card** (Total): #e7f1ff background, #0d6efd icon
- **Green Card** (Upcoming): #d4edda background, #28a745 icon
- **Purple Card** (Completed): #e7e3ff background, #6f42c1 icon
- **Red Card** (Cancelled): #f8d7da background, #dc3545 icon

### Status Badges
- **Confirmed**: #d4edda background, #28a745 text
- **Pending**: #fff3cd background, #ffc107 text
- **Completed**: #e7e3ff background, #6f42c1 text
- **Cancelled**: #f8d7da background, #dc3545 text

---

## 📱 Responsive Breakpoints

### Desktop (> 1200px)
```
┌──────────┬────────────────────────────────────┐
│ Sidebar  │  Main Content (4 stat cards)       │
│ 260px    │  [Card] [Card] [Card] [Card]       │
│          │  Appointments...                    │
└──────────┴────────────────────────────────────┘
```

### Tablet (768px - 1200px)
```
┌──────────┬────────────────────────────────────┐
│ Sidebar  │  Main Content (2x2 stat cards)     │
│ 260px    │  [Card] [Card]                     │
│          │  [Card] [Card]                     │
│          │  Appointments...                    │
└──────────┴────────────────────────────────────┘
```

### Mobile (< 768px)
```
┌────────────────────────────────────────────────┐
│ Sidebar (Full Width)                           │
│ [Avatar] Amit Verma                            │
│ 🏠 Dashboard  📅 Appointments  ...             │
└────────────────────────────────────────────────┘
┌────────────────────────────────────────────────┐
│ Main Content (Stacked)                         │
│ [Card]                                         │
│ [Card]                                         │
│ [Card]                                         │
│ [Card]                                         │
│ Appointments...                                 │
└────────────────────────────────────────────────┘
```

---

## 🔄 User Flow

### 1. Login
```
Login Page → Enter Credentials → Dashboard
```

### 2. View Appointments
```
Dashboard → Upcoming Section → View Details
```

### 3. Book Appointment
```
Dashboard → Find Doctors → Select Doctor → Book
```

### 4. Download Receipt
```
Dashboard → Payment History → Click Receipt → PDF Download
```

### 5. Leave Review
```
Dashboard → Completed Appointments → Click Review → Submit
```

### 6. Update Profile
```
Dashboard → Settings → Edit Info → Save
```

---

## 📊 Data Flow

```
User Login
    ↓
Get/Create Patient
    ↓
Fetch Appointments
    ├─→ Upcoming (date >= today, status = Confirmed/Pending)
    ├─→ Completed (status = Completed)
    └─→ Cancelled (status = Cancelled)
    ↓
Calculate Stats
    ├─→ Total Count
    ├─→ Upcoming Count
    ├─→ Completed Count
    └─→ Cancelled Count
    ↓
Fetch Payments
    └─→ Calculate Total Spent
    ↓
Fetch Reviews
    ↓
Generate Greeting (based on time)
    ↓
Render Dashboard
```

---

## 🎯 Interactive Elements

### Hover Effects
- **Stat Cards**: Lift up 5px
- **Appointment Cards**: Shadow + border color change
- **Buttons**: Background color darken
- **Sidebar Items**: Background lighten

### Click Actions
- **View Details**: Navigate to appointment detail page
- **Reschedule**: Navigate to reschedule form
- **Cancel**: Confirm dialog → Cancel appointment
- **Receipt**: Download PDF
- **Review**: Navigate to review form
- **View All**: Navigate to full list

---

## 📐 Spacing & Sizing

### Sidebar
- Width: 260px
- Padding: 20px
- Avatar: 80px × 80px
- Menu item padding: 12px 15px
- Gap between items: 5px

### Main Content
- Padding: 30px
- Stat cards gap: 20px
- Section margin: 30px
- Card padding: 25px

### Typography
- Welcome heading: 28px
- Section title: 20px
- Stat number: 32px
- Doctor name: 18px
- Body text: 14px

---

## 🎨 Visual Hierarchy

### Level 1 (Most Important)
- Welcome greeting
- Stat card numbers
- Doctor names

### Level 2 (Important)
- Section titles
- Appointment dates
- Payment amounts

### Level 3 (Supporting)
- Descriptions
- Status badges
- Action buttons

### Level 4 (Least Important)
- Timestamps
- Helper text
- Icons

---

## ✨ Animation & Transitions

### Transitions (0.3s ease)
- Stat card hover
- Button hover
- Appointment card hover
- Sidebar menu hover

### Smooth Scrolling
- Anchor links (payment history, reviews)
- Behavior: smooth
- Block: start

---

## 🎯 Empty States

### No Upcoming Appointments
```
┌────────────────────────────────────┐
│         📅 (large icon)            │
│   No Upcoming Appointments         │
│   Book an appointment to start     │
│   [Find Doctors]                   │
└────────────────────────────────────┘
```

### No Completed Appointments
```
┌────────────────────────────────────┐
│         ✅ (large icon)            │
│   No Completed Appointments        │
│   Your history will appear here    │
└────────────────────────────────────┘
```

### No Payment History
```
┌────────────────────────────────────┐
│         💳 (large icon)            │
│   No Payment History               │
│   Your payments will appear here   │
└────────────────────────────────────┘
```

### No Reviews
```
┌────────────────────────────────────┐
│         ⭐ (large icon)            │
│   No Reviews Yet                   │
│   Complete an appointment first    │
└────────────────────────────────────┘
```

---

## 🎉 Status: COMPLETE

All visual elements implemented and tested!

**Access Dashboard:**
http://127.0.0.1:8000/patient/dashboard/

**Test Account:**
- Username: amitverma
- Password: password123
