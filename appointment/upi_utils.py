"""
VitalBook — Cashfree UPI Payment Utilities
==========================================
Handles order creation, payment verification, and webhook signature
validation for the Cashfree payment gateway (UPI / PhonePe / GPay / Paytm).

Sign up free at https://merchant.cashfree.com/merchants/signup
Then add CASHFREE_APP_ID and CASHFREE_SECRET_KEY to your .env file.
"""
import requests
import hashlib
import hmac
import base64
import uuid
import time
from django.conf import settings

# ── Cashfree API endpoints ──────────────────────────────────────────────────
CASHFREE_BASE_URL = {
    'TEST': 'https://sandbox.cashfree.com/pg',
    'PROD': 'https://api.cashfree.com/pg',
}


def _base_url():
    env = getattr(settings, 'CASHFREE_ENV', 'TEST')
    return CASHFREE_BASE_URL.get(env, CASHFREE_BASE_URL['TEST'])


def _headers():
    """Return required Cashfree API request headers."""
    return {
        'Content-Type': 'application/json',
        'x-api-version': '2023-08-01',
        'x-client-id': getattr(settings, 'CASHFREE_APP_ID', ''),
        'x-client-secret': getattr(settings, 'CASHFREE_SECRET_KEY', ''),
    }


def create_upi_order(appointment):
    """
    Create a Cashfree payment order for a given Appointment.
    Returns a dict with keys: success, order_id, payment_session_id, error.
    """
    timestamp = int(time.time())
    order_id = f"VB_{appointment.id}_{timestamp}"
    amount = float(appointment.doctor.consultation_fee)

    # Phone is required by Cashfree; fall back to a placeholder if blank
    phone = getattr(appointment.patient, 'phone', '') or '9999999999'
    # Strip non-digits and ensure at minimum 10 digits
    phone_digits = ''.join(filter(str.isdigit, str(phone)))
    if len(phone_digits) < 10:
        phone_digits = '9999999999'
    phone_digits = phone_digits[-10:]  # Keep last 10 digits

    payload = {
        'order_id': order_id,
        'order_amount': amount,
        'order_currency': 'INR',
        'customer_details': {
            'customer_id': f'patient_{appointment.patient.user.id}',
            'customer_name': (
                appointment.patient.user.get_full_name()
                or appointment.patient.user.username
            ),
            'customer_email': appointment.patient.user.email,
            'customer_phone': phone_digits,
        },
        'order_meta': {
            'return_url': (
                f'http://127.0.0.1:8000/payment/verify/'
                f'?order_id={order_id}&appointment_id={appointment.id}'
            ),
            'notify_url': 'http://127.0.0.1:8000/payment/webhook/',
            'payment_methods': 'upi',
        },
        'order_note': f'VitalBook — Dr. {appointment.doctor.name} on {appointment.date}',
    }

    try:
        print("=== CASHFREE DEBUG START ===")
        print(f"Using App ID: {getattr(settings, 'CASHFREE_APP_ID', '')}")
        print(f"URL: {_base_url()}/orders")
        print(f"Payload: {payload}")
        print("Headers: ", _headers())
        
        response = requests.post(
            f'{_base_url()}/orders',
            headers=_headers(),
            json=payload,
            timeout=10,
        )
        data = response.json()
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {data}")
        print("=== CASHFREE DEBUG END ===")

        if response.status_code == 200:
            return {
                'success': True,
                'order_id': order_id,
                'payment_session_id': data.get('payment_session_id', ''),
                'cf_order_id': data.get('cf_order_id', ''),
            }
        else:
            return {'success': False, 'error': str(data)}

    except Exception as exc:
        print(f"=== CASHFREE DEBUG END WITH EXCEPTION ===")
        print(f'[Cashfree] Exception during order creation: {exc}')
        return {'success': False, 'error': str(exc)}


def create_cashfree_cancellation_order(appointment):
    """
    Create a Cashfree payment order for the ₹200 late-cancellation fee.
    Returns a dict with keys: success, order_id, payment_session_id, error.
    """
    timestamp = int(time.time())
    order_id  = f"VBCANCEL_{appointment.id}_{timestamp}"
    amount    = 200.00  # Fixed ₹200 cancellation fee

    phone = getattr(appointment.patient, 'phone', '') or '9999999999'
    phone_digits = ''.join(filter(str.isdigit, str(phone)))
    if len(phone_digits) < 10:
        phone_digits = '9999999999'
    phone_digits = phone_digits[-10:]

    payload = {
        'order_id':       order_id,
        'order_amount':   amount,
        'order_currency': 'INR',
        'customer_details': {
            'customer_id':    f'patient_{appointment.patient.user.id}',
            'customer_name':  (
                appointment.patient.user.get_full_name()
                or appointment.patient.user.username
            ),
            'customer_email': appointment.patient.user.email,
            'customer_phone': phone_digits,
        },
        'order_meta': {
            'return_url': (
                f'http://127.0.0.1:8000/cancel/verify/{appointment.id}/'
                f'?order_id={order_id}'
            ),
            'payment_methods': 'upi',
        },
        'order_note': f'VitalBook — Cancellation Fee for Appt #{appointment.id}',
    }

    try:
        response = requests.post(
            f'{_base_url()}/orders',
            headers=_headers(),
            json=payload,
            timeout=10,
        )
        data = response.json()
        if response.status_code == 200:
            return {
                'success':             True,
                'order_id':            order_id,
                'payment_session_id':  data.get('payment_session_id', ''),
            }
        return {'success': False, 'error': str(data)}
    except Exception as exc:
        print(f'[Cashfree] Cancellation order error: {exc}')
        return {'success': False, 'error': str(exc)}


def verify_upi_payment(order_id):

    """
    Verify payment status by fetching the order from Cashfree.
    Returns a dict with keys: success, status, amount, payment_method, data.
    """
    try:
        response = requests.get(
            f'{_base_url()}/orders/{order_id}',
            headers=_headers(),
            timeout=10,
        )
        data = response.json()
        order_status = data.get('order_status', '')

        return {
            'success': order_status == 'PAID',
            'status': order_status,
            'order_id': order_id,
            'amount': data.get('order_amount'),
            'payment_method': 'UPI',
            'data': data,
        }

    except Exception as exc:
        print(f'[Cashfree] Verification error: {exc}')
        return {'success': False, 'status': 'ERROR', 'error': str(exc)}


def verify_webhook_signature(raw_body: str, timestamp: str, signature: str) -> bool:
    """
    Validate a Cashfree webhook notification signature.
    See: https://docs.cashfree.com/docs/webhook-authentication
    """
    try:
        secret = getattr(settings, 'CASHFREE_SECRET_KEY', '')
        message = timestamp + raw_body
        computed = hmac.new(
            secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256,
        ).digest()
        computed_b64 = base64.b64encode(computed).decode('utf-8')
        return computed_b64 == signature
    except Exception:
        return False
