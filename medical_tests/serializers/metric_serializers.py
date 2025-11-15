from rest_framework import serializers

from medical_tests.models import TestMetric, TestResultItem

from medical_tests.serializers.unit_serializers import UnitSerializer


class MetricCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestMetric
        fields = ["id", "name", "unit", "normalizer_coefficient", "group_name"]
        read_only_fields = ["id"]


class MetricReadSerializer(serializers.ModelSerializer):
    unit = UnitSerializer(read_only=True)

    class Meta:
        model = TestMetric
        fields = ["id", "name", "unit", "normalizer_coefficient", "group_name"]
        read_only_fields = ["id"]


class TestMetricSerializer(serializers.ModelSerializer):
    result_items = serializers.SerializerMethodField()
    unit = serializers.CharField(source="unit.name")

    class Meta:
        model = TestMetric
        fields = ["id", "name", "unit", "result_items", "group_name"]

    def get_result_items(self, obj):
        patient_id = self.context.get("patient_id")
        result_items = TestResultItem.objects.filter(
            group__patient_id=patient_id, metric=obj
        )
        from medical_tests.serializers.result_item_serializers import (
            TestResultItemSerializerType2,
        )

        return TestResultItemSerializerType2(result_items, many=True).data
