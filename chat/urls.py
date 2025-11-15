from django.urls import (
    path,
)

# from rest_framework.routers import DefaultRouter
from . import views

# router = DefaultRouter()
# router.register("messages", views.MessageListCreateView, basename="messages")

app_name = "chat"

urlpatterns = [
    # path("", include(router.urls), name="messages"),
    path(
        "messages/patient/",
        views.MessageListCreateView.as_view(),
        name="messages-patient",
    ),
    path(
        "messages/doctor/",
        views.MessagesListCreateView2.as_view(),
        name="messages-doctor",
    ),
    path("chats/", views.GetChatsView.as_view(), name="chats"),
]
