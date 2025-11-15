from rest_framework import serializers

from medical_tests.models import TestResultFavoriteGroup
from medical_tests.serializers.metric_serializers import MetricReadSerializer


class MedicalTestResultFavoriteGroupReadSerializer(serializers.ModelSerializer):
    items = MetricReadSerializer(many=True)

    class Meta:
        model = TestResultFavoriteGroup
        fields = ["id", "name", "items"]
        read_only_fields = ["id"]


class MedicalTestResultFavoriteGroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResultFavoriteGroup
        fields = ["id", "name", "items"]
        read_only_fields = ["id"]
