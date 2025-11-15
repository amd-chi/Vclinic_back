from rest_framework import serializers
from datetime import datetime, timedelta
from other_paraclinic_services.serializers import OtherParaclinicServicesSerializer
from patient.models import Patient
from visit.models.other_paraclinic_models import (
    OtherParaclinicFavoriteGroup,
    OtherParaclinicFavoriteItem,
    OtherParaclinicServicesPrescriptionGroup,
    OtherParaclinicServicesPrescriptionItem,
)


class PrescriptionItemForReadSerializer(serializers.ModelSerializer):
    service = OtherParaclinicServicesSerializer()

    class Meta:
        model = OtherParaclinicServicesPrescriptionItem
        fields = ["id", "service", "date"]
        read_only_fields = ["id"]


class PrescriptionItemForCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OtherParaclinicServicesPrescriptionItem
        fields = ["service", "date"]
        read_only_fields = ["id"]

    def validate_date(self, value):
        max_date = datetime.now() + timedelta(days=180)  # 6 ماه آینده
        if value > max_date.date():
            raise serializers.ValidationError(
                "The date cannot be more than 6 months in the future."
            )
        return value


class PrescriptionGroupCreateUpdateSerializer(serializers.Serializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    comment = serializers.CharField(required=False)
    use_insurance = serializers.BooleanField(required=False)
    presc_items = PrescriptionItemForCreateUpdateSerializer(many=True)


class PrescriptionGroupReadSerializer(serializers.ModelSerializer):
    presc_items = PrescriptionItemForReadSerializer(many=True)

    class Meta:
        model = OtherParaclinicServicesPrescriptionGroup
        fields = [
            "id",
            "date",
            "comment",
            "tamin_tracking_code",
            "presc_items",
            "patient",
        ]
        read_only_fields = ["id"]


class PrescriptionFavItemRetrieveListSerializer(serializers.ModelSerializer):
    service = OtherParaclinicServicesSerializer()

    class Meta:
        model = OtherParaclinicFavoriteItem
        fields = ["id", "service"]
        read_only_fields = ["id"]


class PrescriptionFavoriteGroupReadSerializer(serializers.ModelSerializer):
    items = PrescriptionFavItemRetrieveListSerializer(many=True)

    class Meta:
        model = OtherParaclinicFavoriteGroup
        fields = ["id", "name", "items"]
        read_only_fields = ["id", "items"]


class PrescriptionFavItemCreateUpdateSer(serializers.ModelSerializer):
    class Meta:
        model = OtherParaclinicFavoriteItem
        fields = ["id", "service"]
        read_only_fields = ["id"]


class PrescriptionFavoriteGroupCreateUpdateSerializer(serializers.ModelSerializer):
    items = PrescriptionFavItemCreateUpdateSer(many=True)

    class Meta:
        model = OtherParaclinicFavoriteGroup
        fields = ["id", "name", "items"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        favorite_group = OtherParaclinicFavoriteGroup.objects.create(**validated_data)
        for item_data in items_data:
            OtherParaclinicFavoriteItem.objects.create(
                group=favorite_group, **item_data
            )
        return favorite_group

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items")
        instance.name = validated_data.get("name", instance.name)
        instance.save()

        # Delete existing items
        instance.items.all().delete()

        # Create new items
        for item_data in items_data:
            OtherParaclinicFavoriteItem.objects.create(group=instance, **item_data)

        return instance
