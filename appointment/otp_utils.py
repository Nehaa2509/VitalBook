"""
OTP utility functions for VitalBook.
Handles email and SMS OTP sending.
"""
from django.conf import settings
from .otp_email import send_otp_email


def send_email_otp(user, otp):
    """Send OTP via email."""
    return send_otp_email(user.email, otp, user.get_full_name() or user.username)


def send_mobile_otp(mobile_number, otp):
    """Send OTP via SMS using Twilio."""
    try:
        from twilio.rest import Client
        
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        message = client.messages.create(
            body=f'Your VitalBook OTP is: {otp}. Valid for 10 minutes.',
            from_=settings.TWILIO_PHONE_NUMBER,
            to=mobile_number
        )
        
        return True
    except Exception as e:
        print(f"Error sending mobile OTP: {e}")
        return False
