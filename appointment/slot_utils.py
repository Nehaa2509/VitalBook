from datetime import datetime, timedelta
from .models import Availability, Appointment

from django.utils import timezone

def get_available_slots(doctor_id, selected_date):
    # 1. Get Doctor's availability for that specific day
    day_num = selected_date.weekday() # 0=Mon, 1=Tue...
    availability = Availability.objects.filter(doctor_id=doctor_id, day=day_num).first()
    
    if not availability:
        return []

    start = availability.start_time
    end = availability.end_time
    
    # 2. Get existing bookings for this doctor on this date
    # Exclude Cancelled to ensure Pending/Confirmed/Completed block the slot
    booked_slots = Appointment.objects.filter(
        doctor_id=doctor_id, 
        date=selected_date
    ).exclude(status='Cancelled').values_list('time', flat=True)

    # 3. Generate 30-minute slots
    slots = []
    current_time = datetime.combine(selected_date, start)
    end_time = datetime.combine(selected_date, end)

    # Filter out past times if selected date is today
    now = timezone.localtime(timezone.now())
    is_today = selected_date == now.date()

    while current_time < end_time:
        time_obj = current_time.time()
        
        # Check if the slot is in the past
        is_past = is_today and time_obj <= now.time()

        # Only add to list if NOT already booked AND NOT in the past
        if not is_past and time_obj not in booked_slots:
            slots.append(time_obj.strftime('%I:%M %p'))
        
        current_time += timedelta(minutes=30)
    
    return slots
