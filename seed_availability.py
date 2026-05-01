import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hospital_project.settings')
django.setup()

from appointment.models import Doctor, Availability

DAY_MAP = {
    'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6,
    'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6
}

def parse_days(day_str):
    days = set()
    parts = day_str.replace(' ', '').split(',')
    for part in parts:
        if '-' in part:
            start_str, end_str = part.split('-')
            start_idx = DAY_MAP[start_str[:3]]
            end_idx = DAY_MAP[end_str[:3]]
            if start_idx <= end_idx:
                for i in range(start_idx, end_idx + 1):
                    days.add(i)
            else:
                # Wrap around (e.g. Sat-Mon)
                for i in range(start_idx, 7):
                    days.add(i)
                for i in range(0, end_idx + 1):
                    days.add(i)
        else:
            days.add(DAY_MAP[part[:3]])
    return days

def parse_time(time_str):
    try:
        # e.g., "9:00 AM" or "10:00 AM"
        return datetime.strptime(time_str.strip(), '%I:%M %p').time()
    except ValueError:
        # Try without minutes?
        return datetime.strptime(time_str.strip(), '%I %p').time()

def run():
    doctors = Doctor.objects.all()
    created_count = 0
    for doc in doctors:
        if not doc.available_days or not doc.available_time:
            continue
            
        try:
            days = parse_days(doc.available_days)
            times = doc.available_time.split('-')
            if len(times) != 2:
                print(f"Skipping {doc.name}: Invalid time format {doc.available_time}")
                continue
                
            start_time = parse_time(times[0])
            end_time = parse_time(times[1])
            
            for day in days:
                _, created = Availability.objects.get_or_create(
                    doctor=doc,
                    day=day,
                    defaults={'start_time': start_time, 'end_time': end_time}
                )
                if created:
                    created_count += 1
        except Exception as e:
            print(f"Error parsing for {doc.name} (Days: {doc.available_days}, Time: {doc.available_time}): {e}")

    print(f"Successfully created {created_count} Availability records.")

if __name__ == '__main__':
    run()
