from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("medical-tests", views.TestResultGroupViewSet)
router.register(
    "medical-test-results-favorites", views.MedicalTestResultFavoriteGroupViewSet
)
router.register("medical-tests-insurance", views.MedicalTestInsuranceView)
router.register("test-result-visited", views.TestResultItemVisitedViewSet)
router.register("laboratories", views.LaboratoryViewSet)
router.register("test-metrics", views.TestMetricViewSet)
router.register("units", views.UnitsViewSet)

app_name = "medical_tests"

urlpatterns = [
    path("", include(router.urls)),
]
