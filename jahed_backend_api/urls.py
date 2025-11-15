from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path("api/user/", include("user.urls")),
    path("api/patient/", include("patient.urls")),
    path("api/medical-test/", include("medical_tests.urls")),
    path("api/medicine/", include("medicines.urls")),
    path("api/medical-imaging/", include("medical_imaging.urls")),
    path("api/visit/", include("visit.urls")),
    path("api/other-paraclinic-services/", include("other_paraclinic_services.urls")),
    path("api/referral-services/", include("referral_services.urls")),
    path("api/chat/", include("chat.urls")),
    path("api/appointment/", include("appointment.urls")),
    path("api/paraclinic/", include("paraclinic.urls")),
    path("api/statistics/", include("stat_clinic.urls")),
]
