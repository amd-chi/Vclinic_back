"""
URL mappings for the user API.
"""

from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.routers import DefaultRouter

from user import views


app_name = "user"
router = DefaultRouter()
router.register("", views.ManageSecretariesByDoctorViewset)
urlpatterns = [
    path("secretary/", include(router.urls)),
    path("create/", views.CreateUserView.as_view(), name="create"),
    path("me/", views.ManageUserView.as_view(), name="me"),
    path("me/read-all/", views.ReadAllMessagesView.as_view(), name="me-read-all"),
    path(
        "token/",
        extend_schema_view(
            post=extend_schema(
                tags=["Users"],
                summary="Obtain JWT Token",
                description="Get access and refresh tokens by providing valid credentials.",
            )
        )(TokenObtainPairView.as_view()),
        name="token_obtain_pair",
    ),
    path(
        "token/refresh/",
        extend_schema_view(
            post=extend_schema(
                tags=["Users"],
                summary="Refresh JWT Token",
                description="Refresh access token using a valid refresh token.",
            )
        )(TokenRefreshView.as_view()),
        name="token_refresh",
    ),
    path(
        "token2/", views.CaptchaTokenObtainPairView.as_view(), name="token_obtain_pair"
    ),
    path("captcha/", views.get_captcha, name="get_captcha"),
]
