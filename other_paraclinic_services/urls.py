from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("services", views.OtherMedicalServicesViewSet)
router.register("categories", views.CategoryViewSet)

app_name = "other_paraclinic_services"

urlpatterns = [
    path("", include(router.urls)),
]
