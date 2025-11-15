from django.db.utils import IntegrityError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from insurance.connection.tamin_connection import (
    InvalidTokenError,
    TaminClient,
    TokenError,
)
from other_paraclinic_services import serializers
from . import models
from drf_spectacular.utils import extend_schema, extend_schema_view
from django.shortcuts import get_object_or_404
from django.db.models import Q


@extend_schema_view(
    list=extend_schema(tags=["Other Paraclinic Services"]),
    retrieve=extend_schema(tags=["Other Paraclinic Services"]),
    create=extend_schema(tags=["Other Paraclinic Services"]),
    update=extend_schema(tags=["Other Paraclinic Services"]),
    destroy=extend_schema(tags=["Other Paraclinic Services"]),
    partial_update=extend_schema(tags=["Other Paraclinic Services"]),
)
class OtherMedicalServicesViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.OtherParaclinicServicesSerializer
    queryset = models.OtherParaclinicService.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get("search", None)
        category = self.request.query_params.get("category", None)
        token = self.request.headers.get("Tamin-Token")
        if search_query and category:
            if not token:
                queryset = queryset.filter(
                    Q(name__icontains=search_query, category=category)
                    | Q(code__icontains=search_query, category=category)
                )
            else:
                taminClient = TaminClient(token)
                try:
                    category_model = get_object_or_404(models.Category, pk=category)
                    searchResponse = taminClient.searchOtherParaclinicServices(
                        search_query, category_model.code
                    )
                    items = searchResponse["data"]["list"]

                    # دریافت تمامی tamin_id های موجود در دیتابیس
                    existing_services = models.OtherParaclinicService.objects.filter(
                        tamin_id__in=[item["srvId"] for item in items]
                    )
                    existing_tamin_ids = set(
                        existing_services.values_list("tamin_id", flat=True)
                    )

                    # آماده‌سازی لیست جدید برای اضافه شدن
                    new_services = []
                    for item in items:
                        if item["srvId"] not in existing_tamin_ids:
                            new_services.append(
                                models.OtherParaclinicService(
                                    name=item["srvName"],
                                    is_insured=(
                                        True if item["status"] == "1" else False
                                    ),
                                    code=item["srvCode"],
                                    tamin_json=item,
                                    category=category_model,
                                    tamin_id=item["srvId"],
                                )
                            )
                        else:
                            service = existing_services.get(tamin_id=item["srvId"])
                            service.name = item["srvName"]
                            service.is_insured = (
                                True if item["status"] == "1" else False
                            )
                            service.code = item["srvCode"]
                            service.tamin_json = item
                            service.category = category_model

                    # اگر داده‌های جدیدی برای اضافه کردن وجود داشته باشد، آنها را bulk_create می‌کنیم
                    if new_services:
                        for serv in new_services:
                            try:
                                serv.save()
                            except IntegrityError:
                                pass
                    if existing_services:
                        models.OtherParaclinicService.objects.bulk_update(
                            existing_services,
                            fields=["name", "is_insured", "tamin_json"],
                        )
                    # سپس داده‌های اضافه شده یا آپدیت‌شده را به queryset اضافه می‌کنیم
                    queryset = models.OtherParaclinicService.objects.filter(
                        tamin_id__in=[item["srvId"] for item in items]
                    )
                except TokenError:
                    raise InvalidTokenError()

        return queryset


@extend_schema_view(
    list=extend_schema(tags=["Other Paraclinic Services"]),
    retrieve=extend_schema(tags=["Other Paraclinic Services"]),
    create=extend_schema(tags=["Other Paraclinic Services"]),
    update=extend_schema(tags=["Other Paraclinic Services"]),
    destroy=extend_schema(tags=["Other Paraclinic Services"]),
    partial_update=extend_schema(tags=["Other Paraclinic Services"]),
)
class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CategorySerializer
    queryset = models.Category.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
