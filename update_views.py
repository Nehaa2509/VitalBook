import re

with open('E:\\Sneha\\INTERSHIP\\hospital\\appointment\\views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add imports if not exist
if 'import random' not in content:
    content = 'import random\nimport string\n' + content

# Regex for register
register_pattern = re.compile(r'def register\(request\):.*?(?=\n\n\n|\Z|def user_login)', re.DOTALL)
register_replacement = '''def register(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        # Validations
        if not all([first_name, username, email, password1, password2]):
            messages.error(request, 'All fields are required!')
            return render(request, 'appointment/register.html')

        if password1 != password2:
            messages.error(request, 'Passwords do not match!')
            return render(request, 'appointment/register.html')

        if len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters!')
            return render(request, 'appointment/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken!')
            return render(request, 'appointment/register.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'appointment/register.html')

        # Generate 6-digit OTP
        otp = ''.join(random.choices(string.digits, k=6))

        # Store in session
        request.session['reg_otp'] = otp
        request.session['reg_email'] = email
        request.session['reg_username'] = username
        request.session['reg_password'] = password1
        request.session['reg_first_name'] = first_name
        request.session['reg_last_name'] = last_name
        request.session['otp_created_at'] = str(timezone.now())

        # Print to terminal for testing
        print(f'\\n{"="*40}')
        print(f'OTP for {email}: {otp}')
        print(f'{"="*40}\\n')

        # Send real email
        try:
            send_mail(
                subject='🔐 VitalBook — Your OTP Verification Code',
                message=f\\'''
Dear {first_name},

Your OTP verification code for VitalBook is:

{otp}

This code is valid for 10 minutes.
Do not share this code with anyone.

If you did not request this, please ignore this email.

Best regards,
Team VitalBook
                \\''',
                from_email=django_settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
                html_message=f\\'''
<!DOCTYPE html>
<html>
<body style="font-family:Inter,Arial,sans-serif;background:#f4f6f9;padding:40px 0;margin:0;">
<div style="max-width:500px;margin:0 auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);">

    <!-- Header -->
    <div style="background:linear-gradient(135deg,#0d6efd,#0056b3);padding:32px;text-align:center;">
        <div style="background:#f97316;width:48px;height:48px;border-radius:12px;margin:0 auto 12px;display:flex;align-items:center;justify-content:center;font-size:24px;font-weight:900;color:white;">+</div>
        <h1 style="color:white;margin:0;font-size:22px;font-weight:700;">VitalBook</h1>
        <p style="color:rgba(255,255,255,0.8);margin:6px 0 0;font-size:13px;">Your Health, Our Priority</p>
    </div>

    <!-- Body -->
    <div style="padding:36px 32px;text-align:center;">
        <h2 style="color:#0f172a;font-size:20px;margin:0 0 8px;">Verify Your Email</h2>
        <p style="color:#64748b;font-size:14px;margin:0 0 28px;">
            Hi <strong>{first_name}</strong>, use the code below to verify your account.
        </p>

        <!-- OTP Box -->
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

    <!-- Footer -->
    <div style="background:#f8fafc;padding:20px;text-align:center;border-top:1px solid #e2e8f0;">
        <p style="color:#94a3b8;font-size:12px;margin:0;">
            © 2026 VitalBook. All rights reserved.<br>
            If you didn't create an account, ignore this email.
        </p>
    </div>

</div>
</body>
</html>
                \\'''
            )
            messages.success(request, f'OTP sent to {email}! Check your inbox.')
        except Exception as e:
            print(f'Email error: {e}')
            messages.warning(request, f'Could not send email. Check terminal for OTP: {otp}')

        return redirect('verify_otp')

    return render(request, 'appointment/register.html')'''
content = register_pattern.sub(register_replacement, content)

# Regex for verify_otp
verify_otp_pattern = re.compile(r'def verify_otp\(request\):.*?(?=\ndef resend_otp)', re.DOTALL)
verify_otp_replacement = '''def verify_otp(request):
    if not request.session.get('reg_otp'):
        messages.error(request, 'Session expired. Please register again.')
        return redirect('register')

    email = request.session.get('reg_email', '')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp', '').strip()
        stored_otp = request.session.get('reg_otp')
        otp_created_at = request.session.get('otp_created_at')

        # Check expiry (10 minutes)
        if otp_created_at:
            created_time = datetime.fromisoformat(otp_created_at.replace('+00:00', ''))
            if datetime.utcnow() > created_time.replace(tzinfo=None) + timedelta(minutes=10):
                messages.error(request, '⏰ OTP expired! Please register again.')
                # Clear session
                for key in ['reg_otp','reg_email','reg_username','reg_password','reg_first_name','reg_last_name','otp_created_at']:
                    request.session.pop(key, None)
                return redirect('register')

        if entered_otp == stored_otp:
            # Create the user
            try:
                user = User.objects.create_user(
                    username=request.session['reg_username'],
                    email=request.session['reg_email'],
                    password=request.session['reg_password'],
                    first_name=request.session['reg_first_name'],
                    last_name=request.session.get('reg_last_name', ''),
                )
                user.is_active = True
                user.save()

                # Create patient profile
                try:
                    Patient.objects.get_or_create(user=user)
                except:
                    pass

                # Clear session
                for key in ['reg_otp','reg_email','reg_username','reg_password','reg_first_name','reg_last_name','otp_created_at']:
                    request.session.pop(key, None)

                # Send welcome email
                try:
                    send_mail(
                        subject='🎉 Welcome to VitalBook!',
                        message=f'Welcome {user.first_name}! Your account has been verified.',
                        from_email=django_settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[user.email],
                        fail_silently=True,
                        html_message=f\\'''
<div style="font-family:Inter,Arial,sans-serif;max-width:500px;margin:0 auto;background:white;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.1);">
    <div style="background:linear-gradient(135deg,#0d6efd,#0056b3);padding:32px;text-align:center;">
        <h1 style="color:white;margin:0;">🎉 Welcome to VitalBook!</h1>
    </div>
    <div style="padding:32px;text-align:center;">
        <h2 style="color:#0f172a;">Hi {user.first_name}! 👋</h2>
        <p style="color:#64748b;">Your account has been successfully verified. You can now book appointments with top doctors.</p>
        <a href="http://127.0.0.1:8000/login/" style="background:#0d6efd;color:white;padding:12px 28px;border-radius:8px;text-decoration:none;font-weight:600;display:inline-block;margin-top:16px;">Login Now →</a>
    </div>
</div>
                        \\'''
                    )
                except:
                    pass

                messages.success(request, '✅ Account verified! Welcome to VitalBook.')
                return redirect('login')

            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            messages.error(request, '❌ Invalid OTP! Please try again.')

    # Mask email for display
    masked_email = email[:3] + '****' + email[email.find('@'):]

    return render(request, 'appointment/verify_otp.html', {
        'masked_email': masked_email,
    })
'''
content = verify_otp_pattern.sub(verify_otp_replacement, content)

# Regex for resend_otp
resend_otp_pattern = re.compile(r'def resend_otp\(request\):.*?(?=\n\n\n|\Z|@login_required)', re.DOTALL)
resend_otp_replacement = '''def resend_otp(request):
    email = request.session.get('reg_email')
    first_name = request.session.get('reg_first_name', 'User')

    if not email:
        messages.error(request, 'Session expired. Please register again.')
        return redirect('register')

    # Generate new OTP
    otp = ''.join(random.choices(string.digits, k=6))
    request.session['reg_otp'] = otp
    request.session['otp_created_at'] = str(timezone.now())

    print(f'\\nNew OTP for {email}: {otp}\\n')

    try:
        send_mail(
            subject='🔐 VitalBook — New OTP Code',
            message=f'Your new OTP is: {otp}. Valid for 10 minutes.',
            from_email=django_settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
            html_message=f\\'''
<div style="font-family:Arial,sans-serif;max-width:400px;margin:0 auto;padding:32px;text-align:center;">
    <h2 style="color:#0d6efd;">New OTP Code</h2>
    <div style="font-size:42px;font-weight:800;color:#0d6efd;letter-spacing:12px;background:#f0f7ff;padding:20px;border-radius:12px;margin:20px 0;">{otp}</div>
    <p style="color:#64748b;">Valid for 10 minutes. Do not share this code.</p>
</div>
            \\'''
        )
        messages.success(request, f'✅ New OTP sent to {email}!')
    except Exception as e:
        messages.warning(request, f'Email failed. OTP in terminal: {otp}')

    return redirect('verify_otp')'''

content = resend_otp_pattern.sub(resend_otp_replacement, content)

with open('E:\\Sneha\\INTERSHIP\\hospital\\appointment\\views.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Replacement complete.')
