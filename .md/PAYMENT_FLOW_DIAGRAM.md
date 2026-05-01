# VitalBook Payment Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     VITALBOOK PAYMENT FLOW                          │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   PATIENT    │
│  Browses     │
│  Doctors     │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Select Doctor   │
│  Choose Date     │
│  Choose Time     │
└──────┬───────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  BOOK APPOINTMENT                                               │
│  ─────────────────                                              │
│  • Creates Appointment (status: "Pending")                      │
│  • Creates Billing record (is_paid: False)                      │
│  • Generates QR code                                            │
│  • Redirects to Checkout                                        │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  CHECKOUT PAGE (/checkout/<id>/)                               │
│  ────────────────────────────────                               │
│                                                                 │
│  ┌─────────────────┐  ┌──────────────────────────────────┐    │
│  │ Order Summary   │  │  Payment Method Selection        │    │
│  │ ─────────────   │  │  ────────────────────────        │    │
│  │ • Doctor Info   │  │  ○ UPI (Google Pay, PhonePe)     │    │
│  │ • Date & Time   │  │  ○ Card (Visa, Mastercard)       │    │
│  │ • Patient Name  │  │  ○ Net Banking (All Banks)       │    │
│  │                 │  │  ○ Wallet (Paytm, PhonePe)       │    │
│  │ Price Breakdown │  │                                  │    │
│  │ • Fee: ₹800     │  │  ☑ Accept Terms & Conditions     │    │
│  │ • GST: ₹800     │  │                                  │    │
│  │ • Total: ₹800   │  │  [Pay ₹800 Securely] 🔒          │    │
│  │                 │  │                                  │    │
│  │ 🛡️ 100% Secure  │  │  💳 Payment Logos                │    │
│  └─────────────────┘  └──────────────────────────────────┘    │
└──────┬──────────────────────────────────────────────────────────┘
       │ Click "Pay Securely"
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  PROCESS PAYMENT (/process-payment/<id>/)                      │
│  ──────────────────────────────────────                        │
│  • Creates Payment record (status: "Processing")               │
│  • Generates unique Transaction ID (VB + 12 chars)             │
│  • Stores payment method                                       │
│  • Redirects to Processing page                                │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  PAYMENT PROCESSING PAGE                                        │
│  ────────────────────────                                       │
│                                                                 │
│                    ⟳ Processing...                              │
│                   ◯ Pulse Ring                                  │
│                                                                 │
│         Processing Your Payment                                 │
│         Please wait while we securely process...                │
│                                                                 │
│         Transaction ID: VB1A2B3C4D5E6F                          │
│         Amount: ₹800                                            │
│         Method: UPI                                             │
│                                                                 │
│         🛡️ Do not refresh or close this page                    │
│                                                                 │
│         [Auto-redirect after 3 seconds]                         │
└──────┬──────────────────────────────────────────────────────────┘
       │ After 3 seconds
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  PAYMENT SUCCESS (/payment-success/<id>/)                      │
│  ──────────────────────────────────────                        │
│  • Updates Payment (status: "Completed", payment_date: now)    │
│  • Updates Appointment (status: "Confirmed")                   │
│  • Updates Billing (is_paid: True)                             │
│  • Sends confirmation email                                    │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│  SUCCESS PAGE                                                   │
│  ────────────                                                   │
│                                                                 │
│                    ✓ Payment Successful!                        │
│              Your appointment has been confirmed                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ 🧾 Payment Receipt                        [PAID]      │     │
│  │ ─────────────────────────────────────────────────     │     │
│  │ Transaction ID: VB1A2B3C4D5E6F                        │     │
│  │ Payment Date: 03 Apr, 2026 - 2:30 PM                 │     │
│  │ Payment Method: UPI                                   │     │
│  │ Amount Paid: ₹800                                     │     │
│  │                                                       │     │
│  │ Appointment Details:                                  │     │
│  │ 👨‍⚕️ Dr. Priya Sharma - Cardiology                     │     │
│  │ 📅 05 Apr, 2026 at 10:00 AM                           │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                 │
│  [View Appointment]  [My Appointments]                          │
│                                                                 │
│  What's Next?                                                   │
│  📧 Check email    🔲 Use QR code    ⏰ Arrive 15 min early     │
│                                                                 │
│  [Auto-redirect to My Appointments after 10 seconds]           │
└──────┬──────────────────────────────────────────────────────────┘
       │
       ▼
┌──────────────────┐
│ MY APPOINTMENTS  │
│ ────────────     │
│ ✓ Confirmed      │
│   Appointment    │
└──────────────────┘
```

## Database State Changes

### Before Payment:
```
Appointment:
  - status: "Pending"
  - created_at: timestamp

Billing:
  - is_paid: False
  - total_amount: 800.00

Payment:
  - (does not exist yet)
```

### During Payment:
```
Appointment:
  - status: "Pending" (unchanged)

Billing:
  - is_paid: False (unchanged)

Payment:
  - payment_status: "Processing"
  - transaction_id: "VB1A2B3C4D5E6F"
  - payment_method: "UPI"
  - amount: 800.00
```

### After Payment:
```
Appointment:
  - status: "Confirmed" ✓
  - updated_at: timestamp

Billing:
  - is_paid: True ✓
  - total_amount: 800.00

Payment:
  - payment_status: "Completed" ✓
  - payment_date: timestamp ✓
  - transaction_id: "VB1A2B3C4D5E6F"
  - payment_method: "UPI"
  - amount: 800.00
```

## URL Routes

```
/doctors/                           → Browse doctors
/doctor/<id>/                       → Doctor details
/book/<doctor_id>/                  → Book appointment form
/checkout/<appointment_id>/         → Payment checkout page
/process-payment/<appointment_id>/  → Process payment (POST)
/payment-success/<appointment_id>/  → Success page
/my-appointments/                   → View all appointments
/appointment/<id>/                  → Appointment details
```

## Security Checks

```
✓ CSRF Token validation
✓ User authentication required
✓ Permission check (own appointments only)
✓ Unique transaction IDs
✓ Duplicate payment prevention
✓ Status validation
✓ Amount verification
```

## Payment Methods Supported

```
┌─────────────┬──────────────────────────────────────┐
│   Method    │          Providers                   │
├─────────────┼──────────────────────────────────────┤
│ UPI         │ Google Pay, PhonePe, Paytm, BHIM    │
│ Card        │ Visa, Mastercard, RuPay, Amex       │
│ Net Banking │ All major Indian banks               │
│ Wallet      │ Paytm, PhonePe, Amazon Pay, Mobikwik│
└─────────────┴──────────────────────────────────────┘
```

## Error Handling

```
❌ User not authenticated → Redirect to login
❌ Wrong appointment owner → Error message + redirect
❌ Already paid → Info message + redirect to details
❌ No payment method selected → Error + stay on checkout
❌ Invalid appointment ID → 404 error
```

## Auto-Redirects

```
Processing Page → Success Page (3 seconds)
Success Page → My Appointments (10 seconds)
```

---

**VitalBook Payment System**
*Simple. Secure. Seamless.*
