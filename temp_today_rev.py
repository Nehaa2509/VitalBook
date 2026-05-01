import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from django.utils import timezone
from appointment.models import Appointment, Payment
from django.db.models import Sum

local_now = timezone.localtime(timezone.now())
today = local_now.date()

# Match the dashboard's calculation for "Today's Revenue"
todays_revenue_dashboard = (
    Appointment.objects
    .filter(date=today, status__in=['Confirmed', 'Completed'])
    .aggregate(total=Sum('doctor__consultation_fee'))['total'] or 0
)

# Also check completed payments strictly for today (actual payments made today)
todays_payments = (
    Payment.objects
    .filter(payment_status='Completed', payment_date__date=today)
    .aggregate(total=Sum('amount'))['total'] or 0
)

print(f"Today's Revenue (as per Dashboard - appointments scheduled for today): Rs. {todays_revenue_dashboard}")
print(f"Today's Actual Payments Received: Rs. {todays_payments}")
