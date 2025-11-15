from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets, status
from appointment.models import AppointmentSlot
from patient import serializers
from patient.models import Patient
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q, Value
from django.db.models.functions import Concat
from rest_framework.viewsets import mixins
from rest_framework.views import APIView
from insurance.connection.tamin_connection import (
    TaminClient,
    TokenError,
    PatientNotFound,
)
from datetime import date
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes
from patient.models.patient_models import PreRegisterPatient
from patient.serializers.patient_serializers import (
    PatientChangePasswordSerializer,
    PatientRegisterSerializer,
)
from user.permissions import IsSecretary
from utils.sms import SMSClient
import random
import string
from django.core.cache import cache


class GetOtpView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get("phone_number")
        if not phone_number:
            return Response(
                {"error": "phone_number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Generate a 6-digit numeric OTP
        code = "".join(random.choices(string.digits, k=4))

        # 2. Cache it for 3 minutes (180 seconds)
        cache_key = f"otp_{phone_number}"
        cache.set(cache_key, code, timeout=180)

        # 3. Send the OTP
        client = SMSClient()
        client.sendOtpCode(code, phone_number)

        # 4. Return a response
        return Response({"msg": "OTP sent successfully."}, status=status.HTTP_200_OK)


class PatientRegisterView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PatientRegisterSerializer(data=request.data)
        if serializer.is_valid():
            national_id = serializer.data.get("national_id")
            first_name = serializer.data.get("first_name")
            last_name = serializer.data.get("last_name")
            phone_number = serializer.data.get("phone_number")
            otp = serializer.data.get("otp")

            # validate the otp
            cached = cache.get(f"otp_{phone_number}")
            if otp != cached:
                return Response(
                    {"msg": "otp code is wrong or expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            patient = PreRegisterPatient(
                first_name=first_name,
                last_name=last_name,
                national_id=national_id,
                mobile_number=phone_number,
            )
            patient.save()
            return Response({"id": patient.id}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    tags=["Patients"],
    parameters=[
        OpenApiParameter(
            name="national_code",
            type=OpenApiTypes.STR,
            required=True,
            location=OpenApiParameter.QUERY,
            description="National code of the patient",
        )
    ],
)
class PatientGetRegisterDataView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            national_code = request.query_params.get("national_code", None)
            if not national_code:
                return Response(
                    {"error": "National code is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            patient = Patient.objects.get(national_id=national_code)
            appointment_ahead = None
            app_query = AppointmentSlot.objects.filter(
                is_booked=True, patient=patient, date__gte=date.today()
            )
            if app_query.exists():
                app_obj = app_query.first()
                appointment_ahead = {
                    "start_time": app_obj.start_time,
                    "date": app_obj.date,
                }
            return Response(
                {
                    "first_name": patient.first_name,
                    "last_name": patient.last_name,
                    "phone_number": patient.phone_number,
                    "patient_id": patient.id,
                    "appointment_ahead": appointment_ahead,
                }
            )

        except Patient.DoesNotExist:
            return Response(
                {"error": "Patient does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


class PatientChangePasswordUser(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def put(self, request):
        # pass through PatientChangePasswordSerializer
        serializer = PatientChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # check if patient has user defined
            try:
                patient_id = serializer.data.get("patient_id")
                patient = Patient.objects.get(id=patient_id)
                if patient.user:
                    patient.user.set_password(serializer.data.get("password"))
                    patient.user.save()
                    return Response(
                        {"message": "Password changed successfully"},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Patient does not have user"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except Patient.DoesNotExist:
                return Response(
                    {"error": "Patient does not exist"},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(tags=["Patients"]),
    retrieve=extend_schema(tags=["Patients"]),
    create=extend_schema(tags=["Patients"]),
    update=extend_schema(tags=["Patients"]),
    destroy=extend_schema(tags=["Patients"]),
    partial_update=extend_schema(tags=["Patients"]),
    get_by_national_id=extend_schema(tags=["Patients"]),
)
class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.PatientSerializer
    queryset = Patient.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)

    @action(
        detail=False, methods=["get"], url_path="by-national_id/(?P<national_id>\d+)"
    )
    def get_by_national_id(self, request, national_id=None):
        try:
            token = request.headers.get("Tamin-Token", None)
            taminClient = TaminClient(token)
            res = taminClient.getPatient(nationalCode=national_id)
            patient = res["data"]["patient"]
            return Response(
                {
                    "first_name": patient["fName"],
                    "last_name": patient["lName"],
                    "sex": "M" if patient["sex"] == "مرد" else "F",
                },
                status=status.HTTP_200_OK,
            )
        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except PatientNotFound as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)


@extend_schema_view(
    list=extend_schema(tags=["Patients"]),
    retrieve=extend_schema(tags=["Patients"]),
)
class PatientSearchViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    serializer_class = serializers.PatientSearchSerializer
    queryset = Patient.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get("search", None)

        if query:
            if query.isdigit():
                queryset = queryset.filter(
                    Q(national_id__startswith=query)
                    | Q(id__startswith=query)
                    | Q(phone_number__startswith=query)
                )[:30]
            else:
                queryset = queryset.annotate(
                    full_name=Concat("first_name", Value(" "), "last_name")
                ).filter(Q(full_name__icontains=query))[:30]

        return queryset


@extend_schema_view(
    retrieve=extend_schema(tags=["Patients"]),
)
class PatientVisitDetailRetrieveView(
    viewsets.GenericViewSet, mixins.RetrieveModelMixin
):
    queryset = Patient.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]
    serializer_class = serializers.PatientVisitSerializerRequest
