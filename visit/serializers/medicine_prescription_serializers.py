from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from medicines.serializers import MedicineSerializer
from patient.models import Patient
from visit.models import (
    MedicineAmount,
    MedicineInstruction,
    MedicinePrescriptionItem,
    MedicinePrescriptionGroup,
)
from visit.models.medicine_models import (
    MedicineFavoriteGroup,
    MedicinePrescriptionFavoriteItem,
)


class MedicinePrescriptionItemCreateUpdateSerializer(ModelSerializer):
    # do date
    doDate = serializers.DateField(required=False)
    repeat_count = serializers.IntegerField(required=False)

    class Meta:
        model = MedicinePrescriptionItem
        fields = [
            "id",
            "medicine",
            "amount",
            "instruction",
            "usage",
            "quantity",
            "repeat",
            "repeat_count",
            "comment",
            "doDate",
            "is_note",
        ]
        read_only_fields = ["id"]


class MedicineInstructionSerializer(ModelSerializer):
    class Meta:
        model = MedicineInstruction
        fields = ["id", "concept"]
        read_only_fields = ["id"]


class MedicineRepeatSerializer(ModelSerializer):
    class Meta:
        model = MedicineInstruction
        fields = ["id", "concept"]
        read_only_fields = ["id"]


class MedicineAmountSerializer(ModelSerializer):
    class Meta:
        model = MedicineAmount
        fields = ["id", "concept"]
        read_only_fields = ["id"]


class MedicinePrescriptionGroupCreateUpdateSerializer(serializers.Serializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    comment = serializers.CharField(required=False, allow_null=True)
    use_insurance = serializers.BooleanField(required=False)
    presc_items = MedicinePrescriptionItemCreateUpdateSerializer(many=True)


class MedicinePrescriptionItemRetrieveListSerializer(ModelSerializer):
    medicine = MedicineSerializer()
    amount = MedicineAmountSerializer()
    instruction = MedicineInstructionSerializer()
    # usage =

    class Meta:
        model = MedicinePrescriptionItem
        fields = [
            "id",
            "medicine",
            "amount",
            "instruction",
            "quantity",
            "comment",
            "repeat",
            "repeat_count",
            "doDate",
            "is_note",
        ]
        read_only_fields = ["id"]


class MedicinePrescriptionGroupSerializer(ModelSerializer):
    # patient = PatientReducedSerializer()
    presc_items = MedicinePrescriptionItemRetrieveListSerializer(many=True)

    class Meta:
        model = MedicinePrescriptionGroup
        fields = ["id", "date", "comment", "tamin_tracking_code", "presc_items"]
        read_only_fields = ["id"]


class MedicinePrescriptionFavItemRetrieveListSerializer(ModelSerializer):
    medicine = MedicineSerializer()
    amount = MedicineAmountSerializer()
    instruction = MedicineInstructionSerializer()
    # usage =

    class Meta:
        model = MedicinePrescriptionFavoriteItem
        fields = ["id", "medicine", "amount", "instruction", "quantity", "comment"]
        read_only_fields = ["id"]


class MedicineFavoriteGroupReadSerializer(ModelSerializer):
    items = MedicinePrescriptionFavItemRetrieveListSerializer(many=True)

    class Meta:
        model = MedicineFavoriteGroup
        fields = ["id", "name", "items"]
        read_only_fields = ["id"]


class MedicinePrescriptionFavItemCreateUpdate(ModelSerializer):
    class Meta:
        model = MedicinePrescriptionFavoriteItem
        fields = ["id", "medicine", "amount", "instruction", "quantity", "comment"]
        read_only_fields = ["id"]


class MedicineFavoriteGroupCreateUpdateSerializer(ModelSerializer):
    items = MedicinePrescriptionFavItemCreateUpdate(many=True)

    class Meta:
        model = MedicineFavoriteGroup
        fields = ["id", "name", "items"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        medicine_favorite_group = MedicineFavoriteGroup.objects.create(**validated_data)
        for item_data in items_data:
            MedicinePrescriptionFavoriteItem.objects.create(
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
            MedicinePrescriptionFavoriteItem.objects.create(group=instance, **item_data)

        return instance


# class MedicineFavoritesSerializer(ModelSerializer):
#     class Meta:
#         model = MedicineFavorite
#         fields = ["id", "item"]
#         read_only_fields = ["id"]
