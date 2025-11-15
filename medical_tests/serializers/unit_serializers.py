from rest_framework import serializers

from medical_tests.models import MetricUnit


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetricUnit
        fields = ["id", "name"]
        read_only_fields = ["id"]
