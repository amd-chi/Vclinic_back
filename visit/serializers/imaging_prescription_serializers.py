from rest_framework import serializers
from datetime import datetime, timedelta
from medical_imaging.serializers import MedicalImagingInsuranceSerializer
from patient.models import Patient
from visit.models import MedicalImagingPrescriptionItem
from visit.models.medical_imaging_models import (
    MedicalImagingFavoriteGroup,
    MedicalImagingFavoriteItem,
    MedicalImagingPrescriptionGroup,
)


class MedicalImagingPrescriptionItemForReadSerializer(serializers.ModelSerializer):
    imaging = MedicalImagingInsuranceSerializer()

    class Meta:
        model = MedicalImagingPrescriptionItem
        fields = ["id", "imaging", "date"]
        read_only_fields = ["id"]


class MedicalImagingPrescriptionItemForCreateUpdateSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = MedicalImagingPrescriptionItem
        fields = ["imaging", "date"]
        read_only_fields = ["id"]

    def validate_date(self, value):
        max_date = datetime.now() + timedelta(days=180)  # 6 ماه آینده
        if value > max_date.date():
            raise serializers.ValidationError(
                "The date cannot be more than 6 months in the future."
            )
        return value


class MedicalImagingCreateUpdateSerializer(serializers.Serializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    comment = serializers.CharField(required=False, allow_null=True)
    use_insurance = serializers.BooleanField(required=False)
    presc_items = MedicalImagingPrescriptionItemForCreateUpdateSerializer(many=True)


class MedicalImagingGroupReadSerializer(serializers.ModelSerializer):
    presc_items = MedicalImagingPrescriptionItemForReadSerializer(many=True)

    class Meta:
        model = MedicalImagingPrescriptionGroup
        fields = ["id", "date", "comment", "tamin_tracking_code", "presc_items"]
        read_only_fields = ["id"]


class MedicalImagingFavItemRetrieveListSerializer(serializers.ModelSerializer):
    imaging = MedicalImagingInsuranceSerializer()

    class Meta:
        model = MedicalImagingFavoriteItem
        fields = ["id", "imaging"]
        read_only_fields = ["id"]


class MedicalImagingFavoriteGroupReadSerializer(serializers.ModelSerializer):
    items = MedicalImagingFavItemRetrieveListSerializer(many=True)

    class Meta:
        model = MedicalImagingFavoriteGroup
        fields = ["id", "name", "items"]
        read_only_fields = ["id"]


class MedicalImagingFavItemCreateUpdate(serializers.ModelSerializer):
    class Meta:
        model = MedicalImagingFavoriteItem
        fields = ["id", "imaging"]
        read_only_fields = ["id"]


class MedicalImagingFavoriteGroupCreateUpdateSerializer(serializers.ModelSerializer):
    items = MedicalImagingFavItemCreateUpdate(many=True)

    class Meta:
        model = MedicalImagingFavoriteGroup
        fields = ["id", "name", "items"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        medicine_favorite_group = MedicalImagingFavoriteGroup.objects.create(
            **validated_data
        )
        for item_data in items_data:
            MedicalImagingFavoriteItem.objects.create(
                group=medicine_favorite_group, **item_data
            )
        return medicine_favorite_group

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items")
        instance.name = validated_data.get("name", instance.name)
        instance.save()

        # Delete existing items
        instance.items.all().delete()

        # Create new items
        for item_data in items_data:
            MedicalImagingFavoriteItem.objects.create(group=instance, **item_data)

        return instance
