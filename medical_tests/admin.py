from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Laboratory)
admin.site.register(models.MetricUnit)
admin.site.register(models.TestMetric)
admin.site.register(models.TestResultItem)
admin.site.register(models.TestResultGroup)
admin.site.register(models.MedicalTestInsurance)
