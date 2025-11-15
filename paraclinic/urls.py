from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter
from . import views

app_name = "paraclinic"

router = DefaultRouter()
router.register("results", views.ParaclinicResultViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
