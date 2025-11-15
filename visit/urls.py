from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter
from visit import views
from visit.views.history_views import (
    BMDRecordViewset,
    MetricsWithResultsView,
    StoriesViewSet,
    ThyroidHistoryViewSet,
)
from visit.views.insulin_prescription_views import (
    InsulinPrescriptionGroupViewSet,
    InsulinViewSet,
)
from visit.views.insurance_login import (
    CheckTaminTokenApiView,
    Phase1APIView,
    Phase2APIView,
)
from visit.views.medical_imaging_views import MedicalImagingFavoritesViewSets
from visit.views.medicine_prescription_views import (
    MedicineFavoritesViewSets,
    MedicineRepeatViewSet,
)
from visit.views.other_paraclinic_services_views import (
    OtherParaclinicFavoritesViewSets,
    OtherParaclinicServicesPrescriptionViewSet,
)
from visit.views.test_prescription_views import (
    MedicalTestFavoritesViewSets,
)
from visit.views.visit_view import (
    ClinicDataView,
    GetDoctorBaseView,
    VisitPriceView,
    VisitViewSet,
)

router = DefaultRouter()
router.register("bmd-records", BMDRecordViewset)
router.register("medicine-prescription", views.MedicinePrescriptionViewSet)
router.register(
    "other-paraclinic-prescription", OtherParaclinicServicesPrescriptionViewSet
)
router.register("test-prescription", views.MedicalTestPrescriptionViewSet)
router.register("medical-imaging-prescription", views.MedicalImagingPrescriptionViewSet)
router.register("visit-insurance", views.VisitInsuranceViewSet)
router.register("finish-visit", VisitViewSet)
router.register("medicine-amounts", views.MedicineAmountsViewSet)
router.register("medicine-instructions", views.MedicineInstructionsViewSet)
router.register("medicine-repeats", MedicineRepeatViewSet)
router.register("patient-history-basic", views.PatientHistoryBasicViewSet)
router.register("medical-impressions", views.MedicalImpressionsViewSet)
router.register("patient-impressions", views.PatientImpressionItemViewSet)
router.register("patient-stories", StoriesViewSet)
router.register("medicine-favorites", MedicineFavoritesViewSets)
router.register("medical-test-favorites", MedicalTestFavoritesViewSets)
router.register("medical-imaging-favorites", MedicalImagingFavoritesViewSets)
router.register("patient-thyroid-history", ThyroidHistoryViewSet)
router.register("insulins", InsulinViewSet)
router.register("insulin-prescription-groups", InsulinPrescriptionGroupViewSet)
router.register("other-paraclinic-favorites", OtherParaclinicFavoritesViewSets)


app_name = "visit"

urlpatterns = [
    path("", include(router.urls)),
    path(
        "patient/<int:patient_id>/metrics/",
        MetricsWithResultsView.as_view(),
        name="patient-metrics",
    ),
    path("login/phase-1/", Phase1APIView.as_view(), name="phase-1"),
    path("login/phase-2/", Phase2APIView.as_view(), name="phase-2"),
    path("login/check-token/", CheckTaminTokenApiView.as_view(), name="check-token"),
    path("visit-price/", VisitPriceView.as_view(), name="visit-price"),
    path("clinic-data/", ClinicDataView.as_view(), name="clinic-data"),
    path("get-doctor-base/", GetDoctorBaseView.as_view(), name="GetDoctorBaseView"),
]
