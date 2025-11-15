from rest_framework import serializers

from referral_services.models import (
    Doctor,
    DoctorSpeciality,
    ReferralDoctor,
)


class SpecialitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorSpeciality
        fields = ["id", "name"]
        read_only_fields = ["id"]


class DoctorReadSerializer(serializers.ModelSerializer):
    speciality = SpecialitySerializer()

    class Meta:
        model = Doctor
        fields = ["id", "name", "address", "speciality"]
        read_only_fields = ["id"]


class DoctorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ["id", "name", "address", "speciality"]
        read_only_fields = ["id"]


class ReferralServicesReadSerializer(serializers.ModelSerializer):
    doctor = DoctorReadSerializer()

    class Meta:
        model = ReferralDoctor
        fields = [
            "id",
            "patient",
            "doctor",
            "result_date",
            "result",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReferralServicesCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralDoctor
        fields = [
            "id",
            "patient",
            "doctor",
            "result_date",
            "result",
            "comment",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
