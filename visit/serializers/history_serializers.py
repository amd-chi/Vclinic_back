from rest_framework import serializers

from medical_imaging.serializers import MedicalImagingCenterSerializer
from patient.models.patient_models import Patient
from utils.base_models import DEFAULT_EXCLUDE_FIELDS
from visit.models.history_models import (
    MedicalImpression,
    PatientHistoryBasic,
    PatientImpressionItem,
    Story,
    ThyroidHistory,
)
from visit.models.medical_imaging_models import BMDRecordGroup, BMDRecordItem


class PatientHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientHistoryBasic
        fields = [
            "id",
            "patient",
            "ihd",
            "statin",
            "aspirin",
            "retinopathy",
            "right_amputation",
            "left_amputation",
            "gdm",
            "radiation",
            "thyroid_surgery",
            "parathyroid_surgery",
            "osteoprosis",
            "fracture",
            "esrd",
            "pituitary_radiation",
            "alcohol",
            "htn",
            "hlp",
            "smoking",
            "smoking_packes_per_year",
            "blood_pressure_sys",
            "blood_pressure_dias",
            "comment",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        patient_id = validated_data.pop("patient").id
        # check if such history already exists
        patient = Patient.objects.get(id=patient_id)
        profile = PatientHistoryBasic.objects.create(
            created_by=self.context["request"].user, patient=patient, **validated_data
        )
        return profile

    def update(self, instance, validated_data):
        patient_id = validated_data.pop("patient").id
        patient = Patient.objects.get(id=patient_id)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.patient = patient
        instance.save()

        return instance


class MedicalImpressionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalImpression
        fields = ["id", "name"]
        read_only_fields = ["id"]


class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        exclude = DEFAULT_EXCLUDE_FIELDS
        read_only_fields = ["id"]


class PatientImpressionSerializerGet(serializers.ModelSerializer):
    impression = MedicalImpressionSerializer()

    class Meta:
        model = PatientImpressionItem
        fields = ["patient", "impression", "id", "date", "created_at"]
        read_only_fields = ["id"]


class PatientImpressionSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = PatientImpressionItem
        fields = ["patient", "impression", "id", "date", "created_at"]
        read_only_fields = ["id"]


# class PatientImpressionListRetrieveGroupSerializer(serializers.ModelSerializer):
#     impressions = MedicalImpressionSerializer(many=True, read_only=True)

#     class Meta:
#         model = PatientImpressionItem
#         read_only_fields = ["id"]
#         exclude = DEFAULT_EXCLUDE_FIELDS


class PatientThyroidHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ThyroidHistory
        read_only_fields = ["id"]
        exclude = DEFAULT_EXCLUDE_FIELDS


class BMDRecordItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BMDRecordItem
        read_only_fields = ["id"]
        fields = ["parameter", "site", "value", "bmd", "comment", "delta_value"]


# class BMDRecordItemGetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BMDRecordItem
#         read_only_fields = ["id"]
#         fields = ["parameter", "site", "value", "bmd", "comment"]


class BMDRecordGroupReadSerializer(serializers.ModelSerializer):
    items = BMDRecordItemSerializer(many=True)
    center = MedicalImagingCenterSerializer()

    class Meta:
        model = BMDRecordGroup
        read_only_fields = ["id"]
        exclude = DEFAULT_EXCLUDE_FIELDS


class BMDRecordGroupCreateSerializer(serializers.ModelSerializer):
    items = BMDRecordItemSerializer(many=True)

    class Meta:
        model = BMDRecordGroup
        fields = [
            "id",
            "patient",
            "date",
            "center",
            "comment",
            "major_osteoporotic_fracture_risk",
            "hip_fracture_risk",
            "items",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        bmd_group = BMDRecordGroup.objects.create(
            **validated_data, created_by=self.context["request"].user
        )
        for item_data in items_data:
            BMDRecordItem.objects.create(group=bmd_group, **item_data)
        return bmd_group

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items")
        instance.name = validated_data.get("name", instance.name)
        instance.center = validated_data.get("center", instance.center)
        instance.comment = validated_data.get("comment", instance.comment)
        instance.major_osteoporotic_fracture_risk = validated_data.get(
            "major_osteoporotic_fracture_risk",
            instance.major_osteoporotic_fracture_risk,
        )
        instance.hip_fracture_risk = validated_data.get(
            "hip_fracture_risk", instance.hip_fracture_risk
        )
        instance.save()

        # Delete existing items
        instance.items.all().delete()

        # Create new items
        for item_data in items_data:
            BMDRecordItem.objects.create(group=instance, **item_data)

        return instance
