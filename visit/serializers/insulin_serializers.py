from rest_framework import serializers

from visit.models.insulin_prescription_models import (
    Insulin,
    InsulinPrescriptionGroup,
    InsulinPrescriptionItem,
)


class InsulinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insulin
        fields = ["id", "name", "category"]
        read_only_fields = ["id"]


class PrescriptionItemReadSerializer(serializers.ModelSerializer):
    insulin = InsulinSerializer()

    class Meta:
        model = InsulinPrescriptionItem
        fields = ["id", "insulin", "meal", "dose"]
        read_only_fields = ["id"]


class PrescriptionItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsulinPrescriptionItem
        fields = ["id", "insulin", "meal", "dose"]
        read_only_fields = ["id"]


class InsulinPrescriptionGroupReadSerializer(serializers.ModelSerializer):
    presc_items = PrescriptionItemReadSerializer(many=True)

    class Meta:
        model = InsulinPrescriptionGroup
        fields = ["id", "date", "patient", "comment", "presc_items"]


class InsulinPrescriptionGroupCreateUpadteSerializer(serializers.ModelSerializer):
    presc_items = PrescriptionItemCreateUpdateSerializer(many=True)

    class Meta:
        model = InsulinPrescriptionGroup
        fields = ["id", "comment", "patient", "presc_items"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        items_data = validated_data.pop("presc_items")
        medicine_favorite_group = InsulinPrescriptionGroup.objects.create(
            created_by=self.context["request"].user, **validated_data
        )
        for item_data in items_data:
            InsulinPrescriptionItem.objects.create(
                group=medicine_favorite_group, **item_data
            )
        return medicine_favorite_group

    def update(self, instance, validated_data):
        items_data = validated_data.pop("presc_items")
        instance.comment = validated_data.get("comment", instance.comment)
        instance.save()

        # Delete existing items
        instance.presc_items.all().delete()

        # Create new items
        for item_data in items_data:
            InsulinPrescriptionItem.objects.create(group=instance, **item_data)

        return instance
