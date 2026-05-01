# VitalBook Checkout - Testing Guide

## 🧪 Complete Testing Workflow

Follow these steps to test the new checkout and payment system.

---

## 🚀 Step 1: Start the Server

```bash
# Activate virtual environment
.\activate.ps1

# Start Django server
python manage.py runserver
```

**Server URL:** http://127.0.0.1:8000

---

## 👤 Step 2: Login as Patient

### Option A: Use Existing Patient
1. Go to http://127.0.0.1:8000/login
2. Login with:
   - **Username:** `amit_verma`
   - **Password:** `password123`

### Option B: Create New Patient
1. Go to http://127.0.0.1:8000/register
2. Fill registration form
3. Login with new credentials

---

## 📅 Step 3: Book an Appointment

### 3.1 Browse Doctors
1. Click "Doctors" in navigation
2. Or go to http://127.0.0.1:8000/doctors/

### 3.2 Select a Doctor
- Choose any doctor (e.g., Dr. Rajesh Sharma)
- Click "Book Now" button

### 3.3 Fill Appointment Details
```
Date: Select future date (e.g., tomorrow)
Time: Select available time slot
Reason: "Regular checkup"
Symptoms: "General health check"
```

### 3.4 Submit Booking
- Click "Submit" or "Book Appointment"
- You'll be redirected to checkout page

---

## 💳 Step 4: Test Checkout Page

### 4.1 Verify Left Side (Booking Summary)
Check that it displays:
- ✅ Doctor photo (avatar)
- ✅ Doctor name (e.g., Dr. Rajesh Sharma)
- ✅ Specialization (e.g., Cardiology)
- ✅ Appointment date
- ✅ Appointment time
- ✅ Patient name
- ✅ Consultation fee (exact amount, no extras)

### 4.2 Verify Right Side (Payment Options)
Check all 5 categories are visible:

**1. Credit / Debit Card**
- [ ] Visa
- [ ] Mastercard
- [ ] RuPay

**2. Digital Wallets**
- [ ] Apple Pay
- [ ] Google Pay
- [ ] PayPal

**3. UPI**
- [ ] PhonePe
- [ ] GPay
- [ ] Paytm

**4. Bank Transfer**
- [ ] IMPS
- [ ] NEFT
- [ ] ACH
- [ ] SEPA

**5. Buy Now Pay Later**
- [ ] ZestMoney
- [ ] Klarna

### 4.3 Test Payment Selection
1. **Hover over payment options**
   - Should show blue border
   - Should lift slightly (translateY -2px)

