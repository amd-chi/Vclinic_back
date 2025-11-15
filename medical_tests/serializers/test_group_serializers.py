from rest_framework import serializers

from medical_tests.models import TestResultGroup, TestResultItem
from medical_tests.serializers.laboratory_serializers import LaboratoryReducedSerializer
from medical_tests.serializers.result_item_serializers import (
    TestItemCreateSerializer,
    TestItemReadSerializer,
)


class TestResultGroupListSerializer(serializers.ModelSerializer):
    laboratory = LaboratoryReducedSerializer()

    class Meta:
        model = TestResultGroup
        fields = ["id", "patient", "laboratory", "date"]


class TestResultGroupCreateUpdateSerializer(serializers.ModelSerializer):
    results = TestItemCreateSerializer(many=True)

    class Meta:
        model = TestResultGroup
        fields = ["id", "patient", "laboratory", "date", "results"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        results = validated_data.pop("results")
        user = self.context["request"].user
        print(user)
        testResultGroup = TestResultGroup.objects.create(
            **validated_data,
            created_by=user,
        )
        for result in results:
            TestResultItem.objects.create(group=testResultGroup, **result)
        return testResultGroup

    def update(self, instance, validated_data):
        results = validated_data.pop("results")
        instance.patient = validated_data.get("patient", instance.patient)
        instance.laboratory = validated_data.get("laboratory", instance.laboratory)
        instance.date = validated_data.get("date", instance.date)
        instance.save()
        # delete all previous results
        instance.results.all().delete()
        for result in results:
            TestResultItem.objects.create(group=instance, **result)

        return instance


class TestResultGroupReadSerializer(serializers.ModelSerializer):
    results = TestItemReadSerializer(many=True)

    class Meta:
        model = TestResultGroup
        fields = ["id", "patient", "laboratory", "date", "results"]
        read_only_fields = ["id"]
