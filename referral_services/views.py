from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import viewsets
from user.permissions import IsSecretary
from referral_services.serializers import (
    DoctorCreateSerializer,
    DoctorReadSerializer,
    ReferralServicesCreateSerializer,
    ReferralServicesReadSerializer,
    SpecialitySerializer,
)
from . import models
from drf_spectacular.utils import extend_schema, extend_schema_view
# from django.shortcuts import get_object_or_404


@extend_schema_view(
    list=extend_schema(tags=["Referral Services"]),
    retrieve=extend_schema(tags=["Referral Services"]),
    create=extend_schema(tags=["Referral Services"]),
    update=extend_schema(tags=["Referral Services"]),
    destroy=extend_schema(tags=["Referral Services"]),
    partial_update=extend_schema(tags=["Referral Services"]),
)
class SpecialityViewSet(viewsets.ModelViewSet):
    serializer_class = SpecialitySerializer
    queryset = models.DoctorSpeciality.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]


@extend_schema_view(
    list=extend_schema(tags=["Referral Services"]),
    retrieve=extend_schema(tags=["Referral Services"]),
    create=extend_schema(tags=["Referral Services"]),
    update=extend_schema(tags=["Referral Services"]),
    destroy=extend_schema(tags=["Referral Services"]),
    partial_update=extend_schema(tags=["Referral Services"]),
)
class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorReadSerializer
    queryset = models.Doctor.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return DoctorCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", None)
        if search_query:
            queryset = queryset.filter(name__icontains=search_query)
        return queryset


@extend_schema_view(
    list=extend_schema(tags=["Referral Services"]),
    retrieve=extend_schema(tags=["Referral Services"]),
    create=extend_schema(tags=["Referral Services"]),
    update=extend_schema(tags=["Referral Services"]),
    destroy=extend_schema(tags=["Referral Services"]),
    partial_update=extend_schema(tags=["Referral Services"]),
)
class ReferralDoctorViewSet(viewsets.ModelViewSet):
    serializer_class = ReferralServicesReadSerializer
    queryset = models.ReferralDoctor.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return ReferralServicesCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        queryset = super().get_queryset()
        patient = self.request.query_params.get("patient", None)
        if patient:
            queryset = queryset.filter(patient_id=patient)
        return queryset
