from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django.db.models import Q
from insurance.connection.tamin_connection import (
    InvalidTokenError,
    TaminClient,
    TokenError,
)
from medicines.models import Medicine
from . import serializers
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.db.utils import IntegrityError


@extend_schema_view(
    list=extend_schema(tags=["Medicines"]),
    retrieve=extend_schema(tags=["Medicines"]),
    create=extend_schema(tags=["Medicines"]),
    update=extend_schema(tags=["Medicines"]),
    destroy=extend_schema(tags=["Medicines"]),
    partial_update=extend_schema(tags=["Medicines"]),
)
class MedicineViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.MedicineSerializer
    queryset = Medicine.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", None)
        if search_query:
            is_custom = self.request.query_params.get("is_custom", None) == "true"
            token = self.request.headers.get("Tamin-Token")
            if not token:
                if is_custom:
                    queryset = queryset.filter(
                        (
                            Q(name__icontains=search_query)
                            | Q(code__icontains=search_query)
                        )
                        & Q(tamin_json__isnull=True)
                    )[:50]
                else:
                    queryset = queryset.filter(
                        (
                            Q(name__icontains=search_query)
                            | Q(code__icontains=search_query)
                        )
                        & Q(tamin_json__isnull=False)
                    )[:50]
            else:
                if not is_custom:
                    taminClient = TaminClient(token)
                    try:
                        tamin_medicines_response = taminClient.searchMedicines(
                            search_query, limit=70
                        )
                        tamin_medicines = tamin_medicines_response["data"]["list"]

                        available_in_db_medicines = Medicine.objects.filter(
                            tamin_id__in=[
                                tamin_medicine["srvId"]
                                for tamin_medicine in tamin_medicines
                            ]
                        )
                        available_in_db_srv_ids = set(
                            available_in_db_medicines.values_list("tamin_id", flat=True)
                        )
                        # Medicine.objects.bulk_update()
                        # آماده‌سازی لیست جدید برای اضافه شدن
                        new_medicines: list[Medicine] = []
                        for tamin_medicine in tamin_medicines:
                            if tamin_medicine["srvId"] not in available_in_db_srv_ids:
                                new_medicines.append(
                                    Medicine(
                                        name=tamin_medicine["srvName"],
                                        tamin_id=tamin_medicine["srvId"],
                                        code=tamin_medicine["srvCode"],
                                        is_insured=True
                                        if tamin_medicine["status"] == "1"
                                        else False,
                                        category=(
                                            tamin_medicine["formCode"]["formDes"]
                                            if tamin_medicine["formCode"]
                                            else "None"
                                        ),
                                        tamin_json=tamin_medicine,
                                    )
                                )
                            else:
                                # update the medicine
                                medicine = available_in_db_medicines.get(
                                    tamin_id=tamin_medicine["srvId"]
                                )
                                medicine.name = tamin_medicine["srvName"]
                                medicine.code = tamin_medicine["srvCode"]
                                medicine.is_insured = (
                                    True if tamin_medicine["status"] == "1" else False
                                )
                                medicine.category = (
                                    tamin_medicine["formCode"]["formDes"]
                                    if tamin_medicine["formCode"]
                                    else "None"
                                )
                                medicine.tamin_json = tamin_medicine

                        # اگر داده جدید وجود داشته باشد، آنها را bulk_create می‌کنیم
                        if new_medicines:
                            for medicine in new_medicines:
                                try:
                                    medicine.save()
                                except IntegrityError:
                                    pass
                        # اگر داده‌های قبلی وجود داشته باشد، آنها را bulk_update می‌کنیم
                        if available_in_db_medicines:
                            Medicine.objects.bulk_update(
                                available_in_db_medicines,
                                fields=[
                                    "name",
                                    "is_insured",
                                    "category",
                                    "tamin_json",
                                    "code",
                                ],
                            )
                        # سپس داده‌های جدید را بازیابی کرده و در queryset ذخیره می‌کنیم
                        queryset = Medicine.objects.filter(
                            tamin_id__in=[item["srvId"] for item in tamin_medicines]
                        )
                    except TokenError:
                        raise InvalidTokenError()
                else:
                    queryset = queryset.filter(
                        (
                            Q(name__icontains=search_query)
                            | Q(code__icontains=search_query)
                        )
                        & Q(tamin_json__isnull=True)
                    )[:50]
        return queryset
