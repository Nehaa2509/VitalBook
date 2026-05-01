# VitalBook Email Flow Diagram

Visual representation of the email notification system.

---

## Email Trigger Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    VitalBook Email System                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│  User Actions    │
└────────┬─────────┘
         │
         ├─────────────────────────────────────────────────────────┐
         │                                                         │
         ▼                                                         ▼
┌─────────────────┐                                    ┌──────────────────┐
│  Registration   │                                    │  Book & Pay      │
└────────┬────────┘                                    └────────┬─────────┘
         │                                                      │
         ▼                                                      ▼
┌─────────────────┐                                    ┌──────────────────┐
│ register() view │                                    │ process_payment()│
└────────┬────────┘                                    └────────┬─────────┘
         │                                                      │
         ▼                                                      ├──────────┐
┌─────────────────┐                                            │          │
│send_welcome_    │                                            ▼          ▼
│email()          │                                    ┌────────────┐ ┌────────────┐
└────────┬────────┘                                    │send_appt_  │ │send_payment│
         │                                             │confirmation│ │_receipt()  │
         ▼                                             └──────┬─────┘ └──────┬─────┘
┌─────────────────┐                                          │              │
│ 👋 Welcome      │                                          ▼              ▼
│    Email        │                                   ┌────────────┐ ┌────────────┐
└─────────────────┘                                   │ ✅ Confirm │ │ 💳 Receipt │
                                                      │    Email   │ │    Email   │
                                                      └────────────┘ └────────────┘

         ┌─────────────────────────────────────────────────────────┐
         │                                                         │
         ▼                                                         ▼
┌─────────────────┐                                    ┌──────────────────┐
│  Cancel Appt    │                                    │  Submit Review   │
└────────┬────────┘                                    └────────┬─────────┘
         │                                                      │
         ▼                                                      ▼
┌─────────────────┐                                    ┌──────────────────┐
│cancel_appt()    │                                    │submit_review()   │
│view             │                                    │view              │
└────────┬────────┘                                    └────────┬─────────┘
         │                                                      │
         ▼                                                      ▼
┌─────────────────┐                                    ┌──────────────────┐
│send_appt_       │                                    │send_review_      │
│cancelled()      │                                    │thankyou()        │
└────────┬────────┘                                    └────────┬─────────┘
         │                                                      │
         ├──────────┐                                           ▼
         │          │                                   ┌──────────────────┐
         ▼          ▼                                   │ ⭐ Thank You     │
┌────────────┐ ┌────────────┐                          │    Email         │
│ ❌ Cancel  │ │ 📋 Doctor  │                          └──────────────────┘
│    Email   │ │    Notice  │
│ (Patient)  │ │    Email   │
└────────────┘ └────────────┘


┌──────────────────┐
│  Automated Task  │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  Cron Job       │
│  (Daily 9 AM)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│send_reminders   │
│command          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│Find tomorrow's  │
│appointments     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│send_appt_       │
│reminder()       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ ⏰ Reminder     │
│    Email        │
└─────────────────┘
```

---

## Email Template Hierarchy

```
base_email.html (Base Template)
├── Header (Gradient Blue)
│   ├── 💊 VitalBook Logo
│   └── Tagline
├── Body (White Background)
│   └── {% block content %}
│       ├── appointment_confirmation.html
│       ├── payment_receipt.html
│       ├── appointment_reminder.html
│       ├── appointment_cancelled.html
│       ├── doctor_cancellation_notice.html
│       ├── review_thankyou.html
│       └── welcome_email.html
└── Footer (Gray Background)
    ├── Copyright
    ├── Contact Info
    └── Disclaimer
```

---

## Email Components

```
┌─────────────────────────────────────────────────────────┐
│                     Email Header                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Gradient Blue Background (#0d6efd → #0056b3)    │  │
│  │  💊 VitalBook                                     │  │
│  │  Your Health, Our Priority                       │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                     Email Body                          │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Greeting & Message                               │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Info Card (Gray Background)                      │  │
│  │  ┌─────────────────────────────────────────────┐  │  │
│  │  │ 👨‍⚕️ Doctor:        Dr. Rajesh Sharma       │  │  │
│  │  │ 📅 Date:           April 5, 2026            │  │  │
│  │  │ ⏰ Time:           10:00 AM                  │  │  │
│  │  │ 💰 Fee:            ₹500                      │  │  │
│  │  │ Status:            ✅ Confirmed              │  │  │
│  │  └─────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Highlight Box (Yellow/Blue/Green)                │  │
│  │  💡 Important: Arrive 10 minutes early           │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │         [  View Appointments →  ]                 │  │
│  │         (Blue Gradient Button)                    │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                     Email Footer                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │  © 2026 VitalBook. All rights reserved.          │  │
│  │  support@vitalbook.in | +91 98765 43210          │  │
│  │  This is an automated email.                     │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Status Badge Colors

```
✅ Confirmed    →  Green (#d4edda / #155724)
❌ Cancelled    →  Red (#f8d7da / #721c24)
💳 Paid         →  Green (#d4edda / #155724)
⏳ Pending      →  Yellow (#fff3cd / #856404)
```

---

## Email Sending Process

```
┌──────────────┐
│ Trigger      │
│ Event        │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ View         │
│ Function     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ email_utils  │
│ Function     │
└──────┬───────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Validate     │  │ Load         │
│ Email        │  │ Template     │
└──────┬───────┘  └──────┬───────┘
       │                 │
       └────────┬────────┘
                │
                ▼
       ┌──────────────┐
       │ Render       │
       │ HTML         │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │ Send Email   │
       │ (SMTP/       │
       │  Console)    │
       └──────┬───────┘
              │
              ├─────────────┐
              │             │
              ▼             ▼
       ┌──────────┐  ┌──────────┐
       │ Success  │  │ Error    │
       │ Return   │  │ Log &    │
       │ True     │  │ Return   │
       │          │  │ False    │
       └──────────┘  └──────────┘
```

---

## User Journey with Emails

```
Day 1: Registration
├─ User registers account
└─ 👋 Welcome email sent

Day 2: Booking
├─ User books appointment
├─ User completes payment
├─ ✅ Confirmation email sent
└─ 💳 Receipt email sent

Day 3: Reminder
└─ ⏰ Reminder email sent (24h before)

Day 4: Appointment
└─ User attends appointment

Day 5: Review
├─ User submits review
└─ ⭐ Thank you email sent

Alternative: Cancellation
├─ User cancels appointment
├─ ❌ Cancellation email to patient
└─ 📋 Cancellation notice to doctor
```

---

## Email Frequency

```
Per User:
├─ Welcome: Once (registration)
├─ Confirmation: Per booking
├─ Receipt: Per payment
├─ Reminder: 24h before each appointment
├─ Cancellation: Per cancellation
└─ Review Thank You: Per review

System-wide:
└─ Reminders: Daily batch (9 AM)
```

---

## Error Handling Flow

```
┌──────────────┐
│ Email        │
│ Function     │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ try:         │
│   Validate   │
│   email      │
└──────┬───────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Email        │  │ No email     │
│ exists       │  │ address      │
└──────┬───────┘  └──────┬───────┘
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Send email   │  │ Return       │
│              │  │ False        │
└──────┬───────┘  └──────────────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌──────────────┐
│ Success      │  │ Exception    │
│ Return True  │  │ Log error    │
│              │  │ Return False │
└──────────────┘  └──────────────┘
```

---

**Last Updated:** April 3, 2026
