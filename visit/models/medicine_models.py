from django.db import models
from medicines.models import Medicine
from patient.models import Patient
from utils.base_models import BaseModel


class MedicineAmount(models.Model):
    concept = models.CharField(max_length=300)
    category = models.CharField(max_length=100)
    tamin_json = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.concept


class MedicineInstruction(models.Model):
    concept = models.CharField(max_length=300)
    tamin_json = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.concept


class MedicineUsage(models.Model):
    concept = models.CharField(max_length=300)
    tamin_json = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.concept


class MedicineRepeat(models.Model):
    concept = models.CharField(max_length=300)
    tamin_json = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.concept


class MedicinePrescriptionGroup(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    comment = models.TextField(blank=True, null=True)
    tamin_tracking_code = models.CharField(max_length=100, null=True, blank=True)
    tamin_id = models.CharField(max_length=100, null=True, blank=True)
    tamin_response = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_medicine_prescription_groups",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.patient} - {self.date}"

    class Meta:
        indexes = [
            models.Index(fields=["patient", "tamin_id"]),
        ]


class MedicinePrescriptionItem(BaseModel):
    group = models.ForeignKey(
        MedicinePrescriptionGroup, on_delete=models.CASCADE, related_name="presc_items"
    )
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    amount = models.ForeignKey(MedicineAmount, on_delete=models.CASCADE)
    instruction = models.ForeignKey(MedicineInstruction, on_delete=models.CASCADE)
    usage = models.ForeignKey(
        MedicineUsage, on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)
    repeat = models.ForeignKey(
        MedicineRepeat, on_delete=models.CASCADE, null=True, blank=True
    )
    repeat_count = models.PositiveIntegerField(null=True, blank=True)
    doDate = models.DateField(null=True, blank=True)
    is_note = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.medicine} - {self.group}"


class MedicineFavoriteGroup(BaseModel):
    name = models.CharField(max_length=255)


class MedicinePrescriptionFavoriteItem(BaseModel):
    group = models.ForeignKey(
        MedicineFavoriteGroup, on_delete=models.CASCADE, related_name="items"
    )
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    amount = models.ForeignKey(MedicineAmount, on_delete=models.CASCADE)
    instruction = models.ForeignKey(MedicineInstruction, on_delete=models.CASCADE)
    usage = models.ForeignKey(
        MedicineUsage, on_delete=models.CASCADE, null=True, blank=True
    )
    quantity = models.PositiveIntegerField()
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.medicine} - {self.group}"
