"""
VitalBook — Django Forms
Server-side validation as a safety net behind the JS client-side checks.
"""
import datetime
from django import forms
from .models import Patient, Appointment, Availability


class PatientProfileForm(forms.ModelForm):
    """
    Patient profile update form.
    Max date is intentionally NOT set in Python — JavaScript sets it dynamically
    on every page load so it never goes stale.
    """
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(
            format='%Y-%m-%d',
            attrs={
                'type': 'date',
                'id': 'dob-input',
            }
        ),
        # Accept all common ISO and locale formats
        input_formats=['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d'],
    )

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob is None:
            return dob
        today = datetime.date.today()
        if dob > today:
            raise forms.ValidationError('Date of birth cannot be in the future.')
        if dob.year < 1900:
            raise forms.ValidationError('Please enter a valid Date of Birth (year must be 1900 or later).')
        return dob

    class Meta:
        model = Patient
        fields = ['name', 'phone', 'date_of_birth', 'gender', 'blood_group',
                  'address', 'emergency_contact', 'medical_history']


class AppointmentForm(forms.ModelForm):
    time = forms.TimeField(input_formats=['%I:%M %p', '%H:%M:%S', '%H:%M'])

    class Meta:
        model = Appointment
        fields = ['date', 'time', 'reason', 'symptoms']

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        
        # We assume 'doctor' is injected into the form instance before validation
        doctor = getattr(self.instance, 'doctor', None)

        if doctor and date and time:
            # 1. Check if the Doctor works on this Day of the Week
            day_of_week = date.weekday() # Monday is 0, Sunday is 6
            avail = Availability.objects.filter(doctor=doctor, day=day_of_week).first()

            if not avail:
                raise forms.ValidationError(f"Dr. {doctor.name} does not consult on {date.strftime('%A')}.")

            # 2. Check if the Time is within the Doctor's range
            if not (avail.start_time <= time <= avail.end_time):
                raise forms.ValidationError(
                    f"Dr. {doctor.name} is only available between {avail.start_time.strftime('%I:%M %p')} and {avail.end_time.strftime('%I:%M %p')} on {date.strftime('%A')}s."
                )

            # 3. Prevent Double Booking (Same Doctor, Date, and Time)
            # We exclude 'Cancelled' appointments
            exists = Appointment.objects.filter(
                doctor=doctor, 
                date=date, 
                time=time
            ).exclude(status='Cancelled').exists()

            if exists:
                raise forms.ValidationError("This slot is already booked. Please select a different time.")

        return cleaned_data
