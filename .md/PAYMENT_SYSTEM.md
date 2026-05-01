# VitalBook Payment System Documentation

## Overview
VitalBook now includes a simulated payment system that allows patients to pay for their appointments securely before confirmation.

## Features

### 1. Payment Model
- **Transaction ID**: Unique identifier for each payment (format: VB + 12 random characters)
- **Payment Status**: Pending → Processing → Completed/Failed
- **Payment Methods**: UPI, Debit/Credit Card, Net Banking, Wallet
- **Amount Tracking**: Stores consultation fee amount
- **Payment Date**: Timestamp when payment was completed

### 2. Payment Flow

#### Step 1: Book Appointment
- Patient selects doctor and time slot
- Appointment is created with status "Pending"
- Billing record is created (unpaid)
- Patient is redirected to checkout page

#### Step 2: Checkout Page (`/checkout/<appointment_id>/`)
- Displays order summary with doctor details
- Shows price breakdown (consultation fee, GST, total)
- Payment method selection (UPI, Card, Net Banking, Wallet)
- Security badges and payment logos
- Terms & conditions checkbox

#### Step 3: Payment Processing (`/process-payment/<appointment_id>/`)
- Creates Payment record with unique transaction ID
- Shows animated processing screen
- Simulates 3-second payment processing
- Auto-redirects to success page

#### Step 4: Payment Success (`/payment-success/<appointment_id>/`)
- Updates payment status to "Completed"
- Updates appointment status to "Confirmed"
- Marks billing record as paid
- Displays payment receipt with transaction details
- Shows appointment details and next steps
- Auto-redirects to "My Appointments" after 10 seconds

### 3. UI Components

#### Checkout Page Features
- Professional gradient header
- Two-column layout (order summary + payment form)
- Interactive payment method cards with hover effects
- Security badges and trust indicators
- Payment gateway logos (Visa, Mastercard, RuPay, Paytm, Google Pay)

#### Processing Page Features
- Animated spinner with pulse ring effect
- Transaction details display
- Security message
- Auto-redirect after 3 seconds

#### Success Page Features
- Animated success icon (scale-in animation)
- Payment receipt with dashed border
- Transaction ID and payment details
- Appointment summary card
- "What's Next?" section with helpful tips
- Action buttons (View Appointment, My Appointments)

### 4. CSS Styling

All payment pages use consistent styling with:
- Primary color: #4A90E2
- Success color: #28a745
- Gradient backgrounds: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
- Border radius: 12-20px for cards
- Box shadows for depth
- Smooth transitions and hover effects

### 5. Security Features

- CSRF protection on all forms
- User authentication required
- Permission checks (users can only pay for their own appointments)
- Unique transaction IDs
- Payment status tracking
- Duplicate payment prevention

### 6. Database Schema

```python
class Payment(models.Model):
    appointment = ForeignKey(Appointment)
    amount = DecimalField
    payment_status = CharField (Pending/Processing/Completed/Failed)
    payment_method = CharField (UPI/Card/NetBanking/Wallet)
    transaction_id = CharField (unique)
    payment_date = DateTimeField
    created_at = DateTimeField
```

### 7. Admin Interface

Payment records are accessible in Django admin with:
- List view showing transaction ID, amount, status, method
- Filters by status, method, date
- Search by transaction ID, patient name, doctor name
- Editable payment status
- Read-only transaction ID and timestamps

### 8. API Integration

Payment serializer available for REST API:
- Endpoint: `/api/payments/` (if viewset is added)
- Fields: transaction_id, amount, status, method, dates
- Related data: patient name, doctor name
- Display values for choice fields

## Usage Instructions

### For Patients:
1. Browse doctors and select one
2. Choose appointment date and time
3. Click "Book Now"
4. Review order summary on checkout page
5. Select payment method
6. Accept terms and click "Pay Securely"
7. Wait for processing (3 seconds)
8. View payment receipt and confirmation
9. Check email for appointment details

### For Admins:
1. Access Django admin panel
2. Navigate to "Payments" section
3. View all transactions
4. Filter by status or payment method
5. Update payment status if needed
6. Export payment reports

## Testing

### Test Payment Flow:
1. Login as patient (arjun_sharma / password123)
2. Book appointment with any doctor
3. Complete checkout with any payment method
4. Verify payment success page appears
5. Check "My Appointments" for confirmed status
6. Verify payment record in admin panel

### Test Scenarios:
- ✅ Successful payment flow
- ✅ Multiple payment methods
- ✅ Payment status updates
- ✅ Appointment confirmation
- ✅ Billing record updates
- ✅ Permission checks
- ✅ Duplicate payment prevention

## Future Enhancements

Potential improvements:
- Real payment gateway integration (Razorpay, Stripe)
- Payment refunds for cancellations
- Partial payments
- Payment history page
- Invoice generation (PDF)
- Payment reminders via email/SMS
- Multiple payment attempts tracking
- Payment analytics dashboard

## Technical Notes

- Payment processing is simulated (3-second delay)
- No actual money is transferred
- Transaction IDs are randomly generated
- All payments auto-succeed in current implementation
- For production, integrate real payment gateway

## Files Modified/Created

### New Files:
- `appointment/templates/appointment/checkout.html`
- `appointment/templates/appointment/payment_processing.html`
- `appointment/templates/appointment/payment_success.html`
- `appointment/migrations/0003_payment.py`
- `PAYMENT_SYSTEM.md`

### Modified Files:
- `appointment/models.py` (added Payment model)
- `appointment/views.py` (added checkout, process_payment, payment_success views)
- `appointment/urls.py` (added payment routes)
- `appointment/admin.py` (registered Payment model)
- `appointment/serializers.py` (added PaymentSerializer)
- `appointment/static/css/style.css` (fixed rating stars CSS)

## Support

For issues or questions:
- Email: care@vitalbook.in
- Phone: +91 98765 43210
- Admin Panel: http://127.0.0.1:8000/admin/

---

**VitalBook Payment System v1.0**
*Secure, Simple, Seamless*
