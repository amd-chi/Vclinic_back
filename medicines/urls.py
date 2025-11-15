from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("medicines", views.MedicineViewSet)

app_name = "medicines"

urlpatterns = [
    path("", include(router.urls)),
]
