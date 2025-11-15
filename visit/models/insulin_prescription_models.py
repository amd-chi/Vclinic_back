from django.db import models
from patient.models.patient_models import Patient
from utils.base_models import BaseModel

meal_choices = {
    "5AM": "5am",
    "Morning": "m",
    "Lunch": "l",
    "Dinner": "d",
}

categories_choices = {
    "short_acting": "Short Acting",
    "long_acting": "Long Acting",
    "None": "None",
}


class Insulin(models.Model):
    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=255, null=True, blank=True, choices=categories_choices
    )

    def __str__(self):
        return self.name


class InsulinPrescriptionItem(BaseModel):
    insulin = models.ForeignKey(Insulin, on_delete=models.CASCADE)
    meal = models.CharField(max_length=255, choices=meal_choices)
    dose = models.IntegerField()
    group = models.ForeignKey(
        "InsulinPrescriptionGroup",
        on_delete=models.CASCADE,
        related_name="presc_items",
    )

    def __str__(self):
        return f"{self.insulin} - {self.group}"


class InsulinPrescriptionGroup(BaseModel):
    date = models.DateField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_insulin_prescription_groups",
        null=True,
        blank=True,
    )
