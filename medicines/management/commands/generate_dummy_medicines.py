from django.core.management.base import BaseCommand
from medicines.models import Medicine


class Command(BaseCommand):
    help = "Generate dummy data for Medicine model"

    def handle(self, *args, **kwargs):
        # Generate 10 medicines
        medicines_data = [
            {
                "name": "Paracetamol",
                "code": "MED001",
                "description": "Pain reliever and fever reducer",
                "dosage_form": "Tablet",
            },
            {
                "name": "Ibuprofen",
                "code": "MED002",
                "description": "Nonsteroidal anti-inflammatory drug (NSAID)",
                "dosage_form": "Tablet",
            },
            {
                "name": "Amoxicillin",
                "code": "MED003",
                "description": "Antibiotic",
                "dosage_form": "Tablet",
            },
            {
                "name": "Lisinopril",
                "code": "MED004",
                "description": "Blood pressure medication",
                "dosage_form": "Tablet",
            },
            {
                "name": "Atorvastatin",
                "code": "MED005",
                "description": "Cholesterol-lowering medication",
                "dosage_form": "Tablet",
            },
            {
                "name": "Omeprazole",
                "code": "MED006",
                "description": "Proton pump inhibitor (PPI)",
                "dosage_form": "Tablet",
            },
            {
                "name": "Metformin",
                "code": "MED007",
                "description": "Diabetes medication",
                "dosage_form": "Tablet",
            },
            {
                "name": "Cetirizine",
                "code": "MED008",
                "description": "Antihistamine",
                "dosage_form": "Tablet",
            },
            {
                "name": "Albuterol",
                "code": "MED009",
                "description": "Bronchodilator",
                "dosage_form": "Tablet",
            },
            {
                "name": "Warfarin",
                "code": "MED010",
                "description": "Anticoagulant",
                "dosage_form": "Tablet",
            },
        ]

        # Save the medicines to the database
        for medicine_data in medicines_data:
            Medicine.objects.create(**medicine_data)
        self.stdout.write(self.style.SUCCESS(f"Successfully created Medicines"))
