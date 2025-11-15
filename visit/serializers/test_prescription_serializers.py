from rest_framework import serializers
from datetime import datetime, timedelta
from medical_tests.serializers.test_insurance_serializers import (
    MedicalTestInsuranceSerializer,
)
from patient.models import Patient
from visit.models import (
    MedicalTestPrescriptionItem,
)
from visit.models.medical_test_models import (
    # MedicalTestFavorite,
    MedicalTestFavoriteGroup,
    MedicalTestFavoriteItem,
    MedicalTestPrescriptionGroup,
)


class MedicalTestPrescriptionItemSerializer(serializers.ModelSerializer):
    test = MedicalTestInsuranceSerializer()

    class Meta:
        model = MedicalTestPrescriptionItem
        fields = ["id", "test", "date"]
        read_only_fields = ["id"]

    def validate_date(self, value):
        max_date = datetime.now() + timedelta(days=180)  # 6 ماه آینده
        if value > max_date.date():
            raise serializers.ValidationError(
                "The date cannot be more than 6 months in the future."
            )
        return value


class MedicalTestPrescriptionItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalTestPrescriptionItem
        fields = ["test", "date"]
        read_only_fields = ["id"]


class MedicalTestCreateUpdateSerializer(serializers.Serializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    comment = serializers.CharField(required=False, allow_null=True)
    use_insurance = serializers.BooleanField(required=False)
    presc_items = MedicalTestPrescriptionItemCreateUpdateSerializer(many=True)


class MedicalTestGroupSerializer(serializers.ModelSerializer):
    presc_items = MedicalTestPrescriptionItemSerializer(many=True)

    class Meta:
        model = MedicalTestPrescriptionGroup
        fields = ["id", "date", "comment", "tamin_tracking_code", "presc_items"]
        read_only_fields = ["id"]


class MedicalTestFavItemRetrieveListSerializer(serializers.ModelSerializer):
    test = MedicalTestInsuranceSerializer()

    class Meta:
        model = MedicalTestFavoriteItem
        fields = ["id", "test"]
        read_only_fields = ["id"]


class MedicalTestFavoriteGroupReadSerializer(serializers.ModelSerializer):
    items = MedicalTestFavItemRetrieveListSerializer(many=True)

    class Meta:
        model = MedicalTestFavoriteGroup
        fields = ["id", "name", "items"]
        read_only_fields = ["id", "ite"]


class MedicalTestFavItemCreateUpdate(serializers.ModelSerializer):
    class Meta:
        model = MedicalTestFavoriteItem
        fields = ["id", "test"]
        read_only_fields = ["id"]


class MedicalTestFavoriteGroupCreateUpdateSerializer(serializers.ModelSerializer):
    items = MedicalTestFavItemCreateUpdate(many=True)

    class Meta:
        model = MedicalTestFavoriteGroup
        fields = ["id", "name", "items"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        medicine_favorite_group = MedicalTestFavoriteGroup.objects.create(
            **validated_data
        )
        for item_data in items_data:
            MedicalTestFavoriteItem.objects.create(
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
            MedicalTestFavoriteItem.objects.create(group=instance, **item_data)

        return instance
