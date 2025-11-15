from rest_framework import serializers

from other_paraclinic_services.models import Category, OtherParaclinicService


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "concept"]
        read_only_fields = ["id"]


class OtherParaclinicServicesSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = OtherParaclinicService
        fields = ["id", "name", "is_insured", "category"]
        read_only_fields = ["id"]
