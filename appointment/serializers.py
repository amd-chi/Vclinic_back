from rest_framework import serializers

from patient.models.patient_models import PreRegisterPatient
from patient.serializers.patient_serializers import PatientSearchSerializer
from .models import AppointmentSlot, PaymentTransaction


class PreRegisterPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreRegisterPatient
        fields = ["mobile_number", "first_name", "last_name", "national_id"]


class AppointmentSlotGetSerializer(serializers.ModelSerializer):
    patient = PatientSearchSerializer()
    pre_registered_patient = PreRegisterPatientSerializer()

    class Meta:
        model = AppointmentSlot
        fields = [
            "id",
            "date",
            "start_time",
            "end_time",
            "patient",
            "is_booked",
            "pre_registered_patient",
        ]
        read_only_fields = ["id", "is_booked"]


class AppointmentSlotPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppointmentSlot
        fields = ["id", "date", "start_time", "end_time", "is_booked", "patient"]
        extra_kwargs = {
            "patient": {"required": False, "allow_null": True},
        }
        read_only_fields = ["id", "is_booked"]


class CreatePaymentSerializer(serializers.Serializer):
    slot_id = serializers.IntegerField()
    patient_id = serializers.IntegerField()
    is_pre_registered = serializers.BooleanField(required=False, default=False)


class PaymentInitResponseSerializer(serializers.Serializer):
    start_pay_url = serializers.CharField()
    authority = serializers.CharField()


class PaymentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = [
            "id",
            "slot",
            "patient",
            "amount",
            "status",
            "authority",
            "ref_id",
            "created_at",
            "verified_at",
        ]


class BulkAppointmentSlotSerializer(serializers.Serializer):
    slots = AppointmentSlotPostSerializer(many=True)

    def create(self, validated_data):
        slots_data = validated_data["slots"]
        slots = [AppointmentSlot(**slot) for slot in slots_data]
        return AppointmentSlot.objects.bulk_create(slots)
