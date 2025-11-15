from rest_framework import serializers
from . import models


class MedicineSerializer(serializers.ModelSerializer):
    is_insurance_supported = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Medicine
        fields = [
            "id",
            "name",
            "category",
            "is_insured",
            "is_insurance_supported",
        ]
        read_only_fields = ["id"]

    def get_is_insurance_supported(self, obj):
        return obj.tamin_json is not None
