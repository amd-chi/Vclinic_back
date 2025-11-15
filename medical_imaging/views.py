from django.db.utils import IntegrityError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from insurance.connection.tamin_connection import (
    InvalidTokenError,
    TaminClient,
    TokenError,
)
from medical_imaging import serializers
from . import models
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.models import Q


@extend_schema_view(
    list=extend_schema(tags=["Medical Imaging"]),
    retrieve=extend_schema(tags=["Medical Imaging"]),
    create=extend_schema(tags=["Medical Imaging"]),
    update=extend_schema(tags=["Medical Imaging"]),
    destroy=extend_schema(tags=["Medical Imaging"]),
    partial_update=extend_schema(tags=["Medical Imaging"]),
)
class MedicalImagingInsuranceView(viewsets.ModelViewSet):
    serializer_class = serializers.MedicalImagingInsuranceSerializer
    queryset = models.MedicalImagingInsurance.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", None)
        token = self.request.headers.get("Tamin-Token")
        if search_query:
            if not token:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) | Q(code__icontains=search_query)
                )

            else:
                taminClient = TaminClient(token)
                try:
                    tamin_imaging_response = taminClient.searchMedicalImaging(
                        search_query, limit=70
                    )
                    tamin_imagings = tamin_imaging_response["data"]["list"]

                    # دریافت تمام srvCode های موجود در دیتابیس
                    availabel_in_db_imagings = (
                        models.MedicalImagingInsurance.objects.filter(
                            tamin_id__in=[
                                tamin_imaging["srvId"]
                                for tamin_imaging in tamin_imagings
                            ]
                        )
                    )
                    available_in_db_srv_ids = set(
                        availabel_in_db_imagings.values_list("tamin_id", flat=True)
                    )

                    # آماده‌سازی لیست جدید برای اضافه شدن
                    new_imagings = []
                    for tamin_imaging in tamin_imagings:
                        if tamin_imaging["srvId"] not in available_in_db_srv_ids:
                            new_imagings.append(
                                models.MedicalImagingInsurance(
                                    name=tamin_imaging["srvName"],
                                    code=tamin_imaging["srvCode"],
                                    tamin_id=tamin_imaging["srvId"],
                                    is_insured=(
                                        True
                                        if tamin_imaging["status"] == "1"
                                        else False
                                    ),
                                    tamin_json=tamin_imaging,
                                )
                            )
                        else:
                            # update the imaging
                            imaging = availabel_in_db_imagings.get(
                                tamin_id=tamin_imaging["srvId"]
                            )
                            imaging.name = tamin_imaging["srvName"]
                            imaging.code = tamin_imaging["srvCode"]
                            imaging.is_insured = (
                                True if tamin_imaging["status"] == "1" else False
                            )
                            imaging.tamin_json = tamin_imaging

                    if new_imagings:
                        for imaging in new_imagings:
                            try:
                                imaging.save()
                            except IntegrityError:
                                pass
                    if available_in_db_srv_ids:
                        models.MedicalImagingInsurance.objects.bulk_update(
                            availabel_in_db_imagings,
                            ["name", "is_insured", "tamin_json"],
                        )
                    # آپدیت queryset
                    queryset = models.MedicalImagingInsurance.objects.filter(
                        tamin_id__in=[
                            tamin_imaging["srvId"] for tamin_imaging in tamin_imagings
                        ]
                    )
                except TokenError:
                    raise InvalidTokenError()

        return queryset


@extend_schema_view(
    list=extend_schema(tags=["Medical Imaging"]),
    retrieve=extend_schema(tags=["Medical Imaging"]),
    create=extend_schema(tags=["Medical Imaging"]),
    update=extend_schema(tags=["Medical Imaging"]),
    destroy=extend_schema(tags=["Medical Imaging"]),
    partial_update=extend_schema(tags=["Medical Imaging"]),
)
class MedicalImagingResultViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MedicalImagingResultSerializer
    queryset = models.MedicalImagingResult.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return serializers.MedicalImagingResultDetailSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = super().get_queryset()
        patient_id = self.request.query_params.get("patient", None)
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


@extend_schema_view(
    list=extend_schema(tags=["Medical Imaging"]),
    retrieve=extend_schema(tags=["Medical Imaging"]),
    create=extend_schema(tags=["Medical Imaging"]),
    update=extend_schema(tags=["Medical Imaging"]),
    destroy=extend_schema(tags=["Medical Imaging"]),
    partial_update=extend_schema(tags=["Medical Imaging"]),
)
class MedicalImagingCentersViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MedicalImagingCenterSerializer
    queryset = models.MedicalImagingCenter.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset
