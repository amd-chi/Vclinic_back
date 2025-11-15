from django.db.utils import IntegrityError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from insurance.connection.tamin_connection import (
    InvalidTokenError,
    TaminClient,
    TokenError,
)
from medical_tests.serializers.favorite_groups_serializers import (
    MedicalTestResultFavoriteGroupCreateSerializer,
    MedicalTestResultFavoriteGroupReadSerializer,
)
from medical_tests.serializers.laboratory_serializers import LaboratorySerializer
from medical_tests.serializers.metric_serializers import (
    MetricCreateUpdateSerializer,
    MetricReadSerializer,
)
from medical_tests.serializers.result_item_serializers import (
    TestResultItemVisitedSerializer,
)
from medical_tests.serializers.test_group_serializers import (
    TestResultGroupCreateUpdateSerializer,
    TestResultGroupListSerializer,
    TestResultGroupReadSerializer,
)
from medical_tests.serializers.test_insurance_serializers import (
    MedicalTestInsuranceSerializer,
)
from medical_tests.serializers.unit_serializers import UnitSerializer
from . import models
from django.db.models import Q, RestrictedError
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(tags=["Medical Tests"]),
    retrieve=extend_schema(tags=["Medical Tests"]),
    create=extend_schema(tags=["Medical Tests"]),
    update=extend_schema(tags=["Medical Tests"]),
    destroy=extend_schema(tags=["Medical Tests"]),
    partial_update=extend_schema(tags=["Medical Tests"]),
)
class TestResultGroupViewSet(viewsets.ModelViewSet):
    serializer_class = TestResultGroupReadSerializer
    queryset = models.TestResultGroup.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    filterset_fields = ["patient"]

    def get_serializer_class(self):
        if self.action == "list" and self.request.query_params.get("patient"):
            return TestResultGroupListSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return TestResultGroupCreateUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get("patient", None)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset


@extend_schema_view(
    list=extend_schema(tags=["Medical Tests"]),
    retrieve=extend_schema(tags=["Medical Tests"]),
    create=extend_schema(tags=["Medical Tests"]),
    update=extend_schema(tags=["Medical Tests"]),
    destroy=extend_schema(tags=["Medical Tests"]),
    partial_update=extend_schema(tags=["Medical Tests"]),
)
class LaboratoryViewSet(viewsets.ModelViewSet):
    serializer_class = LaboratorySerializer
    queryset = models.Laboratory.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query))
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except RestrictedError:
            return Response(
                {"error": "Cannot delete this object because it is protected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema_view(
    list=extend_schema(tags=["Medical Tests"]),
    retrieve=extend_schema(tags=["Medical Tests"]),
    create=extend_schema(tags=["Medical Tests"]),
    update=extend_schema(tags=["Medical Tests"]),
    destroy=extend_schema(tags=["Medical Tests"]),
    partial_update=extend_schema(tags=["Medical Tests"]),
)
class TestMetricViewSet(viewsets.ModelViewSet):
    serializer_class = MetricReadSerializer
    queryset = models.TestMetric.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return MetricCreateUpdateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query))
        return queryset


