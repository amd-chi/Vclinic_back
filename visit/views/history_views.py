from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from user.permissions import IsSecretary
from django.db.models import Q
from medical_tests.models import TestMetric
from medical_tests.serializers.metric_serializers import TestMetricSerializer
from visit import serializers
from visit.models.history_models import (
    MedicalImpression,
    PatientHistoryBasic,
    PatientImpressionItem,
    Story,
    ThyroidHistory,
)
from drf_spectacular.utils import extend_schema, extend_schema_view
from visit.models.medical_imaging_models import BMDRecordGroup
from visit.serializers.history_serializers import (
    BMDRecordGroupCreateSerializer,
    BMDRecordGroupReadSerializer,
    PatientImpressionSerializerGet,
    PatientImpressionSerializerCreate,
    PatientThyroidHistorySerializer,
    StorySerializer,
)


@extend_schema_view(
    list=extend_schema(tags=["Visit - History"]),
    retrieve=extend_schema(tags=["Visit - History"]),
    create=extend_schema(tags=["Visit - History"]),
    update=extend_schema(tags=["Visit - History"]),
    destroy=extend_schema(tags=["Visit - History"]),
    partial_update=extend_schema(tags=["Visit - History"]),
)
class BMDRecordViewset(viewsets.ModelViewSet):
    serializer_class = BMDRecordGroupCreateSerializer
    queryset = BMDRecordGroup.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get("patient", None)
        if patient_id:
            queryset = queryset.filter(patient=patient_id)
        return queryset

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return BMDRecordGroupReadSerializer
        return super().get_serializer_class()


@extend_schema_view(
    list=extend_schema(tags=["Visit - History"]),
    retrieve=extend_schema(tags=["Visit - History"]),
    create=extend_schema(tags=["Visit - History"]),
    update=extend_schema(tags=["Visit - History"]),
    destroy=extend_schema(tags=["Visit - History"]),
    partial_update=extend_schema(tags=["Visit - History"]),
    get_by_patient=extend_schema(tags=["Visit - History"]),
)
class PatientHistoryBasicViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PatientHistorySerializer
    queryset = PatientHistoryBasic.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    @action(detail=False, methods=["get"], url_path="by-patient/(?P<patient_id>[^/.]+)")
    def get_by_patient(self, request, patient_id=None):
        try:
            history = PatientHistoryBasic.objects.get(patient__id=patient_id)
        except PatientHistoryBasic.DoesNotExist:
            return Response(
                {"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
            )
        serializer = self.get_serializer(history)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(tags=["Visit - History"]),
    retrieve=extend_schema(tags=["Visit - History"]),
    create=extend_schema(tags=["Visit - History"]),
    update=extend_schema(tags=["Visit - History"]),
    destroy=extend_schema(tags=["Visit - History"]),
    partial_update=extend_schema(tags=["Visit - History"]),
)
class MedicalImpressionsViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MedicalImpressionSerializer
    queryset = MedicalImpression.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    # def get_serializer_class(self):
    #     if self.action == "list" and self.request.query_params.get("search"):
    #         return serializers.PatientSearchSerializer
    #     return self.serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query))
        return queryset


@extend_schema_view(
    list=extend_schema(tags=["Visit - History"]),
    retrieve=extend_schema(tags=["Visit - History"]),
    create=extend_schema(tags=["Visit - History"]),
    update=extend_schema(tags=["Visit - History"]),
    destroy=extend_schema(tags=["Visit - History"]),
    partial_update=extend_schema(tags=["Visit - History"]),
)
class PatientImpressionItemViewSet(viewsets.ModelViewSet):
    serializer_class = PatientImpressionSerializerCreate
    queryset = PatientImpressionItem.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(
            created_by=self.request.user,
        )

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return PatientImpressionSerializerGet
        return self.serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        patient = self.request.query_params.get("patient", None)
        if patient:
            queryset = queryset.filter(patient=patient)
        return queryset


@extend_schema_view(
    list=extend_schema(tags=["Visit - History"]),
    retrieve=extend_schema(tags=["Visit - History"]),
    create=extend_schema(tags=["Visit - History"]),
    update=extend_schema(tags=["Visit - History"]),
    destroy=extend_schema(tags=["Visit - History"]),
    partial_update=extend_schema(tags=["Visit - History"]),
)
class StoriesViewSet(viewsets.ModelViewSet):
    serializer_class = StorySerializer
    queryset = Story.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        patient = self.request.query_params.get("patient", None)
        if patient:
            queryset = queryset.filter(patient=patient)
        return queryset

    def perform_create(self, serializer):
        return serializer.save(
            created_by=self.request.user,
        )


@extend_schema(tags=["Visit - History"])
class MetricsWithResultsView(generics.ListAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TestMetricSerializer

    def get_queryset(self):
        patient_id = self.kwargs.get("patient_id")
        return TestMetric.objects.filter(
            result_items__group__patient_id=patient_id
        ).distinct()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["patient_id"] = self.kwargs.get("patient_id")
        return context


@extend_schema_view(
    list=extend_schema(tags=["Visit - History"]),
    retrieve=extend_schema(tags=["Visit - History"]),
    create=extend_schema(tags=["Visit - History"]),
    update=extend_schema(tags=["Visit - History"]),
    destroy=extend_schema(tags=["Visit - History"]),
    partial_update=extend_schema(tags=["Visit - History"]),
)
class ThyroidHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = PatientThyroidHistorySerializer
    queryset = ThyroidHistory.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(
            created_by=self.request.user,
        )

    def get_queryset(self):
        queryset = super().get_queryset()
        patient = self.request.query_params.get("patient", None)
        if patient:
            queryset = queryset.filter(patient=patient)
        return queryset
