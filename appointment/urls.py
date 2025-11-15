from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("slots", views.AppointmentSlotViewSet)

app_name = "appointment"

urlpatterns = [
    path("", include(router.urls)),
    path(
        "reserve-slot/<int:slot_id>/",
        views.ReserveAppointmentSlotView.as_view(),
        name="reserve-slot",
    ),
    # path(
    #     "reserve-slot-by-anyone/<int:slot_id>/",
    #     views.ReserveAppointmentByAnySlotView.as_view(),
    #     name="reserve-slot-by-anyone",
    # ),
    path("start/", views.StartPaymentView.as_view(), name="payment-start"),
    path(
        "verify/", views.VerifyPaymentView.as_view(), name="payment-verify"
    ),  # callback_url
    path("<int:id>/", views.PaymentDetailView.as_view(), name="payment-detail"),
    path(
        "first-available/",
        views.FirstAvailableSlotView.as_view(),
        name="first-available-slot",
    ),
]
