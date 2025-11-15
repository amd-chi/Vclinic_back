from django.db import models

from utils.base_models import BaseModel

from .patient_models import Patient

states_choices = [
    ("Pending", "Pending"),
    ("Visiting", "Visiting"),
    ("Canceled_by_patient", "Canceled_by_patient"),
    ("Canceled_by_secretary", "Canceled_by_secretary"),
    ("Visited", "Visited"),
]


class Appointment(BaseModel):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    datetime = models.DateTimeField()
    description = models.TextField(max_length=511, null=True, blank=True)
    status = models.CharField(max_length=255, default="Pending", choices=states_choices)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_appointments",
        null=True,
        blank=True,
    )
    # canceled_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return (
            self.patient.first_name
            + " "
            + self.patient.last_name
            + " - "
            + self.datetime.strftime("%Y-%m-%d %H:%M")
        )

    class Meta:
        indexes = [
            models.Index(fields=["datetime"]),
        ]
