from rest_framework import serializers

from medical_tests.models import MedicalTestInsurance


class MedicalTestInsuranceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalTestInsurance
        fields = ["id", "name", "is_insured"]
        read_only_fields = ["id"]
