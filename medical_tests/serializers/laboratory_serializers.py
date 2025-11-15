from rest_framework import serializers

from medical_tests.models import Laboratory


class LaboratoryReducedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratory
        fields = ["id", "name"]
        read_only_fields = ["id"]


class LaboratorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Laboratory
        fields = ["id", "name", "address", "phone_number"]
        read_only_fields = ["id"]
