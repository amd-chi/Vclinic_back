from rest_framework import generics
from chat.models import Message
from chat.serializers import (
    ChatMessageSerializer,
    MessageSerializer1,
    MessageSerializer2,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.models import Min, Max
from patient.models.patient_models import Patient
from user.permissions import IsSecretary
from django.db.models import Q
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiParameter, extend_schema
from drf_spectacular.types import OpenApiTypes


@extend_schema(tags=["Chats"])
class MessageListCreateView(generics.ListCreateAPIView):
    """
    This View is for patients to list all messages related them and creating a new message.
    """

    queryset = Message.objects.all()
    authentication_classes = [JWTAuthentication]
    serializer_class = MessageSerializer1
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Marking all unseen messages from doctor as seen when listing
        queryset = Message.objects.filter(user=self.request.user).order_by("-timestamp")
        queryset.filter(is_doctor_response=True, is_seen=False).update(is_seen=True)
        return queryset

    def perform_create(self, serializer):
        # Creating a new message from the patient
        serializer.save(user=self.request.user, is_doctor_response=False)


# add a patient query string to the schema


@extend_schema(
    tags=["Chats"],
    parameters=[
        OpenApiParameter(
            name="patient",
            description="Patient ID (required)",
            required=True,
            type=OpenApiTypes.INT,  # Use OpenApiTypes for better type compatibility
            location=OpenApiParameter.QUERY,  # Indicate it's a query parameter
        )
    ],
)
class MessagesListCreateView2(generics.ListCreateAPIView):
    """
    This ViewSet is for listing all messages for the doctor and create messages
    """

    authentication_classes = [JWTAuthentication]
    serializer_class = MessageSerializer1
    permission_classes = [IsSecretary]

    def get_serializer_class(self):
        # Use different serializer for creating a message
        if self.request.method == "POST":
            return MessageSerializer2
        return self.serializer_class

    def get_queryset(self):
        # Get patient query param
        patient_id = self.request.query_params.get("patient")
        if not patient_id:
            raise ValidationError({"detail": "Patient ID is required."})

        # Ensure the patient exists
        patient = get_object_or_404(Patient, id=patient_id)

        # Filter messages for the given patient
        queryset = Message.objects.filter(user__patient=patient).order_by("-timestamp")

        # Update unseen messages as seen
        queryset.filter(is_doctor_response=False, is_seen=False).update(is_seen=True)

        return queryset

    def perform_create(self, serializer):
        # Creating a new message from the doctor
        serializer.save(is_doctor_response=True, created_by=self.request.user)


@extend_schema(tags=["Chats"])
class GetChatsView(generics.ListAPIView):
    """
    This View returns a list of users who have sent at least one message,
    along with their latest message information.
    """

    permission_classes = [IsSecretary]
    authentication_classes = [JWTAuthentication]
    serializer_class = ChatMessageSerializer

    def get_queryset(self):
        # Querying the latest messages for each user
        return (
            Message.objects.filter(is_doctor_response=False)
            .values(
                "user",
                "user__patient_id",
                "user__patient__first_name",
                "user__patient__last_name",
            )
            .annotate(
                latest_message_content=Max(
                    "content", filter=Q(is_doctor_response=False)
                ),
                latest_message_time=Max("timestamp"),
                is_seen=Min("is_seen"),
            )
            .order_by("-latest_message_time")
        )[0:50]
