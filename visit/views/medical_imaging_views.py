from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

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

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status

from visit.models import MedicalImagingPrescriptionGroup, MedicalImagingPrescriptionItem
from visit.models.medical_imaging_models import MedicalImagingFavoriteGroup
from visit.serializers.imaging_prescription_serializers import (
    MedicalImagingFavoriteGroupCreateUpdateSerializer,
    MedicalImagingFavoriteGroupReadSerializer,
)
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(tags=["Visit - Medical Imaging"]),
    retrieve=extend_schema(tags=["Visit - Medical Imaging"]),
    create=extend_schema(tags=["Visit - Medical Imaging"]),
    update=extend_schema(tags=["Visit - Medical Imaging"]),
    destroy=extend_schema(tags=["Visit - Medical Imaging"]),
    partial_update=extend_schema(tags=["Visit - Medical Imaging"]),
    get_last_prescription=extend_schema(tags=["Visit - Medical Imaging"]),
)
class MedicalImagingPrescriptionViewSet(ModelViewSet):
    serializer_class = serializers.MedicalImagingGroupReadSerializer
    queryset = MedicalImagingPrescriptionGroup.objects.all()
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
            return serializers.MedicalImagingCreateUpdateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["get"], url_path="last-prescription")
    def get_last_prescription(self, request):
        last_prescription = self.get_queryset().order_by("-date").first()
        if last_prescription:
            serializer = self.get_serializer(last_prescription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # get values from serializer
        patient = serializer.validated_data["patient"]
        comment = serializer.validated_data["comment"]
        use_insurance = serializer.validated_data["use_insurance"]
        prescribed_imagings = serializer.validated_data["presc_items"]
        token = request.headers.get("Tamin-Token")
        tamin_imaging_tracking_code = None
        tamin_id = None
        if not prescribed_imagings:
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
            tamin_prescs = []  # imagings that are capable of being prescribed with tamin

            from persiantools.jdatetime import JalaliDate

            for prescription_item in prescribed_imagings:
                imaging = prescription_item["imaging"]

                if imaging.tamin_json:
                    # can be prescribed with tamin
                    # get drug instructions and amount json objects for insurance
                    jalali_date = JalaliDate(prescription_item["date"])
                    # year/month/day
                    formatted_date = (
                        f"{jalali_date.year}{jalali_date.month:02}{jalali_date.day:02}"
                    )

                    imaging_obj = imaging.tamin_json
                    aggregated_imaging_obj = {
                        "date": formatted_date,
                        **imaging_obj,
                    }
                    tamin_prescs.append(aggregated_imaging_obj)
            if len(tamin_prescs) > 0:
                try:
                    response = taminClient.prescribeImaging(
                        nationalCode=patient.national_id,
                        comment=comment,
                        prescs=tamin_prescs,
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
                        {"error": "Medicine prescription exceeded"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                tamin_imaging_tracking_code = response["data"]["noteHead"][
                    "trackingCode"
                ]
                tamin_id = str(response["data"]["headId"])

        group = MedicalImagingPrescriptionGroup.objects.create(
            patient=patient,
            comment=comment,
            tamin_tracking_code=tamin_imaging_tracking_code,
            tamin_id=tamin_id,
            created_by=request.user,
        )

        medicine_prescription_items = [
            MedicalImagingPrescriptionItem(group=group, **prescription_item)
            for prescription_item in prescribed_imagings
        ]

        MedicalImagingPrescriptionItem.objects.bulk_create(medicine_prescription_items)

        return Response(
            {
                "id": group.id,
                "tamin_imaging_tracking_code": tamin_imaging_tracking_code,
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
            tamin_prescs = []  # imagings that are capable of being prescribed with tamin

            from persiantools.jdatetime import JalaliDate

            for prescription_item in presc_items:
                imaging = prescription_item["imaging"]

                if imaging.tamin_json:
                    # can be prescribed with tamin
                    # get drug instructions and amount json objects for insurance
                    jalali_date = JalaliDate(prescription_item["date"])
                    # year/month/day
                    formatted_date = (
                        f"{jalali_date.year}{jalali_date.month:02}{jalali_date.day:02}"
                    )

                    imaging_obj = imaging.tamin_json
                    aggregated_imaging_obj = {
                        "date": formatted_date,
                        **imaging_obj,
                    }
                    tamin_prescs.append(aggregated_imaging_obj)
            if len(tamin_prescs) > 0:
                try:
                    taminClient.editPrescriptionImaging(
                        nationalCode=patient.national_id,
                        editCode=currentPresc.tamin_id,
                        comment=comment,
                        prescs=tamin_prescs,
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
            MedicalImagingPrescriptionItem.objects.create(group=instance, **item)
        return Response(
            {
                "id": instance.id,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(tags=["Visit - Medical Imaging"]),
    retrieve=extend_schema(tags=["Visit - Medical Imaging"]),
    create=extend_schema(tags=["Visit - Medical Imaging"]),
    update=extend_schema(tags=["Visit - Medical Imaging"]),
    destroy=extend_schema(tags=["Visit - Medical Imaging"]),
    partial_update=extend_schema(tags=["Visit - Medical Imaging"]),
)
class MedicalImagingFavoritesViewSets(ModelViewSet):
    serializer_class = MedicalImagingFavoriteGroupReadSerializer
    queryset = MedicalImagingFavoriteGroup.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return MedicalImagingFavoriteGroupCreateUpdateSerializer
        return super().get_serializer_class()
