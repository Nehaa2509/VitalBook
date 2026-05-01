from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Shows how to set up automatic reminders'

    def handle(self, *args, **kwargs):
        self.stdout.write('''
To run reminders automatically every hour, add this to Windows Task Scheduler or use:

Option 1 - Run manually:
    python manage.py send_hourly_reminders

Option 2 - Windows Task Scheduler:
    Program: python
    Arguments: manage.py send_hourly_reminders
    Start in: E:\\Sneha\\INTERSHIP\\hospital
    Trigger: Every 1 hour

Option 3 - Install django-crontab for automatic scheduling:
    pip install django-crontab

    In settings.py add:
    INSTALLED_APPS += ['django_crontab']
    CRONJOBS = [
        ('0 * * * *', 'django.core.management.call_command', ['send_hourly_reminders']),
    ]

    Then run:
    python manage.py crontab add
        ''')
