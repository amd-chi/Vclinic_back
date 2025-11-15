from rest_framework import viewsets, generics
from rest_framework_simplejwt.authentication import JWTAuthentication
from referral_services.models import ReferralDoctor
from user.permissions import IsSecretary
from insurance.connection.tamin_connection import (
    TaminClient,
    TokenError,
    PatientNotFound,
)
from patient.models.appointment_models import Appointment
from visit import serializers
from visit.models import VisitInsurance
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db import models
from visit.models.history_models import Story
from visit.models.medical_imaging_models import MedicalImagingPrescriptionGroup
from visit.models.medical_test_models import (
    MedicalTestPrescriptionGroup,
    MedicalTestPrescriptionItem,
)
from visit.models.medicine_models import MedicinePrescriptionGroup
from visit.models.other_paraclinic_models import (
    OtherParaclinicServicesPrescriptionGroup,
)
from visit.models.visit_models import ClinicData, Visit, VisitPrice
from rest_framework.views import APIView
from datetime import time
from visit.serializers.visit_serializer import (
    ClinicDataSerializer,
    VisitPriceSerializer,
    VisitSerializerCreate,
    VisitSerializerRead,
    VisitSerializerUpdate,
)
from rest_framework.decorators import action
import datetime


@extend_schema_view(
    get=extend_schema(tags=["Clinic - Data"], description="Retrieve the clinic data."),
    put=extend_schema(
        tags=["Clinic - Data"], description="Update the existing clinic data."
    ),
    patch=extend_schema(
        tags=["Clinic - Data"], description="Partially update the clinic data."
    ),
)
class GetDoctorBaseView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def get(self, request):
        # doctor = request.user.doctor
        token = request.headers.get("Tamin-Token")
        if not token:
            return Response(
                {"error": "Tamin Token is required for insurance usage"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            taminClient = TaminClient(token)
            doctor = taminClient.getCurrentUser()["data"]
            data = {
                "name": doctor["firstName"] + " " + doctor["lastName"],
                "medical_education_number": doctor["docId"],
                "speciality": doctor["docSpec"]["specDesc"],
            }
            return Response(data, status=status.HTTP_200_OK)
        except TokenError:
            return Response(
                {"error": "Tamin Token is invalid or expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(tags=["Clinic - Data"], description="Retrieve the clinic data.")
class ClinicDataView(generics.RetrieveUpdateAPIView):
    queryset = ClinicData.objects.all()
    serializer_class = ClinicDataSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_queryset().get()
            serializer = self.get_serializer(instance, data=request.data)
        except ClinicData.DoesNotExist:
            serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK if instance else status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        """
        Always return the single instance of ClinicData or raise NotFound if it does not exist.
        """
        try:
            return ClinicData.objects.get()
        except ClinicData.DoesNotExist:
            return None


@extend_schema_view(
    list=extend_schema(tags=["Visit - Visit"]),
    retrieve=extend_schema(tags=["Visit - Visit"]),
    create=extend_schema(tags=["Visit - Visit"]),
    update=extend_schema(tags=["Visit - Visit"]),
    destroy=extend_schema(tags=["Visit - Visit"]),
    partial_update=extend_schema(tags=["Visit - Visit"]),
    brief=extend_schema(tags=["Visit - Visit"]),
)
class VisitViewSet(viewsets.ModelViewSet):
    serializer_class = VisitSerializerCreate
    queryset = Visit.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def get_queryset(self):
        # the last 30
        if self.action == "list":
            return super().get_queryset().order_by("-date")[:250]
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return VisitSerializerRead
        elif self.action in ["update", "partial_update"]:
            return VisitSerializerUpdate
        return super().get_serializer_class()

    @action(detail=False, methods=["get"], url_path="brief")
    def brief(self, request):
        today = datetime.date.today()
        total_fee = (
            Visit.objects.filter(date=today).aggregate(total_fee=models.Sum("fee"))[
                "total_fee"
            ]
            or 0
        )
        visited = Visit.objects.filter(date=today).count()
        today_min = datetime.datetime.combine(today, time.min)
        today_max = datetime.datetime.combine(today, time.max)
        appointments = Appointment.objects.filter(
            datetime__range=(today_min, today_max)
        ).count()
        data = {
            "total_fee": total_fee,
            "visited": visited,
            "appointments": appointments,
        }
        return Response(data)

    @action(detail=False, methods=["get"], url_path="today-actions")
    def today_actions(self, request):
        today = datetime.date.today()

        today_min = datetime.datetime.combine(today, time.min)
        today_max = datetime.datetime.combine(today, time.max)
        patient_id = request.query_params.get("patient_id")
        if not patient_id:
            return Response(
                {"error": "Patient ID is    required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        medicine_submitted_today = MedicinePrescriptionGroup.objects.filter(
            patient=patient_id, date=today
        ).exists()
        imaging_submitted_today = MedicalImagingPrescriptionGroup.objects.filter(
            patient=patient_id, date=today
        ).exists()
        medical_test_submitted_today = MedicalTestPrescriptionGroup.objects.filter(
            patient=patient_id, date=today
        ).exists()
        referral_submitted_today = ReferralDoctor.objects.filter(
            patient=patient_id, created_at__range=(today_min, today_max)
        ).exists()

        paraclinic_submitted_today = (
            OtherParaclinicServicesPrescriptionGroup.objects.filter(
                patient=patient_id, date=today
            ).exists()
        )

        visit_submitted_today = Visit.objects.filter(
            patient=patient_id, date=today
        ).exists()
        story_submitted_today = Story.objects.filter(
            patient=patient_id, date=today
        ).exists()

        last_visit = (
            Visit.objects.filter(patient=patient_id, date__lt=datetime.date.today())
            .order_by("-date")
            .first()
        )
        last_visit_dict = None
        if last_visit:
            last_visit_date = last_visit.date
            last_visit_date_min = datetime.datetime.combine(last_visit_date, time.min)
            last_visit_date_max = datetime.datetime.combine(last_visit_date, time.max)

            medicine_submitted_last_visit = MedicinePrescriptionGroup.objects.filter(
                patient=patient_id, date=last_visit_date
            ).exists()
            imaging_submitted_last_visit = (
                MedicalImagingPrescriptionGroup.objects.filter(
                    patient=patient_id, date=last_visit_date
                ).exists()
            )
            medical_test_submitted_last_visit = (
                MedicalTestPrescriptionGroup.objects.filter(
                    patient=patient_id, date=last_visit_date
                ).exists()
            )
            referral_submitted_last_visit = ReferralDoctor.objects.filter(
                patient=patient_id,
                created_at__range=(last_visit_date_min, last_visit_date_max),
            ).exists()
            paraclinic_submitted_last_visit = (
                OtherParaclinicServicesPrescriptionGroup.objects.filter(
                    patient=patient_id, date=last_visit_date
                ).exists()
            )
            story_submitted_last_visit = Story.objects.filter(
                patient=patient_id, date=last_visit_date
            ).exists()

            last_visit_dict = {
                "medicine_submitted": medicine_submitted_last_visit,
                "imaging_submitted": imaging_submitted_last_visit,
                "medical_test_submitted": medical_test_submitted_last_visit,
                "referral_submitted": referral_submitted_last_visit,
                "paraclinic_submitted": paraclinic_submitted_last_visit,
                "story_submitted": story_submitted_last_visit,
            }

        data = {
            "today": {
                "medicine_submitted": medicine_submitted_today,
                "imaging_submitted": imaging_submitted_today,
                "medical_test_submitted": medical_test_submitted_today,
                "referral_submitted": referral_submitted_today,
                "paraclinic_submitted": paraclinic_submitted_today,
                "visit_submitted": visit_submitted_today,
                "story_submitted": story_submitted_today,
            },
            "last_visit": last_visit_dict,
        }

        return Response(data, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(tags=["Visit - Visit"]),
    retrieve=extend_schema(tags=["Visit - Visit"]),
    create=extend_schema(tags=["Visit - Visit"]),
    update=extend_schema(tags=["Visit - Visit"]),
    destroy=extend_schema(tags=["Visit - Visit"]),
    partial_update=extend_schema(tags=["Visit - Visit"]),
)
class VisitInsuranceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.VisitInsuranceSerializer
    queryset = VisitInsurance.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def create(self, request):
        patient = request.data.get("patient")
        comment = request.data.get("comment")
        token = request.headers.get("Tamin-Token")
        if not token:
            return Response(
                {"error": "Tamin Token is required for insurance usage"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        taminClient = TaminClient(token)
        try:
            response = taminClient.visit(patient.national_id, comment=comment)
        except TokenError:
            return Response(
                {"error": "Tamin Token is invalid or expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except PatientNotFound:
            return Response(
                {"error": "Patient not found in insurance records"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tamin_tracking_code = response["data"]["noteHead"]["trackingCode"]
        visit = VisitInsurance.objects.create(
            patient=patient,
            comment=comment,
            tamin_tracking_code=(tamin_tracking_code),
        )
        return Response(
            {
                "id": visit.id,
                "tamin_tracking_code": tamin_tracking_code,
            },
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Visit - Visit"])
class VisitPriceView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def get(self, request):
        patient_id = request.query_params.get("patient_id")
        visit_price, created = VisitPrice.objects.get_or_create(
            defaults={"price": 100}  # default value
        )

        last_item = (
            MedicalTestPrescriptionItem.objects.filter(group__patient_id=patient_id)
            .order_by("-date")
            .first()
        )
        last_test_date = last_item.date if last_item else None

        # serializer = VisitPriceSerializer(visit_price, last_item_date)
        return Response(
            {"price": visit_price.price, "last_test_date": last_test_date},
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        # Update the existing record or create a new one
        serializer = VisitPriceSerializer(data=request.data)
        if serializer.is_valid():
            VisitPrice.objects.update_or_create(defaults=serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
