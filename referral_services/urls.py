from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter

from referral_services.views import (
    DoctorViewSet,
    ReferralDoctorViewSet,
    SpecialityViewSet,
)

router = DefaultRouter()
router.register("doctors", DoctorViewSet)
router.register("refer-doctor", ReferralDoctorViewSet)
router.register("specialities", SpecialityViewSet)

app_name = "referral_services"

urlpatterns = [
    path("", include(router.urls)),
]
