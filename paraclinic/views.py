from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from paraclinic import serializers
from user.permissions import IsSecretary
from . import models
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(tags=["Paraclinic"]),
    retrieve=extend_schema(tags=["Paraclinic"]),
    create=extend_schema(tags=["Paraclinic"]),
    update=extend_schema(tags=["Paraclinic"]),
    destroy=extend_schema(tags=["Paraclinic"]),
    partial_update=extend_schema(tags=["Paraclinic"]),
)
class ParaclinicResultViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ParaclinicResultSerializer
    queryset = models.ParaclinicResult.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    # def get_serializer_class(self):
    #     if self.action in ["retrieve", "list"]:
    #         return serializers.MedicalImagingResultDetailSerializer
    #     return self.serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get("patient", None)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)
