from appointment.models import Specialization

# Delete existing specializations
print(f"Deleting {Specialization.objects.count()} existing specializations...")
Specialization.objects.all().delete()

# Create new specializations
specs = [
    {
        "name": "Cardiology",
        "description": "Comprehensive heart care including diagnostics, intervention, and rehabilitation.",
        "icon": "heartbeat"
    },
    {
        "name": "Neurology",
        "description": "Expert treatment for disorders of the brain, spine, and nervous system.",
        "icon": "brain"
    },
    {
        "name": "Orthopedics",
        "description": "Advanced care for bones, joints, muscles, and sports injuries.",
        "icon": "bone"
    },
    {
        "name": "General Medicine",
        "description": "Primary healthcare and diagnosis for common illnesses and chronic conditions.",
        "icon": "stethoscope"
    },
    {
        "name": "Pediatrics",
        "description": "Specialized medical care for infants, children, and adolescents.",
        "icon": "baby"
    },
    {
        "name": "Dermatology",
        "description": "Comprehensive skin care, treatment for acne, eczema, and cosmetic procedures.",
        "icon": "allergies"
    }
]

for spec_data in specs:
    Specialization.objects.create(**spec_data)
    print(f"Created: {spec_data['name']}")

print(f"Successfully created {Specialization.objects.count()} specializations.")
