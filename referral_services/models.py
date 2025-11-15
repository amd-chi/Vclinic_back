from django.db import models

from patient.models.patient_models import Patient
from utils.base_models import BaseModel


class DoctorSpeciality(models.Model):
    name = models.CharField(max_length=255)


# Create your models here.
class Doctor(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(null=True, blank=True)
    speciality = models.ForeignKey(DoctorSpeciality, on_delete=models.CASCADE)
    # city = models.CharField(max_length=255)
    # country = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class ReferralDoctor(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    result_date = models.DateField(null=True, blank=True)
    result = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_referral_doctors",
        null=True,
        blank=True,
    )
