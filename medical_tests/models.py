from utils.base_models import BaseModel, models


# Create your models here.


class MetricUnit(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class TestMetric(models.Model):
    name = models.CharField(max_length=255, unique=True)
    unit = models.ForeignKey(MetricUnit, on_delete=models.RESTRICT)
    normalizer_coefficient = models.FloatField(default=1)
    group_name = models.CharField(max_length=255, default="Other")

    def __str__(self):
        return self.name


class Laboratory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]
        verbose_name_plural = "Laboratories"

    def __str__(self):
        return self.name


class TestResultGroup(BaseModel):
    patient = models.ForeignKey("patient.Patient", on_delete=models.CASCADE)
    laboratory = models.ForeignKey(
        Laboratory, on_delete=models.CASCADE, null=True, blank=True
    )
    date = models.DateField()
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_test_result_groups",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"ID: {self.id} - {self.patient} - آزمایشگاه {self.laboratory}"

    class Meta:
        indexes = [
            models.Index(fields=["patient"]),
        ]


class TestResultItem(BaseModel):
    group = models.ForeignKey(
        "TestResultGroup",
        on_delete=models.CASCADE,
        related_name="results",
    )
    metric = models.ForeignKey(
        TestMetric, on_delete=models.RESTRICT, related_name="result_items"
    )
    raw_value = models.FloatField(null=True, blank=True)
    reference_range = models.FloatField(blank=True, null=True)
    value = models.FloatField(null=True, blank=True)
    comment = models.CharField(max_length=256, null=True, blank=True)
    visited = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.raw_value is not None and self.reference_range:
            self.value = round(
                (
                    self.raw_value
                    / self.reference_range
                    * self.metric.normalizer_coefficient
                ),
                2,
            )

        # ذخیره‌سازی شیء با مقدار جدید value
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Group: {self.group.id} - {self.metric}"


class TestResultFavoriteGroup(BaseModel):
    name = models.CharField(max_length=255)
    items = models.ManyToManyField(TestMetric, related_name="favorite_groups")


class MedicalTestInsurance(BaseModel):
    name = models.CharField(max_length=511)
    is_insured = models.BooleanField(default=False)
    tamin_json = models.JSONField(null=True, blank=True)
    tamin_id = models.IntegerField(blank=True, null=True, unique=True)
    code = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return self.name + (" (Insured)" if self.is_insured else "")

    class Meta:
        indexes = [
            models.Index(fields=["name", "tamin_id"]),
        ]
