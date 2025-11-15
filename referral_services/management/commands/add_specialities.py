from django.core.management.base import BaseCommand

from referral_services.models import DoctorSpeciality


class Command(BaseCommand):
    help = "Imports some specialities into Unit model"

    def handle(self, *args, **kwargs):
        medical_specialties = [
            "General Practice",
            "Cardiology",
            "Psychiatry",
            "Ophthalmology",
            "Orthopedics",
            "Pathology",
            "Dermatology",
            "Gastroenterology",
            "Pediatrics",
            "Obstetrics and Gynecology",
            "General Surgery",
            "Neurosurgery",
            "Otolaryngology (ENT)",
            "Pulmonology",
            "Infectious Disease",
            "Rheumatology",
            "Oncology",
            "Dentistry",
            "Psychology",
            "Urology",
        ]

        for spec in medical_specialties:
            DoctorSpeciality.objects.get_or_create(name=spec)

        self.stdout.write(
            self.style.SUCCESS("Medical specialities successfully imported")
        )
