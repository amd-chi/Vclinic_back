from rest_framework.viewsets import ModelViewSet
from user.permissions import IsSecretary
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, extend_schema_view
from visit.models.insulin_prescription_models import (
    Insulin,
    InsulinPrescriptionGroup,
)
from visit.serializers.insulin_serializers import (
    InsulinPrescriptionGroupCreateUpadteSerializer,
    InsulinPrescriptionGroupReadSerializer,
    InsulinSerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["Visit - Insulin"]),
    retrieve=extend_schema(tags=["Visit - Insulin"]),
    create=extend_schema(tags=["Visit - Insulin"]),
    update=extend_schema(tags=["Visit - Insulin"]),
    destroy=extend_schema(tags=["Visit - Insulin"]),
    partial_update=extend_schema(tags=["Visit - Insulin"]),
)
class InsulinViewSet(ModelViewSet):
    serializer_class = InsulinSerializer
    queryset = Insulin.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def get_queryset(self):
        queryset = super().get_queryset()

        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset


@extend_schema_view(
    list=extend_schema(tags=["Visit - Insulin"]),
    retrieve=extend_schema(tags=["Visit - Insulin"]),
    create=extend_schema(tags=["Visit - Insulin"]),
    update=extend_schema(tags=["Visit - Insulin"]),
    destroy=extend_schema(tags=["Visit - Insulin"]),
    partial_update=extend_schema(tags=["Visit - Insulin"]),
)
class InsulinPrescriptionGroupViewSet(ModelViewSet):
    serializer_class = InsulinPrescriptionGroupReadSerializer
    queryset = InsulinPrescriptionGroup.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def get_queryset(self):
        queryset = super().get_queryset()
        patient = self.request.query_params.get("patient", None)
        if patient:
            queryset = queryset.filter(patient=patient)
        return queryset

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return InsulinPrescriptionGroupCreateUpadteSerializer
        return super().get_serializer_class()
