from django.db import models
from patient.models import Patient
from utils.base_models import BaseModel

ihd_choices = {
    "CABG": "CABG",
    "STENT": "STENT",
    "Angiography": "Angiography",
}

retinopathy_choices = {
    "Normal": "Normal",
    "NPDR": "NPDR",
    "PDR": "PDR",
    "CSME": "CSME",
}

# eye_laser_choices = {
#     "Right": "Right",
#     "Left": "Left",
#     "Both": "Both",
# }

amputation_choices = {
    "Finger": "Finger",
    "Sims": "Sims",
    "Below-Knee": "Below-Knee",
    "Ante-Knee": "Ante-Knee",
}

pituitary_radiation = {
    "gKnife": "gKnife",
    "Conventional": "Conventional",
}

smoking_choices = {
    "Active": "Active",
    "Passive": "Passive",
    "Ex-smoker": "Ex-smoker",
}

fracture_choices = {
    "Neck-Femur": "Neck-Femur",
    "Lumbar-Spine": "Lumbar-Spine",
    "Colles": "Colles",
    "Other": "Other",
}

alcohol_choices = {
    "Social": "Social",
    "Regular": "Regular",
    "Heavy": "Heavy",
}


class PatientHistoryBasic(BaseModel):
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="basic_history"
    )
    aspirin = models.BooleanField(blank=True, null=True)
    statin = models.BooleanField(blank=True, null=True)
    ihd = models.CharField(max_length=255, choices=ihd_choices, blank=True, null=True)
    retinopathy = models.CharField(
        max_length=255, choices=retinopathy_choices, blank=True, null=True
    )
    # eye_laser = models.CharField(
    #     max_length=255, choices=eye_laser_choices, blank=True, null=True
    # )
    right_amputation = models.CharField(
        max_length=255, choices=amputation_choices, blank=True, null=True
    )
    left_amputation = models.CharField(
        max_length=255, choices=amputation_choices, blank=True, null=True
    )
    gdm = models.BooleanField(blank=True, null=True)
    radiation = models.BooleanField(blank=True, null=True)
    thyroid_surgery = models.BooleanField(blank=True, null=True)
    parathyroid_surgery = models.BooleanField(blank=True, null=True)
    osteoprosis = models.BooleanField(blank=True, null=True)
    fracture = models.CharField(
        max_length=255, choices=fracture_choices, blank=True, null=True
    )
    esrd = models.BooleanField(blank=True, null=True)
    pituitary_radiation = models.CharField(
        max_length=255, choices=pituitary_radiation, blank=True, null=True
    )
    alcohol = models.CharField(
        choices=alcohol_choices, max_length=255, blank=True, null=True
    )
    htn = models.BooleanField(blank=True, null=True)
    hlp = models.BooleanField(blank=True, null=True)
    smoking = models.CharField(
        max_length=255, choices=smoking_choices, blank=True, null=True
    )
    smoking_packes_per_year = models.IntegerField(blank=True, null=True)
    blood_pressure_sys = models.IntegerField(blank=True, null=True)
    blood_pressure_dias = models.IntegerField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_patient_histories",
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]


class MedicalImpression(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name


class PatientImpressionItem(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField()
    impression = models.ForeignKey(MedicalImpression, on_delete=models.CASCADE)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_impression_items",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.patient} - {self.date}"

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]


class Story(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.RESTRICT)
    date = models.DateField(auto_now_add=True)
    story = models.TextField()
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_stories",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.patient} - {self.date}"

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]


Thyroidectomy_Choices = {
    "Right": "Right",
    "Left": "Left",
    "Total": "Total",
    "Subtotal": "Subtotal",
    "Near_total": "Near Total",
}

Mng_Right_Left_Choices = {
    "Right > Left": "Right > Left",
    "Left > Right": "Left > Right",
    "Equal": "Equal",
}


class ThyroidHistory(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    is_normal = models.BooleanField(blank=True, null=True)
    thyroidectomy = models.CharField(
        max_length=255, choices=Thyroidectomy_Choices, blank=True, null=True
    )
    thyroidectomy_date = models.DateField(blank=True, null=True)
    simple_goiter_gram = models.FloatField(blank=True, null=True)
    # simple_goiter_times_normal = models.IntegerField(blank=True, null=True)
    mng_gram = models.FloatField(blank=True, null=True)
    mng_right_left = models.CharField(
        max_length=255, choices=Mng_Right_Left_Choices, blank=True, null=True
    )
    mng_largest_right_size_width = models.FloatField(blank=True, null=True)
    mng_largest_right_size_height = models.FloatField(blank=True, null=True)
    mng_largest_left_size_width = models.FloatField(blank=True, null=True)
    mng_largest_left_size_height = models.FloatField(blank=True, null=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_thyroid_histories",
        null=True,
        blank=True,
    )

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]
