from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("medical-imaging-insurance", views.MedicalImagingInsuranceView)
router.register("medical-imaging-results", views.MedicalImagingResultViewSet)
router.register("medical-imaging-centers", views.MedicalImagingCentersViewSet)

app_name = "medical_imaging"

urlpatterns = [
    path("", include(router.urls)),
]
