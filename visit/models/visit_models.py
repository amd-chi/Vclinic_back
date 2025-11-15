from django.db import models
from patient.models import Patient
from utils.base_models import BaseModel


class Visit(BaseModel):
    date = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    # comment = models.TextField()
    fee = models.IntegerField()
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_visits",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.date} - {self.patient}"

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]


class VisitInsurance(BaseModel):
    date = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    comment = models.TextField()
    tamin_tracking_code = models.CharField(max_length=100)

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]


class VisitPrice(models.Model):
    price = models.IntegerField(default=400000)

    def __str__(self):
        return f"Visit Price: {self.price} toman"


class ClinicData(models.Model):
    doctor_name = models.CharField(max_length=255)
    clinic_address = models.CharField(max_length=100)
    clinic_phone = models.CharField(max_length=100)
    medical_education_number = models.CharField(max_length=100)
    speciality = models.CharField(max_length=100)
    # clinic_email = models.EmailField(max_length=100)
    # clinic_website = models.URLField(max_length=100)

    def __str__(self):
        return f"{self.clinic_name} - {self.clinic_address} - {self.clinic_phone}"
