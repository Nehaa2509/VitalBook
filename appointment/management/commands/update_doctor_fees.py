from django.core.management.base import BaseCommand
from appointment.models import Doctor


class Command(BaseCommand):
    help = 'Update doctor fees based on experience levels'

    def handle(self, *args, **kwargs):

        doctor_data = [
            # Junior Residents (3-9 years) - ₹200 to ₹400
            {
                'name': 'Vikram Singh',
                'experience': 5,
                'fee': 300,
                'level': 'Junior Resident'
            },
            {
                'name': 'Neha Patel',
                'experience': 8,
                'fee': 380,
                'level': 'Junior Resident'
            },

            # Consultants (10-19 years) - ₹400 to ₹700
            {
                'name': 'Rohan Sharma',
                'experience': 12,
                'fee': 550,
                'level': 'Consultant'
            },
            {
                'name': 'Priya Desai',
                'experience': 14,
                'fee': 650,
                'level': 'Consultant'
            },
            {
                'name': 'Rahul Verma',
                'experience': 17,
                'fee': 680,
                'level': 'Consultant'
            },
            {
                'name': 'Kabir Khan',
                'experience': 19,
                'fee': 700,
                'level': 'Consultant'
            },

            # Senior Consultants / HOD (20+ years) - ₹700 to ₹1000
            {
                'name': 'Sneha Reddy',
                'experience': 25,
                'fee': 850,
                'level': 'Senior Consultant'
            },
            {
                'name': 'Pooja Nair',
                'experience': 28,
                'fee': 900,
                'level': 'Senior Consultant / HOD'
            },
            {
                'name': 'Meera Iyer',
                'experience': 35,
                'fee': 950,
                'level': 'Senior Consultant / HOD'
            },
            {
                'name': 'Amit Joshi',
                'experience': 38,
                'fee': 1000,
                'level': 'Senior Consultant / HOD'
            },
        ]

        updated = 0
        not_found = []

        for data in doctor_data:
            try:
                # Try to find doctor by name (partial match)
                doctor = Doctor.objects.filter(
                    name__icontains=data['name']
                ).first()

                if doctor:
                    doctor.experience_years = data['experience']
                    doctor.consultation_fee = data['fee']
                    doctor.save()
                    updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✅ Updated Dr. {data['name']} | "
                            f"Experience: {data['experience']} yrs | "
                            f"Fee: ₹{data['fee']} | "
                            f"Level: {data['level']}"
                        )
                    )
                else:
                    not_found.append(data['name'])
                    self.stdout.write(
                        self.style.WARNING(
                            f"⚠️  Doctor not found: {data['name']}"
                        )
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error updating {data['name']}: {str(e)}")
                )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'✅ Updated: {updated} doctors'))
        if not_found:
            self.stdout.write(self.style.WARNING(f'⚠️  Not found: {", ".join(not_found)}'))
        self.stdout.write('='*50)
