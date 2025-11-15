from rest_framework import serializers

from paraclinic.models import ParaclinicResult


class ParaclinicResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParaclinicResult
        fields = [
            "id",
            "title",
            "date",
            "comment",
            "patient",
        ]
        read_only_fields = ["id"]
