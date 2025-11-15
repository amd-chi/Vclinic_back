"""
Serializers for the user API View.
"""

from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.cache import cache

from app_messages.models import AppMessage


class CaptchaTokenObtainPairSerializer(TokenObtainPairSerializer):
    captcha_key = serializers.CharField(write_only=True)
    captcha_value = serializers.CharField(write_only=True)

    def validate(self, attrs):
        captcha_key = attrs.pop("captcha_key", None)
        captcha_value = attrs.pop("captcha_value", "").lower()

        real_value = cache.get(f"captcha_{captcha_key}")
        if not real_value or real_value != captcha_value:
            raise serializers.ValidationError("Invalid or expired CAPTCHA.")

        # If CAPTCHA is valid, proceed
        return super().validate(attrs)


class UserSerializer2(serializers.ModelSerializer):
    """Serializer for the secretaries"""

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "first_name",
            "last_name",
            "password",
            "phone_number",
            "national_id",
            "role",
            "is_active",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
            "id": {"read_only": True},
            "role": {"read_only": True},
            "is_active": {"required": False},
        }

    def create(self, validated_data):
        """Create and return a Secretary with encrypted password."""
        password = validated_data.pop("password", None)

        if password is None:
            raise serializers.ValidationError({"password": "This field is required."})

        user = get_user_model()(**validated_data, role="secretary")
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update and return Secretary."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    unread_messages = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "first_name",
            "last_name",
            "password",
            "phone_number",
            "national_id",
            "role",
            "patient",
            "unread_messages",
        ]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 5},
            "role": {"read_only": True},
            "unread_messages": {"read_only": True},
        }

    def get_unread_messages(self, obj):
        unread_qs = AppMessage.objects.exclude(users_read=obj)

        # خروجی سبک: هم count هم چند فیلد لازم از آیتم‌ها
        return {
            "count": unread_qs.count(),
            "items": list(
                unread_qs.order_by("-created_at").values("id", "content", "created_at")[
                    :20
                ]  # مثلاً فقط ۲۰ تای آخر
            ),
        }

    def create(self, validated_data):
        """Create and return a Manager with encrypted password."""
        # take patient object and check if correct and not taken by other user
        patient = validated_data.get("patient", None)
        if patient is None:
            raise serializers.ValidationError({"patient": "This field is required."})
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return Manager."""
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the manager auth token."""

    email = serializers.EmailField()
    password = serializers.CharField(
        style={"input_type": "password"},
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get("email")
        password = attrs.get("password")
        manager = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not manager:
            msg = _("Unable to authenticate with provided credentials.")
            raise serializers.ValidationError(msg, code="authorization")

        attrs["user"] = manager
        return attrs