2. **Click on any payment option**
   - Should get blue border
   - Background should turn light blue (#e7f1ff)
   - "Complete Payment" button should enable

3. **Click different options**
   - Only one should be selected at a time
   - Previous selection should deselect

### 4.4 Test Complete Payment Button
1. **Before selection:**
   - Button should be disabled (gray)
   - Cursor should show "not-allowed"

2. **After selection:**
   - Button should be enabled (blue)
   - Cursor should show "pointer"

---

## ⚙️ Step 5: Test Payment Processing

### 5.1 Click "Complete Payment"
Watch for these stages:

**Stage 1: Processing Overlay (2 seconds)**
- [ ] Fullscreen dark overlay appears
- [ ] Spinning circle animation
- [ ] Text: "Processing your payment..."
- [ ] Duration: exactly 2 seconds

**Stage 2: Success Modal**
- [ ] Processing overlay disappears
- [ ] Success modal appears
- [ ] Green checkmark icon
- [ ] "Payment Successful!" heading

### 5.2 Verify Receipt Details
Check the receipt shows:
- [ ] Booking ID (format: VB-XXXXXXXX)
- [ ] Doctor Name
- [ ] Appointment Date
- [ ] Appointment Time
- [ ] Amount Paid
- [ ] Payment Method (the one you selected)

### 5.3 Watch Auto-Redirect
- [ ] Countdown starts at 3 seconds
- [ ] Text: "Redirecting to dashboard in X seconds..."
- [ ] Countdown decreases: 3 → 2 → 1
- [ ] Auto-redirects to "My Appointments" page

---

## ✅ Step 6: Verify in My Appointments

### 6.1 Check Appointment Status
1. You should be on "My Appointments" page
2. Find your new appointment
3. Verify:
   - [ ] Status shows "Confirmed" (not "Pending")
   - [ ] Appointment details are correct
   - [ ] Payment badge shows "Paid"

### 6.2 View Appointment Details
1. Click on the appointment
2. Check:
   - [ ] Full appointment information
   - [ ] Payment record exists
   - [ ] Billing marked as paid

---

## 🔧 Step 7: Verify in Admin Panel

### 7.1 Login to Admin
1. Go to http://127.0.0.1:8000/admin/
2. Login with:
   - **Username:** `admin`
   - **Password:** `admin123`

### 7.2 Check Appointment
1. Navigate to "Appointments"
2. Find your appointment
3. Verify:
   - [ ] Status = "Confirmed"
   - [ ] Updated timestamp is recent

### 7.3 Check Payment Record
1. Navigate to "Payments"
2. Find your payment
3. Verify:
   - [ ] Transaction ID (VB-XXXXXXXX)
   - [ ] Amount matches consultation fee
   - [ ] Payment status = "Completed"
   - [ ] Payment method matches selection
   - [ ] Payment date is current

### 7.4 Check Billing Record
1. Navigate to "Billings"
2. Find your billing record
3. Verify:
   - [ ] is_paid = True (checked)
   - [ ] Total amount correct

---

## 📱 Step 8: Test Responsive Design

### 8.1 Desktop View (>968px)
- [ ] Two-column layout
- [ ] Payment options in 3 columns
- [ ] All elements visible

### 8.2 Tablet View (768px - 968px)
1. Resize browser to ~800px width
2. Check:
   - [ ] Single column layout
   - [ ] Payment options in 2 columns
   - [ ] Scrollable content

### 8.3 Mobile View (<576px)
1. Resize browser to ~400px width
2. Or use browser DevTools mobile emulation
3. Check:
   - [ ] Single column layout
   - [ ] Payment options in 1 column
   - [ ] Touch-friendly buttons
   - [ ] No horizontal scroll

---

## 🐛 Step 9: Test Error Scenarios

### 9.1 Test Without Selection
1. Don't select any payment method
2. Click "Complete Payment"
3. Expected: Button should be disabled

### 9.2 Test Duplicate Payment
1. Complete a payment successfully
2. Go back to checkout page for same appointment
3. Expected: Should redirect with message "already paid"

### 9.3 Test Wrong User
1. Login as different patient
2. Try to access checkout URL of another user's appointment
3. Expected: Permission denied, redirect to my appointments

### 9.4 Test Network Error
1. Open browser DevTools (F12)
2. Go to Network tab
3. Set throttling to "Offline"
4. Try to complete payment
5. Expected: Error alert appears

---

## 🎯 Step 10: Test Different Payment Methods

Test the flow with each payment method category:

### Test 1: Credit Card
- [ ] Select Visa
- [ ] Complete payment
- [ ] Verify receipt shows "Visa"

### Test 2: Digital Wallet
- [ ] Select Google Pay
- [ ] Complete payment
- [ ] Verify receipt shows "Google Pay"

### Test 3: UPI
- [ ] Select PhonePe
- [ ] Complete payment
- [ ] Verify receipt shows "PhonePe"

### Test 4: Bank Transfer
- [ ] Select IMPS
- [ ] Complete payment
- [ ] Verify receipt shows "IMPS"

### Test 5: BNPL
- [ ] Select ZestMoney
- [ ] Complete payment
- [ ] Verify receipt shows "ZestMoney"

---

## 📊 Expected Results Summary

### ✅ Successful Test Checklist

- [ ] Checkout page loads correctly
- [ ] All 17 payment options visible
- [ ] Payment selection works
- [ ] Hover effects work
- [ ] Complete payment button enables/disables
- [ ] Processing overlay shows for 2 seconds
- [ ] Success modal appears with correct data
- [ ] Countdown works (3 seconds)
- [ ] Auto-redirect to my appointments
- [ ] Appointment status = "Confirmed"
- [ ] Payment record created in database
- [ ] Billing marked as paid
- [ ] Responsive design works on all screen sizes
- [ ] Error handling works correctly

---

## 🔍 Debugging Tips

### Issue: Checkout page doesn't load
**Check:**
- Is user logged in?
- Does appointment exist?
- Is appointment owned by current user?

**Solution:**
```bash
# Check in Django shell
python manage.py shell
>>> from appointment.models import Appointment
>>> Appointment.objects.filter(id=YOUR_ID).first()
```

### Issue: Payment button stays disabled
**Check:**
- Did you click on a payment option?
- Check browser console for JavaScript errors

**Solution:**
- Open DevTools (F12)
- Check Console tab for errors
- Verify JavaScript is enabled

### Issue: AJAX request fails
**Check:**
- Is CSRF token present?
- Is server running?
- Check Network tab in DevTools

**Solution:**
```javascript
// In browser console
console.log(document.querySelector('[name=csrfmiddlewaretoken]').value);
```

### Issue: Success modal doesn't show
**Check:**
- Did backend return success response?
- Check Network tab for response

**Solution:**
- Open DevTools → Network tab
- Find "process_payment" request
- Check response JSON

---

## 📈 Performance Benchmarks

### Expected Timings:
- Page load: < 1 second
- Payment selection: Instant
- Processing animation: 2 seconds
- AJAX request: < 500ms
- Success modal: Instant
- Redirect countdown: 3 seconds
- **Total flow:** ~6 seconds

---

## 🎉 Success Criteria

Your checkout system is working correctly if:

1. ✅ All 17 payment options are visible and selectable
2. ✅ Processing animation shows for exactly 2 seconds
3. ✅ Success modal displays correct booking details
4. ✅ Auto-redirect works after 3 seconds
5. ✅ Appointment status changes to "Confirmed"
6. ✅ Payment record is created in database
7. ✅ Responsive design works on all devices
8. ✅ Error handling prevents duplicate payments

---

## 📞 Need Help?

If you encounter issues:

1. **Check Django logs:**
   ```bash
   # In terminal where server is running
   # Look for error messages
   ```

2. **Check browser console:**
   - Press F12
   - Go to Console tab
   - Look for JavaScript errors

3. **Check Network requests:**
   - Press F12
   - Go to Network tab
   - Find failed requests

4. **Contact support:**
   - Email: care@vitalbook.in
   - Phone: +91 98765 43210

---

**Happy Testing! 🚀**

*VitalBook Checkout System v1.0*
*Last Updated: April 3, 2026*
