from chat.models import Message
from rest_framework import serializers

from patient.models.patient_models import Patient


class MessageSerializer1(serializers.ModelSerializer):
    """the serializer for patient and doctor get message"""

    class Meta:
        model = Message
        fields = ["id", "user", "is_doctor_response", "content", "timestamp", "is_seen"]
        read_only_fields = ["is_doctor_response", "id", "timestamp", "user", "is_seen"]


class MessageSerializer2(serializers.ModelSerializer):
    """The serializer for doctor to create a message."""

    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(), required=True, write_only=True
    )

    class Meta:
        model = Message
        fields = ["id", "patient", "is_doctor_response", "content", "timestamp"]
        read_only_fields = ["is_doctor_response", "id", "timestamp"]

    def create(self, validated_data):
        # Map patient to user
        patient = validated_data.pop("patient")
        validated_data["user"] = patient.user  # Map Patient to User
        return super().create(validated_data)


class ChatMessageSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField(source="user__patient_id")
    first_name = serializers.CharField(source="user__patient__first_name")
    last_name = serializers.CharField(source="user__patient__last_name")
    latest_message_content = serializers.CharField()
    latest_message_time = serializers.DateTimeField()
    has_unseen = serializers.SerializerMethodField()

    def get_has_unseen(self, obj):
        """Determine if there are unseen messages."""
        return not obj["is_seen"]

    class Meta:
        fields = [
            "patient_id",
            "first_name",
            "last_name",
            "latest_message_content",
            "latest_message_time",
            "has_unseen",
        ]
