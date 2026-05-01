"""
One-time cleanup: Fixes "Dr. Dr. Name" by ensuring exactly one "Dr. " prefix.
Run: python manage.py fix_dr_prefix
"""

from django.core.management.base import BaseCommand
from appointment.models import Doctor
from django.db.models import F, Value
from django.db.models.functions import Concat, Substr


class Command(BaseCommand):
    help = 'Fix "Dr. Dr." duplication in doctor names'

    def handle(self, *args, **options):
        self.stdout.write('🔧 Fixing doctor name prefixes...')

        # 1. Strip ALL leading "Dr. " or "Dr " prefixes first (normalize to clean name)
        # We use a loop to handle potential multiple prefixes like "Dr. Dr. Dr. "
        max_passes = 5
        for _ in range(max_passes):
            updated = Doctor.objects.filter(name__startswith='Dr. ').update(
                name=Substr('name', 5)  # Remove "Dr. " (4 chars + space)
            )
            updated += Doctor.objects.filter(name__startswith='Dr ').update(
                name=Substr('name', 4)
            )
            if updated == 0:
                break

        # 2. Now add exactly ONE "Dr. " prefix to all names
        Doctor.objects.exclude(name__startswith='Dr. ').update(
            name=Concat(Value('Dr. '), F('name'))
        )

        # Verification
        total = Doctor.objects.count()
        clean = Doctor.objects.filter(name__startswith='Dr. ').count()
        self.stdout.write(self.style.SUCCESS(
            f'✅ Done. {clean}/{total} doctors now have exactly one "Dr. " prefix.'
        ))
