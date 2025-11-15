from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
# router.register("primary-stat",  , basename="primary-stat")
app_name = "stat_clinic"

urlpatterns = [
    path(
        "primary-statistics/", views.VisitCounterView.as_view(), name="basic-statistics"
    ),
]
