"""
One-time cleanup: strips 'Dr. ' prefix from doctor names in database
so templates can safely display 'Dr. {{ doctor.name }}' without duplication.

Run once: python manage.py fix_doctor_names
"""

from django.core.management.base import BaseCommand
from appointment.models import Doctor


class Command(BaseCommand):
    help = 'Fix "Dr. Dr." bug by stripping duplicate prefix from doctor names'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Fixing doctor names...')
        fixed = 0
        for doc in Doctor.objects.all():
            name = doc.name.strip()
            # Strip any leading 'Dr.' or 'dr.' prefix
            for prefix in ['Dr.', 'Dr ', 'dr.', 'dr ']:
                if name.startswith(prefix):
                    name = name[len(prefix):].strip()
                    break
            # Remove extra spaces
            name = ' '.join(name.split())
            if name != doc.name:
                doc.name = name
                doc.save(update_fields=['name'])
                fixed += 1

        self.stdout.write(f'✅ Fixed {fixed} doctor names. All names are now clean.')
