from django.db import models

from patient.models.patient_models import Patient
from utils.base_models import BaseModel


class MedicalImagingInsurance(models.Model):
    name = models.CharField(max_length=511)
    is_insured = models.BooleanField(default=False)
    tamin_json = models.JSONField(null=True, blank=True)
    tamin_id = models.IntegerField(null=True, blank=True, unique=True)
    code = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return self.name + (" (Insured)" if self.is_insured else "")

    class Meta:
        indexes = [
            models.Index(fields=["name", "tamin_id"]),
        ]


class MedicalImagingCenter(models.Model):
    name = models.CharField(max_length=511)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Imaging Centers"
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class MedicalImagingResult(BaseModel):
    imaging = models.ForeignKey(MedicalImagingInsurance, on_delete=models.CASCADE)
    date = models.DateField()
    patient = models.ForeignKey(Patient, on_delete=models.RESTRICT)
    comment = models.TextField()
    imaging_center = models.ForeignKey(
        MedicalImagingCenter, on_delete=models.RESTRICT, null=True, blank=True
    )
    url = models.URLField(blank=True, null=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_medical_imaging_results",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"ID: {self.id} - {self.date} - {self.imaging_center}"

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]
