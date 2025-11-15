from django.db import models
from medical_tests.models import MedicalTestInsurance
from patient.models import Patient
from utils.base_models import BaseModel


class MedicalTestPrescriptionGroup(BaseModel):
    date = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    tamin_tracking_code = models.CharField(max_length=100, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    tamin_id = models.CharField(max_length=100, null=True, blank=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_medical_test_prescription_groups",
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["patient", "code"]),
        ]


class MedicalTestPrescriptionItem(BaseModel):
    group = models.ForeignKey(
        MedicalTestPrescriptionGroup,
        on_delete=models.CASCADE,
        related_name="presc_items",
    )
    test = models.ForeignKey(MedicalTestInsurance, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.test} - {self.group}"


class MedicalTestFavoriteGroup(BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]


class MedicalTestFavoriteItem(BaseModel):
    group = models.ForeignKey(
        MedicalTestFavoriteGroup, on_delete=models.CASCADE, related_name="items"
    )
    test = models.ForeignKey(MedicalTestInsurance, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.medicine} - {self.group}"
