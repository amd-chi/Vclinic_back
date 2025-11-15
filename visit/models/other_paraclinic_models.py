from django.db import models
from other_paraclinic_services.models import OtherParaclinicService
from patient.models import Patient
from utils.base_models import BaseModel


class OtherParaclinicServicesPrescriptionGroup(BaseModel):
    date = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    tamin_tracking_code = models.CharField(max_length=100, null=True, blank=True)
    tamin_id = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_other_paraclinic_prescription_groups",
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]


class OtherParaclinicServicesPrescriptionItem(BaseModel):
    group = models.ForeignKey(
        OtherParaclinicServicesPrescriptionGroup,
        on_delete=models.CASCADE,
        related_name="presc_items",
    )
    service = models.ForeignKey(OtherParaclinicService, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.imaging} - {self.group}"


class OtherParaclinicFavoriteGroup(BaseModel):
    name = models.CharField(max_length=255)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]


class OtherParaclinicFavoriteItem(BaseModel):
    group = models.ForeignKey(
        OtherParaclinicFavoriteGroup, on_delete=models.CASCADE, related_name="items"
    )
    service = models.ForeignKey(OtherParaclinicService, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.item} - {self.group}"
