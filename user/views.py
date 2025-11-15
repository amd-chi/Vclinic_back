from rest_framework import generics, permissions, viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

# from rest_framework.settings import api_settings
from app_messages.models import AppMessage
from user.models import User
from user.permissions import IsDoctor
from user.serializers import (
    # CustomTokenObtainPairSerializer,
    CaptchaTokenObtainPairSerializer,
    UserSerializer,
    UserSerializer2,
)
from drf_spectacular.utils import extend_schema

from rest_framework.response import Response
from utils.captcha.captcha import generate_captcha
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)


@api_view(["GET"])
@permission_classes([AllowAny])
@authentication_classes([])
def get_captcha(request):
    key, image = generate_captcha()
    return Response(
        {
            "captcha_key": key,
            "captcha_image": f"data:image/png;base64,{image}",
        }
    )


class CaptchaTokenObtainPairView(TokenObtainPairView):
    serializer_class = CaptchaTokenObtainPairSerializer


@extend_schema(tags=["Users"])
class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""

    # permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = []
    permission_classes = [AllowAny]
    serializer_class = UserSerializer


# @extend_schema(tags=["Users"])
# class CreateTokenView(ObtainAuthToken):
#     """Create a new auth token for user."""

#     serializer_class = AuthTokenSerializer
#     renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


@extend_schema(tags=["Users"])
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""

    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        user = request.user

        # پیام‌های نخوانده قبل از هر تغییری:
        unread_qs = AppMessage.objects.exclude(users_read=user)
        # سریالایز با پاس دادن unread_qs تا دوباره کوئری نزند
        serializer = self.get_serializer(user, context={"unread_qs": unread_qs})
        data = serializer.data

        return Response(data)


class ReadAllMessagesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        unread_qs = AppMessage.objects.exclude(users_read=user)
        count = unread_qs.count()
        if count:
            user.app_messages_read.add(*unread_qs)
        return Response({"status": "ok", "marked_as_read": count})


class ManageSecretariesByDoctorViewset(viewsets.ModelViewSet):
    serializer_class = UserSerializer2
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsDoctor]
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(role="secretary")
