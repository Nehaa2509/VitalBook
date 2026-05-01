@echo off
cd E:\Sneha\INTERSHIP\hospital
call venv\Scripts\activate
python manage.py send_appointment_reminders >> reminders.log 2>&1
echo Reminders checked at %date% %time% >> reminders.log
