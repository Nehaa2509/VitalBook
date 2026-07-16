import os
import requests
import json
from django.conf import settings

def send_transactional_email(to_email, subject, html_content, to_name=""):
    """
    Sends transactional email using Brevo's transactional HTTP API (v3).
    Does not raise exceptions. Returns True on success, False on failure.
    """
    api_key = os.environ.get('BREVO_API_KEY') or getattr(settings, 'BREVO_API_KEY', '')
    if not api_key:
        print("[ERROR] BREVO_API_KEY not configured.")
        return False

    sender_email = os.environ.get('BREVO_SENDER_EMAIL') or getattr(settings, 'BREVO_SENDER_EMAIL', 'noreply@vitalbook.in')
    sender_name = os.environ.get('BREVO_SENDER_NAME') or getattr(settings, 'BREVO_SENDER_NAME', 'VitalBook')

    url = "https://api.brevo.com/v3/smtp/email"
    headers = {
        "api-key": api_key,
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email
        },
        "to": [
            {
                "email": to_email,
                "name": to_name or to_email
            }
        ],
        "subject": subject,
        "htmlContent": html_content
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
        if response.status_code in [200, 201, 202]:
            print(f"[OK] Email '{subject}' sent successfully to {to_email} via Brevo HTTP API.")
            return True
        else:
            print(f"[ERROR] Brevo API error {response.status_code}: {response.text}")
            return False
    except requests.RequestException as e:
        print(f"[ERROR] Connection to Brevo failed: {e}")
        return False


def send_otp_email(to_email, otp, to_name=""):
    """
    Sends OTP verification email.
    """
    html_content = f'''<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;background:#f4f6f9;padding:40px 0;margin:0;">
<div style="max-width:500px;margin:0 auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
    <div style="background:linear-gradient(135deg,#0d6efd,#0056b3);padding:32px;text-align:center;">
        <h1 style="color:white;margin:0;font-size:22px;font-weight:700;">VitalBook</h1>
    </div>
    <div style="padding:36px 32px;text-align:center;">
        <h2 style="color:#0f172a;font-size:20px;margin:0 0 8px;">Verify Your Email</h2>
        <p style="color:#64748b;font-size:14px;margin:0 0 28px;">
            Hi {to_name or 'there'}, use the code below to verify your account.
        </p>
        <div style="background:#f0f7ff;border:2px dashed #0d6efd;border-radius:12px;padding:24px;margin:0 0 24px;">
            <p style="color:#64748b;font-size:12px;margin:0 0 8px;text-transform:uppercase;letter-spacing:1px;font-weight:600;">Your OTP Code</p>
            <div style="font-size:42px;font-weight:800;color:#0d6efd;letter-spacing:12px;font-family:monospace;">
                {otp}
            </div>
        </div>
        <p style="color:#94a3b8;font-size:13px;margin:0 0 6px;">
            ⏰ This code expires in <strong>10 minutes</strong>
        </p>
        <p style="color:#94a3b8;font-size:12px;margin:0;">
            🔒 Never share this code with anyone
        </p>
    </div>
</div>
</body>
</html>'''
    return send_transactional_email(
        to_email=to_email,
        subject="🔐 VitalBook — Your OTP Verification Code",
        html_content=html_content,
        to_name=to_name
    )
