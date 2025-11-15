from datetime import timedelta, datetime
from rest_framework.generics import mixins
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from medicines.models import Medicine
from patient.models.patient_models import Patient
from user.permissions import IsSecretary
from insurance.connection.tamin_connection import (
    DeletePrescriptionError,
    PrescriptionCountExceeded,
    TaminClient,
    TokenError,
    PatientNotFound,
    PrescriptionNotEditable,
)
from visit import serializers
from visit.models.medicine_models import MedicineFavoriteGroup, MedicineRepeat
from visit.serializers.medicine_prescription_serializers import (
    MedicineFavoriteGroupCreateUpdateSerializer,
    MedicineFavoriteGroupReadSerializer,
    MedicineRepeatSerializer,
)

from ..models import (
    MedicineAmount,
    MedicineInstruction,
    MedicinePrescriptionGroup,
    MedicinePrescriptionItem,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from persiantools.jdatetime import JalaliDate

from django.db import transaction


@extend_schema_view(
    list=extend_schema(tags=["Visit - Medicine"]),
    retrieve=extend_schema(tags=["Visit - Medicine"]),
)
class MedicineAmountsViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = serializers.MedicineAmountSerializer
    queryset = MedicineAmount.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["Visit - Medicine"]),
    retrieve=extend_schema(tags=["Visit - Medicine"]),
)
class MedicineInstructionsViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = serializers.MedicineInstructionSerializer
    queryset = MedicineInstruction.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["Visit - Medicine"]),
    retrieve=extend_schema(tags=["Visit - Medicine"]),
)
class MedicineRepeatViewSet(
    GenericViewSet,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
    serializer_class = MedicineRepeatSerializer
    queryset = MedicineRepeat.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=["Visit - Medicine"]),
    retrieve=extend_schema(tags=["Visit - Medicine"]),
    create=extend_schema(tags=["Visit - Medicine"]),
    update=extend_schema(tags=["Visit - Medicine"]),
    destroy=extend_schema(tags=["Visit - Medicine"]),
    partial_update=extend_schema(tags=["Visit - Medicine"]),
    get_last_prescription=extend_schema(tags=["Visit - Medicine"]),
    update_last_tamin_prescriptions=extend_schema(
        tags=["Visit - Medicine"],
        parameters=[
            OpenApiParameter(
                name="patient_id",
                type=int,
                location=OpenApiParameter.QUERY,
                required=True,
                description="ID of the patient",
            )
        ],
    ),
)
class MedicinePrescriptionViewSet(ModelViewSet):
    serializer_class = serializers.MedicinePrescriptionGroupSerializer
    queryset = MedicinePrescriptionGroup.objects.all()
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
            return serializers.MedicinePrescriptionGroupCreateUpdateSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=["get"], url_path="last-prescription")
    def get_last_prescription(self, request):
        last_prescription = self.get_queryset().order_by("-date").first()
        if last_prescription:
            serializer = self.get_serializer(last_prescription)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"error": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=["post"], url_path="update-prescriptions-tamin")
    def update_last_tamin_prescriptions(self, request):
        token = request.headers.get("Tamin_Token")
        patient_id = request.query_params.get("patient")
        patient = Patient.objects.get(id=patient_id)
        if not token:
            return Response(
                {"error": "Tamin Token is required for insurance usage"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        taminClient = TaminClient(token)
        try:
            year_jalali = JalaliDate.today().year
            doctor_id = taminClient.getCurrentUser()["data"]["docId"]
            for year in [
                year_jalali,
                year_jalali - 1,
                year_jalali - 2,
            ]:
                response = taminClient.getLastYearPrescriptions(
                    patient.national_id, year
                )
                with transaction.atomic():
                    if response["data"].get("list") is None:
                        continue
                    for group in response["data"]["list"]:
                        group_id = group["noteHeadEprscId"]
                        if MedicinePrescriptionGroup.objects.filter(
                            tamin_id=group_id
                        ).exists():
                            continue
                        elif group["docId"] != doctor_id:
                            # if the doctor id is not equal to the current doctor id, skip this group
                            continue
                        comment = group["comments"]
                        date_raw_jalali: str = group["prescDate"]
                        # اگر طول رشته کمتر از 8 باشد، صفرها را به ابتدای رشته اضافه می‌کنیم
                        if "/" in date_raw_jalali:
                            year, month, day = date_raw_jalali.split("/")
                            date_raw_jalali = f"{year}{month.zfill(2)}{day.zfill(2)}"

                        date_raw = date_raw_jalali.zfill(8)
                        # تبدیل به فرمت YYYY/MM/DD
                        formatted_date = (
                            f"{date_raw[:4]}-{date_raw[4:6]}-{date_raw[6:]}"
                        )

                        date_iso_gregorian = (
                            JalaliDate.fromisoformat(formatted_date)
                            .to_gregorian()
                            .isoformat()
                        )
                        group_res = taminClient.getPrecriptionGroup(
                            group_id, patient.national_id
                        )
                        items = group_res.get("data").get("list")
                        group_model = MedicinePrescriptionGroup.objects.create(
                            patient=patient,
                            comment=comment,
                            tamin_id=group_id,
                            tamin_tracking_code="بدون کد",
                        )
                        group_model.save()
                        group_model.date = date_iso_gregorian
                        group_model.save()
                        for item in items:
                            item_model = MedicinePrescriptionItem()
                            item_model.group = group_model

                            medicine_tamin_id = item["srvId"]["srvId"]
                            try:
                                medicine = Medicine.objects.get(
                                    tamin_id=medicine_tamin_id
                                )
                            except Medicine.DoesNotExist:
                                medicine = Medicine()
                                medicine.is_insured = (
                                    True if item["srvId"]["status"] == "1" else False
                                )
                                medicine.tamin_id = medicine_tamin_id
                                medicine.code = item["srvId"]["srvCode"]
                                medicine.name = item["srvId"]["srvName"]
                                medicine.category = (
                                    item["srvId"]["formCode"]["formDes"]
                                    if item["srvId"]["formCode"]
                                    else "None"
                                )
                                medicine.save()
                            item_model.medicine = medicine
                            amount_id = item["timesAday"]["drugAmntId"]
                            try:
                                item_model.amount = MedicineAmount.objects.get(
                                    tamin_json__drugAmntId=amount_id
                                )
                            except MedicineAmount.DoesNotExist:
                                item_model.amount = MedicineAmount.objects.get(
                                    tamin_json__drugAmntId=170
                                )
                            instruction_id = item["drugInstruction"]["drugInstId"]
                            try:
                                item_model.instruction = (
                                    MedicineInstruction.objects.get(
                                        tamin_json__drugInstId=instruction_id
                                    )
                                )
                            except MedicineInstruction.DoesNotExist:
                                item_model.instruction = (
                                    MedicineInstruction.objects.get(
                                        tamin_json__drugInstId=77
                                    )
                                )
                            item_model.quantity = item["srvQty"]  # ok

                            item_model.repeat = None  # ok

                            item_model.repeat_count = item["repeat"]  # ok

                            item_model.doDate = None

                            item_model.save()

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
        return Response(response["data"], status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # get values from serializer
        patient = serializer.validated_data["patient"]
        comment = serializer.validated_data["comment"]
        token = request.headers.get("Tamin_Token")
        prescribed_medicines = serializer.validated_data["presc_items"]
        use_insurance = serializer.validated_data["use_insurance"]
        tamin_tracking_code = None
        tamin_id = None
        if not prescribed_medicines:
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
            tamin_drugs = []  # drugs that are capable of being prescribed with tamin

            for prescription_item in prescribed_medicines:
                medicine = prescription_item["medicine"]

                if medicine.tamin_json and not prescription_item.get("is_note", False):
                    # can be prescribed with tamin
                    # get drug instructions and amount json objects for insurance
                    instruction_json = prescription_item.get("instruction").tamin_json
                    amount_json = prescription_item.get("amount").tamin_json
                    drug_obj = medicine.tamin_json
                    repeat_obj = prescription_item.get("repeat")
                    datedo = ""
                    if repeat_obj:
                        days_delta = int(repeat_obj.tamin_json["repeatDaysCode"])
                        # create the date from today until days_delta
                        date_gregorian = datetime.now() + timedelta(days=days_delta)
                        jalali_date = JalaliDate(date_gregorian)
                        # year/month/day
                        datedo = f"{jalali_date.year}{jalali_date.month:02}{jalali_date.day:02}"
                    elif prescription_item.get("doDate"):
                        date_gregorian = prescription_item.get("doDate")
                        jalali_date = JalaliDate(date_gregorian)
                        # year/month/day
                        datedo = f"{jalali_date.year}{jalali_date.month:02}{jalali_date.day:02}"

                    aggregated_drug_obj = {
                        "drugAmount": amount_json,
                        "drugInstruction": instruction_json,
                        "quantity": prescription_item["quantity"],
                        "repeat": prescription_item.get("repeat_count", None),
                        "datedo": datedo,
                        **drug_obj,
                    }
                    tamin_drugs.append(aggregated_drug_obj)
            if len(tamin_drugs) > 0:
                try:
                    response = taminClient.prescribeMedicine(
                        nationalCode=patient.national_id,
                        medicines=tamin_drugs,
                        comment=comment,
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
                tamin_tracking_code = response["data"]["noteHead"]["trackingCode"]
                tamin_id = str(response["data"]["headId"])

        group = MedicinePrescriptionGroup.objects.create(
            patient=patient,
            comment=comment,
            tamin_tracking_code=tamin_tracking_code,
            tamin_id=tamin_id,
            created_by=request.user,
        )

        medicine_prescription_items = [
            MedicinePrescriptionItem(group=group, **prescription_item)
            for prescription_item in prescribed_medicines
        ]

        MedicinePrescriptionItem.objects.bulk_create(medicine_prescription_items)

        return Response(
            {
                "id": group.id,
                "tamin_medicine_tracking_code": tamin_tracking_code,
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

        if self.get_object().tamin_id:
            token = request.headers.get("Tamin_Token")
            if not token:
                return Response(
                    {"error": "Tamin Token is required for insurance usage"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            taminClient = TaminClient(token)
            tamin_drugs = []  # drugs that are capable of being prescribed with tamin

            for prescription_item in presc_items:
                medicine = prescription_item["medicine"]

                if medicine.tamin_json and not prescription_item.get("is_note", False):
                    # can be prescribed with tamin
                    # get drug instructions and amount json objects for insurance
                    instruction_json = prescription_item.get("instruction").tamin_json
                    amount_json = prescription_item.get("amount").tamin_json
                    drug_obj = medicine.tamin_json
                    repeat_obj = prescription_item.get("repeat")
                    datedo = ""
                    if repeat_obj:
                        days_delta = int(repeat_obj.tamin_json["repeatDaysCode"])
                        # create the date from today until days_delta
                        date_gregorian = datetime.now() + timedelta(days=days_delta)
                        jalali_date = JalaliDate(date_gregorian)
                        # year/month/day
                        datedo = f"{jalali_date.year}{jalali_date.month:02}{jalali_date.day:02}"
                    elif prescription_item.get("doDate"):
                        date_gregorian = prescription_item.get("doDate")
                        jalali_date = JalaliDate(date_gregorian)
                        # year/month/day
                        datedo = f"{jalali_date.year}{jalali_date.month:02}{jalali_date.day:02}"

                    aggregated_drug_obj = {
                        "drugAmount": amount_json,
                        "drugInstruction": instruction_json,
                        "quantity": prescription_item["quantity"],
                        "repeat": prescription_item.get("repeat_count", None),
                        "datedo": datedo,
                        **drug_obj,
                    }
                    tamin_drugs.append(aggregated_drug_obj)

            if len(tamin_drugs) > 0:
                try:
                    taminClient.editMedicinePrescription(
                        nationalCode=patient.national_id,
                        code=self.get_object().tamin_id,
                        medicines=tamin_drugs,
                        comment=comment,
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
            MedicinePrescriptionItem.objects.create(group=instance, **item)
        return Response(
            {
                "id": instance.id,
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=extend_schema(tags=["Visit - Medicine"]),
    retrieve=extend_schema(tags=["Visit - Medicine"]),
    create=extend_schema(tags=["Visit - Medicine"]),
    update=extend_schema(tags=["Visit - Medicine"]),
    destroy=extend_schema(tags=["Visit - Medicine"]),
    partial_update=extend_schema(tags=["Visit - Medicine"]),
)
class MedicineFavoritesViewSets(ModelViewSet):
    serializer_class = MedicineFavoriteGroupReadSerializer
    queryset = MedicineFavoriteGroup.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return MedicineFavoriteGroupCreateUpdateSerializer
        return super().get_serializer_class()
