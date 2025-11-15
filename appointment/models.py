from django.db import models
from patient.models.patient_models import PreRegisterPatient
from utils.base_models import BaseModel


# appointments/models.py


class AppointmentSlot(BaseModel):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    patient = models.ForeignKey(
        "patient.Patient", on_delete=models.CASCADE, null=True, blank=True
    )
    pre_registered_patient = models.ForeignKey(
        PreRegisterPatient, on_delete=models.CASCADE, null=True, blank=True
    )
    is_booked = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_appointment_slots",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.date} {self.start_time}-{self.end_time}"

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
            models.Index(fields=["is_booked", "date"]),
            models.Index(fields=["date", "start_time"]),
        ]


class PaymentTransaction(BaseModel):
    class Status(models.TextChoices):
        INITIATED = "INITIATED", "Initiated"
        PENDING_VERIFY = "PENDING_VERIFY", "Pending Verify"
        PAID = "PAID", "Paid"
        FAILED = "FAILED", "Failed"
        CANCELED = "CANCELED", "Canceled"

    slot = models.ForeignKey(
        "AppointmentSlot",
        on_delete=models.PROTECT,
        related_name="payments",
    )
    patient = models.ForeignKey(
        "patient.Patient", on_delete=models.PROTECT, null=True, blank=True
    )
    pre_registered_patient = models.ForeignKey(
        PreRegisterPatient, on_delete=models.CASCADE, null=True, blank=True
    )
    amount = models.PositiveIntegerField()  # مبلغ به ریال (طبق زرین‌پال)
    description = models.CharField(max_length=255, blank=True)
    authority = models.CharField(max_length=64, blank=True, db_index=True)
    ref_id = models.BigIntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.INITIATED
    )
    is_sandbox = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [models.Index(fields=["authority"])]
        constraints = [
            # هر اسلات همزمان فقط یک پرداخت فعال (غیرنهایی) داشته باشد
            models.UniqueConstraint(
                fields=["slot"],
                condition=models.Q(status__in=["INITIATED", "PENDING_VERIFY"]),
                name="uniq_active_payment_per_slot",
            )
        ]
