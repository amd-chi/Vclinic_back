from django.db import models


class OtherParaclinicService(models.Model):
    name = models.CharField(max_length=511)
    is_insured = models.BooleanField(default=False)
    tamin_json = models.JSONField(null=True, blank=True)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    tamin_id = models.IntegerField(null=True, blank=True, unique=True)
    code = models.CharField(null=True, blank=True, max_length=255)

    def __str__(self):
        return self.name + (" (Insured)" if self.is_insured else "")

    class Meta:
        indexes = [
            models.Index(fields=["name", "tamin_id"]),
        ]


class Category(models.Model):
    concept = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
