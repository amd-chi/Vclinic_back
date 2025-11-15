from django.db import models
from medical_imaging.models import MedicalImagingCenter, MedicalImagingInsurance
from patient.models import Patient
from utils.base_models import BaseModel


class MedicalImagingPrescriptionGroup(BaseModel):
    date = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    tamin_tracking_code = models.CharField(max_length=100, null=True, blank=True)
    tamin_id = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_medical_imaging_prescription_groups",
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]


class MedicalImagingPrescriptionItem(BaseModel):
    group = models.ForeignKey(
        MedicalImagingPrescriptionGroup,
        on_delete=models.CASCADE,
        related_name="presc_items",
    )
    imaging = models.ForeignKey(MedicalImagingInsurance, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.imaging} - {self.group}"


class MedicalImagingFavoriteGroup(BaseModel):
    name = models.CharField(max_length=255)


class MedicalImagingFavoriteItem(BaseModel):
    group = models.ForeignKey(
        MedicalImagingFavoriteGroup, on_delete=models.CASCADE, related_name="items"
    )
    imaging = models.ForeignKey(MedicalImagingInsurance, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.medicine} - {self.group}"


SITE_CHOICES = [
    ("SPINE", "SPINE"),
    ("FEMURAL_NECK_RIGHT", "FEMURAL_NECK_RIGHT"),
    ("FEMURAL_NECK_LEFT", "FEMURAL_NECK_LEFT"),
    ("FEMURAL_NECK_MEAN", "FEMURAL_NECK_MEAN"),
    ("TOTAL_HIP_RIGHT", "TOTAL_HIP_RIGHT"),
    ("TOTAL_HIP_LEFT", "TOTAL_HIP_LEFT"),
    ("TOTAL_HIP_MEAN", "TOTAL_HIP_MEAN"),
    ("RADIUS", "RADIUS"),
]


PARAMETER_CHOICES = [
    ("T_SCORE", "T_SCORE"),
    ("Z_SCORE", "Z_SCORE"),
]


class BMDRecordItem(BaseModel):
    group = models.ForeignKey(
        "BMDRecordGroup", on_delete=models.CASCADE, related_name="items"
    )
    parameter = models.CharField(max_length=255, choices=PARAMETER_CHOICES)
    site = models.CharField(max_length=255, choices=SITE_CHOICES)
    value = models.FloatField()
    bmd = models.FloatField()
    comment = models.TextField(blank=True, null=True)
    delta_value = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.parameter} - {self.group}"


class BMDRecordGroup(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)

    date = models.DateField()
    center = models.ForeignKey(
        MedicalImagingCenter, on_delete=models.CASCADE, related_name="bmd_records"
    )
    comment = models.TextField(blank=True, null=True)
    major_osteoporotic_fracture_risk = models.FloatField(blank=True, null=True)
    hip_fracture_risk = models.FloatField(blank=True, null=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_bmd_record_groups",
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]