@extend_schema_view(
    list=extend_schema(tags=["Medical Tests"]),
    retrieve=extend_schema(tags=["Medical Tests"]),
    create=extend_schema(tags=["Medical Tests"]),
    update=extend_schema(tags=["Medical Tests"]),
    destroy=extend_schema(tags=["Medical Tests"]),
    partial_update=extend_schema(tags=["Medical Tests"]),
)
class UnitsViewSet(viewsets.ModelViewSet):
    serializer_class = UnitSerializer
    queryset = models.MetricUnit.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
        except RestrictedError:
            return Response(
                {"error": "Cannot delete this object because it is protected."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(Q(name__icontains=search_query))
        return queryset


def extract_name(name: str):
    if "-" in name:
        # find the first block after passing two -
        try:
            return name.split("-")[2].strip()
        except Exception:
            return name
    return name


@extend_schema_view(
    list=extend_schema(tags=["Medical Tests"]),
    retrieve=extend_schema(tags=["Medical Tests"]),
    create=extend_schema(tags=["Medical Tests"]),
    update=extend_schema(tags=["Medical Tests"]),
    destroy=extend_schema(tags=["Medical Tests"]),
    partial_update=extend_schema(tags=["Medical Tests"]),
)
class MedicalTestInsuranceView(viewsets.ModelViewSet):
    serializer_class = MedicalTestInsuranceSerializer
    queryset = models.MedicalTestInsurance.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", None)
        if search_query:
            token = self.request.headers.get("Tamin-Token")
            if not token:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) | Q(code__icontains=search_query)
                )
            else:
                taminClient = TaminClient(token)
                try:
                    tamin_tests_response = taminClient.searchMedicalTests(search_query)
                    tamin_tests = tamin_tests_response["data"]["list"]

                    # دریافت تمامی tamin_id های موجود در دیتابیس
                    available_in_db_tests = models.MedicalTestInsurance.objects.filter(
                        tamin_id__in=[tamin_test["srvId"] for tamin_test in tamin_tests]
                    )
                    available_in_db_srv_ids = set(
                        available_in_db_tests.values_list("tamin_id", flat=True)
                    )

                    # آماده‌سازی لیست جدید برای اضافه شدن
                    new_tests = []
                    for tamin_test in tamin_tests:
                        if tamin_test["srvId"] not in available_in_db_srv_ids:
                            new_tests.append(
                                models.MedicalTestInsurance(
                                    name=tamin_test["srvName"],
                                    is_insured=True
                                    if tamin_test["status"] == "1"
                                    else False,
                                    code=tamin_test["srvCode"],
                                    tamin_json=tamin_test,
                                    tamin_id=tamin_test["srvId"],
                                )
                            )
                        else:
                            # update the existing test
                            test = available_in_db_tests.get(
                                tamin_id=tamin_test["srvId"]
                            )
                            test.name = tamin_test["srvName"]
                            test.code = tamin_test["srvCode"]
                            test.is_insured = (
                                True if tamin_test["status"] == "1" else False
                            )
                            test.tamin_json = tamin_test

                    # اگر داده جدیدی وجود داشته باشد، آنها را bulk_create می‌کنیم
                    if new_tests:
                        for test in new_tests:
                            try:
                                test.save()
                            except IntegrityError:
                                pass
                    if available_in_db_tests:
                        models.MedicalTestInsurance.objects.bulk_update(
                            available_in_db_tests,
                            ["name", "is_insured", "tamin_json", "code"],
                        )
                    # سپس داده‌های جدید یا به‌روز شده را به queryset اضافه می‌کنیم
                    queryset = models.MedicalTestInsurance.objects.filter(
                        tamin_id__in=[tamin_test["srvId"] for tamin_test in tamin_tests]
                    )

                except TokenError:
                    raise InvalidTokenError()
        return queryset


@extend_schema_view(
    update=extend_schema(tags=["Medical Tests"]),
    partial_update=extend_schema(tags=["Medical Tests"]),
)
class TestResultItemVisitedViewSet(viewsets.GenericViewSet, mixins.UpdateModelMixin):
    serializer_class = TestResultItemVisitedSerializer
    queryset = models.TestResultItem.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["Medical Tests"]),
    retrieve=extend_schema(tags=["Medical Tests"]),
    create=extend_schema(tags=["Medical Tests"]),
    update=extend_schema(tags=["Medical Tests"]),
    destroy=extend_schema(tags=["Medical Tests"]),
    partial_update=extend_schema(tags=["Medical Tests"]),
)
class MedicalTestResultFavoriteGroupViewSet(viewsets.ModelViewSet):
    serializer_class = MedicalTestResultFavoriteGroupReadSerializer
    queryset = models.TestResultFavoriteGroup.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if (
            self.action == "create"
            or self.action == "update"
            or self.action == "partial_update"
        ):
            return MedicalTestResultFavoriteGroupCreateSerializer
        return super().get_serializer_class()
