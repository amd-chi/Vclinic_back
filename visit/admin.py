from django.contrib import admin

from visit.models.history_models import (
    MedicalImpression,
)
from visit.models.medical_imaging_models import (
    MedicalImagingPrescriptionGroup,
    MedicalImagingPrescriptionItem,
)
from .models import (
    MedicalTestPrescriptionGroup,
    MedicalTestPrescriptionItem,
    MedicinePrescriptionGroup,
    MedicinePrescriptionItem,
)
from . import models


class MedicinePrescriptionItemInline(admin.StackedInline):
    model = MedicinePrescriptionItem
    extra = 1
    # تنظیمات CSS سفارشی
    # classes = ["collapse"]
    # محدود کردن تعداد ستون‌ها یا تنظیم عرض ستون‌ها
    fields = ["medicine", "amount", "instruction", "usage", "quantity"]
    verbose_name = "Medicine Prescription Item"
    verbose_name_plural = "Medicine Prescription Items"


@admin.register(MedicinePrescriptionGroup)
class MedicinePrescriptionGroupAdmin(admin.ModelAdmin):
    inlines = [MedicinePrescriptionItemInline]
    list_display = ["patient", "date", "comment", "tamin_tracking_code", "date"]
    search_fields = ["patient__last_name", "comment", "tamin_tracking_code"]
    list_filter = ["patient__first_name"]


class MedicalTestPrescriptionItemInline(admin.StackedInline):
    model = MedicalTestPrescriptionItem
    extra = 1
    # تنظیمات CSS سفارشی
    # classes = ["collapse"]
    # محدود کردن تعداد ستون‌ها یا تنظیم عرض ستون‌ها
    fields = ["test", "date"]
    verbose_name = "Test Prescription Item"
    verbose_name_plural = "Test Prescription Items"


@admin.register(MedicalTestPrescriptionGroup)
class MedicalTestPrescriptionGroupAdmin(admin.ModelAdmin):
    inlines = [MedicalTestPrescriptionItemInline]
    list_display = ["patient", "comment", "tamin_tracking_code", "date"]
    search_fields = ["patient__last_name", "comment", "tamin_tracking_code"]
    list_filter = ["patient__first_name"]


class MedicalImagingItemInline(admin.StackedInline):
    model = MedicalImagingPrescriptionItem
    extra = 1
    # تنظیمات CSS سفارشی
    # classes = ["collapse"]
    # محدود کردن تعداد ستون‌ها یا تنظیم عرض ستون‌ها
    fields = ["imaging", "date"]
    verbose_name = "Imaging Prescription Item"
    verbose_name_plural = "Imaging Prescription Items"


@admin.register(MedicalImagingPrescriptionGroup)
class MedicalImagingGroupAdmin(admin.ModelAdmin):
    inlines = [MedicalImagingItemInline]
    list_display = ["patient", "comment", "tamin_tracking_code", "date"]
    search_fields = ["patient__last_name", "comment", "tamin_tracking_code"]
    list_filter = ["patient__first_name"]


# Register your models here.
admin.site.register(models.MedicineAmount)
admin.site.register(models.MedicineInstruction)
admin.site.register(models.MedicineUsage)


class MedicalImpressionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


admin.site.register(MedicalImpression, MedicalImpressionAdmin)
admin.site.register(models.PatientHistoryBasic)


class PatientImpressionGroupAdmin(admin.ModelAdmin):
    list_display = ("patient", "date")
    search_fields = ("patient__name",)
    list_filter = ("date",)
    filter_horizontal = ("impressions",)


# admin.site.register(PatientImpressionGroup, PatientImpressionGroupAdmin)
