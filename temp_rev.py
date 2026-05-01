import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from appointment.models import Payment
from django.db.models import Sum

doctor_revenue = Payment.objects.filter(payment_status='Completed').values('appointment__doctor__name').annotate(total=Sum('amount')).order_by('-total')

print('\n--- Revenue Breakdown by Doctor ---')
for dr in doctor_revenue:
    print(f"- Dr. {dr['appointment__doctor__name']}: Rs. {dr['total']}")
