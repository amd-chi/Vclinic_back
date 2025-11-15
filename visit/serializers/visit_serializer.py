from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from patient.models.appointment_models import Appointment
from patient.serializers.patient_serializers import PatientSearchSerializer
from visit.models import VisitInsurance
from visit.models.visit_models import ClinicData, Visit, VisitPrice

# import datetime
from datetime import time, datetime


class VisitInsuranceSerializer(ModelSerializer):
    class Meta:
        model = VisitInsurance
        fields = "__all__"
        read_only_fields = ["id", "tamin_tracking_code"]


class VisitPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitPrice
        fields = ["price"]


class VisitSerializerCreate(serializers.ModelSerializer):
    next_visit_date = serializers.DateField(write_only=True)
    appointment_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = Visit
        fields = ["patient", "fee", "id", "appointment_id", "next_visit_date"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        patient = validated_data.get("patient")
        if Visit.objects.filter(patient=patient, date=datetime.today()).exists():
            raise serializers.ValidationError("Patient already has a visit today.")
        fee = validated_data.get("fee")
        next_visit = validated_data.get("next_visit_date")
        visit = Visit.objects.create(
            patient=patient, fee=fee, created_by=self.context["request"].user
        )
        patient.next_visit_date = next_visit

        today_min = datetime.combine(datetime.today(), time.min)
        today_max = datetime.combine(datetime.today(), time.max)

        filter = Appointment.objects.filter(
            patient=patient, datetime__range=(today_min, today_max)
        )
        if filter.exists():
            appointment_instance = filter.first()
            appointment_instance.status = "Visited"
            appointment_instance.save()
        patient.save()

        return visit


class VisitSerializerUpdate(serializers.ModelSerializer):
    next_visit_date = serializers.DateField()

    class Meta:
        model = Visit
        fields = ["patient", "fee", "next_visit_date", "id"]
        read_only_fields = ["id"]

    def update(self, instance, validated_data):
        next_visit = validated_data.get("next_visit_date")
        fee = validated_data.get("fee")
        if fee:
            instance.fee = fee
        instance.patient.next_visit_date = next_visit
        instance.patient.save()

        return super().update(instance, validated_data)


class VisitSerializerRead(serializers.ModelSerializer):
    patient = PatientSearchSerializer()
    next_visit_date = serializers.DateField(
        source="patient.next_visit_date", read_only=True
    )

    class Meta:
        model = Visit
        fields = ["id", "date", "patient", "fee", "next_visit_date"]
        read_only_fields = ["id", "patient", "fee", "next_visit_date"]


class ClinicDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicData
        fields = [
            "doctor_name",
            "clinic_address",
            "clinic_phone",
            "medical_education_number",
            "speciality",
        ]
