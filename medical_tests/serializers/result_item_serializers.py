from rest_framework import serializers
from medical_tests.models import TestResultItem
from medical_tests.serializers.metric_serializers import (
    MetricReadSerializer,
)


class TestItemReadSerializer(serializers.ModelSerializer):
    metric = MetricReadSerializer()

    class Meta:
        model = TestResultItem
        fields = ["id", "group", "metric", "raw_value", "reference_range", "comment"]
        read_only_fields = ["id", "group"]


class TestItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResultItem
        fields = ["id", "metric", "reference_range", "raw_value", "comment"]
        read_only_fields = ["id"]


class TestResultItemSerializerType2(serializers.ModelSerializer):
    date = serializers.DateField(source="group.date", read_only=True)
    laboratory = serializers.CharField(source="group.laboratory.name", read_only=True)

    class Meta:
        model = TestResultItem
        fields = [
            "id",
            "value",
            "visited",
            "date",
            "comment",
            "laboratory",
        ]


class TestResultItemVisitedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResultItem
        fields = ["visited"]
