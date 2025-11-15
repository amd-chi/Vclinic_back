from rest_framework import serializers

from medical_imaging.models import (
    MedicalImagingCenter,
    MedicalImagingInsurance,
    MedicalImagingResult,
)


class MedicalImagingInsuranceSerializer(serializers.ModelSerializer):
    is_insurance_supported = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = MedicalImagingInsurance
        fields = ["id", "name", "is_insured", "is_insurance_supported"]
        read_only_fields = ["id"]

    def get_is_insurance_supported(self, obj):
        return obj.tamin_json is not None


class MedicalImagingCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalImagingCenter
        fields = ["id", "name", "address", "phone_number"]
        read_only_fields = ["id"]


class MedicalImagingResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalImagingResult
        fields = [
            "id",
            "date",
            "comment",
            "imaging_center",
            "url",
            "patient",
            "imaging",
            "created_at",
        ]
        read_only_fields = ["id"]


class MedicalImagingResultDetailSerializer(serializers.ModelSerializer):
    imaging_center = MedicalImagingCenterSerializer()
    imaging = MedicalImagingInsuranceSerializer()

    class Meta:
        model = MedicalImagingResult
        fields = [
            "id",
            "date",
            "imaging",
            "comment",
            "imaging_center",
            "url",
            "patient",
            "created_at",
        ]
        read_only_fields = ["id"]
