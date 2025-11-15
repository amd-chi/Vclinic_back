from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from patient.views.appointment_views import AppointmentViewSet
from patient.views.patient_views import (
    GetOtpView,
    PatientChangePasswordUser,
    PatientGetRegisterDataView,
    PatientRegisterView,
    PatientSearchViewSet,
    PatientViewSet,
    PatientVisitDetailRetrieveView,
)

router = DefaultRouter()
router.register("patients", PatientViewSet, "asd123")
router.register("patient-search", PatientSearchViewSet, "asd1asd")
router.register("appointments", AppointmentViewSet, "1kasd")
router.register("visit", PatientVisitDetailRetrieveView, "a12h3kjsad")

app_name = "patient"

urlpatterns = [
    path("", include(router.urls)),
    path("register-data/", PatientGetRegisterDataView.as_view(), name="register-data"),
    path("register-patient/", PatientRegisterView.as_view(), name="register-patient"),
    path("get-otp-code/", GetOtpView.as_view(), name="get-otp-code"),
    path(
        "change-password/", PatientChangePasswordUser.as_view(), name="change-password"
    ),
]
