from patient.models.patient_models import Patient
from utils.base_models import BaseModel
from django.db import models


class ParaclinicResult(BaseModel):
    title = models.CharField(max_length=255)
    date = models.DateField()
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    comment = models.TextField()
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_paraclinic_results",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"ID: {self.id} - {self.date} - {self.title}"

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]
