from rest_framework.viewsets import ModelViewSet

from user.permissions import IsSecretary
from insurance.connection.tamin_connection import (
    DeletePrescriptionError,
    PrescriptionCountExceeded,
    PrescriptionNotEditable,
    TaminClient,
    TokenError,
    PatientNotFound,
)
from visit import serializers

# from rest_framework.decorators import action
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status

from visit.models import MedicalTestPrescriptionGroup, MedicalTestPrescriptionItem
from visit.models.medical_test_models import MedicalTestFavoriteGroup
from visit.serializers.test_prescription_serializers import (
    MedicalTestFavoriteGroupCreateUpdateSerializer,
    MedicalTestFavoriteGroupReadSerializer,
)
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(tags=["Visit - Test"]),
    retrieve=extend_schema(tags=["Visit - Test"]),
    create=extend_schema(tags=["Visit - Test"]),
    update=extend_schema(tags=["Visit - Test"]),
    destroy=extend_schema(tags=["Visit - Test"]),
    partial_update=extend_schema(tags=["Visit - Test"]),
)
class MedicalTestPrescriptionViewSet(ModelViewSet):
    serializer_class = serializers.MedicalTestGroupSerializer
    queryset = MedicalTestPrescriptionGroup.objects.all()
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
            return serializers.MedicalTestCreateUpdateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # get values from serializer
        patient = serializer.validated_data["patient"]
        comment = serializer.validated_data["comment"]
        use_insurance = serializer.validated_data["use_insurance"]
        prescribed_tests = serializer.validated_data["presc_items"]
        token = request.headers.get("Tamin-Token")
        tamin_tracking_code = None
        tamin_id = None
        if not prescribed_tests:
            return Response(
                {"error": "Prescription items are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # prescription items available
        if use_insurance:
            # use insurance
            if not token:
                return Response(
                    {"error": "Tamin Token is required for insurance usage"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            taminClient = TaminClient(token)
            tamin_tests = []  # drugs that are capable of being prescribed with tamin

            from persiantools.jdatetime import JalaliDate

            for prescription_item in prescribed_tests:
                test = prescription_item["test"]

                if test.tamin_json:
                    # can be prescribed with tamin
                    # get drug instructions and amount json objects for insurance
                    jalali_date = JalaliDate(prescription_item["date"])
                    # year/month/day
                    formatted_date = (
                        f"{jalali_date.year}{jalali_date.month:02}{jalali_date.day:02}"
                    )

                    test_obj = test.tamin_json
                    aggregated_test_obj = {
                        "date": formatted_date,
                        **test_obj,
                    }
                    tamin_tests.append(aggregated_test_obj)
            if len(tamin_tests) > 0:
                try:
                    response = taminClient.prescribeTest(
                        nationalCode=patient.national_id,
                        comment=comment,
                        tests=tamin_tests,
                    )
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
                except PrescriptionCountExceeded:
                    return Response(
                        {"error": "Test prescription exceeded"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                tamin_tracking_code = response["data"]["noteHead"]["trackingCode"]
                tamin_id = str(response["data"]["headId"])

        group = MedicalTestPrescriptionGroup.objects.create(
            patient=patient,
            comment=comment,
            tamin_tracking_code=tamin_tracking_code,
            tamin_id=tamin_id,
            created_by=request.user,
        )

        Test_prescription_items = [
            MedicalTestPrescriptionItem(group=group, **prescription_item)
            for prescription_item in prescribed_tests
        ]

        MedicalTestPrescriptionItem.objects.bulk_create(Test_prescription_items)

        return Response(
            {
                "id": group.id,
                "tamin_test_tracking_code": tamin_tracking_code,
            },
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        if self.get_object().tamin_id:
            token = request.headers.get("Tamin_Token")
            if not token:
                return Response(
                    {"error": "Tamin Token is required for insurance usage"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            taminClient = TaminClient(token)
            try:
                taminClient.deletePrescription(self.get_object().tamin_id)
            except TokenError:
                return Response(
                    {"error": "Tamin Token is invalid or expired"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except DeletePrescriptionError:
                return Response(
                    {"error": "Prescription Not Deletable"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # get values from serializer
        comment = serializer.validated_data["comment"]
        token = request.headers.get("Tamin_Token")
        presc_items = serializer.validated_data["presc_items"]
        patient = self.get_object().patient
        currentPresc = self.get_object()
        if self.get_object().tamin_id:
            token = request.headers.get("Tamin_Token")
            if not token:
                return Response(
                    {"error": "Tamin Token is required for insurance usage"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            taminClient = TaminClient(token)
            tamin_prescs = []  # tests that are capable of being prescribed with tamin

            from persiantools.jdatetime import JalaliDate

            for prescription_item in presc_items:
                test = prescription_item["test"]

                if test.tamin_json:
                    # can be prescribed with tamin
                    # get drug instructions and amount json objects for insurance
                    jalali_date = JalaliDate(prescription_item["date"])
                    # year/month/day
                    formatted_date = (
                        f"{jalali_date.year}{jalali_date.month:02}{jalali_date.day:02}"
                    )

                    test_obj = test.tamin_json
                    aggregated_imaging_obj = {
                        "date": formatted_date,
                        **test_obj,
                    }
                    tamin_prescs.append(aggregated_imaging_obj)
            if len(tamin_prescs) > 0:
                try:
                    taminClient.editMedicalTestPrescription(
                        nationalCode=patient.national_id,
                        code=currentPresc.tamin_id,
                        comment=comment,
                        tests=tamin_prescs,
                    )
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
                except PrescriptionNotEditable:
                    return Response(
                        {"error": "Prescription Not Editable"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        # do the update in db
        instance = self.get_object()
        instance.comment = comment

        instance.save()
        # delete all previous results
        instance.presc_items.all().delete()
        for item in presc_items:
            MedicalTestPrescriptionItem.objects.create(group=instance, **item)
        return Response(
            {
                "id": instance.id,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(tags=["Visit - Test"]),
    retrieve=extend_schema(tags=["Visit - Test"]),
    create=extend_schema(tags=["Visit - Test"]),
    update=extend_schema(tags=["Visit - Test"]),
    destroy=extend_schema(tags=["Visit - Test"]),
    partial_update=extend_schema(tags=["Visit - Test"]),
)
class MedicalTestFavoritesViewSets(ModelViewSet):
    serializer_class = MedicalTestFavoriteGroupReadSerializer
    queryset = MedicalTestFavoriteGroup.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return MedicalTestFavoriteGroupCreateUpdateSerializer
        return super().get_serializer_class()
