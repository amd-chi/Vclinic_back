from django.db import models


class Medicine(models.Model):
    name = models.CharField(max_length=511)
    category = models.CharField(max_length=255, default="None")
    is_insured = models.BooleanField(default=False)
    tamin_json = models.JSONField(blank=True, null=True)
    tamin_id = models.IntegerField(blank=True, null=True, unique=True)
    code = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.id} - {self.name}"

    class Meta:
        indexes = [
            models.Index(fields=["name", "tamin_id"]),
        ]
