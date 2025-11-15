from rest_framework import serializers

from patient.models import Appointment
from patient.serializers.patient_serializers import PatientReducedSerializer


class AppointmentListRetrieveSerializer(serializers.ModelSerializer):
    """Serializer for Appointment"""

    patient = PatientReducedSerializer()

    class Meta:
        model = Appointment
        fields = ["id", "patient", "datetime", "description", "status"]

        read_only_fields = ["id"]


class AppointmentCreateUpdateDestroySerializer(serializers.ModelSerializer):
    """Serializer for Appointment"""

    class Meta:
        model = Appointment
        fields = ["id", "patient", "datetime", "description", "status"]

        read_only_fields = ["id"]
