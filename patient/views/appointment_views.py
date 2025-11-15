from datetime import datetime, time
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from patient import serializers
from patient.models import Appointment
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view


@extend_schema_view(
    list=extend_schema(tags=["Appointment"]),
    retrieve=extend_schema(tags=["Appointment"]),
    create=extend_schema(tags=["Appointment"]),
    update=extend_schema(tags=["Appointment"]),
    destroy=extend_schema(tags=["Appointment"]),
    partial_update=extend_schema(tags=["Appointment"]),
)
class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AppointmentCreateUpdateDestroySerializer
    queryset = Appointment.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list" or self.action == "retrieve":
            return serializers.AppointmentListRetrieveSerializer
        return self.serializer_class

    def list(self, request):
        date_str = request.query_params.get("date", None)
        if date_str:
            try:
                specifiedDate = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()
                today_min = datetime.combine(specifiedDate, time.min)
                today_max = datetime.combine(specifiedDate, time.max)
                queryset = Appointment.objects.filter(
                    datetime__range=(today_min, today_max)
                )
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data)
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Please use YYYY-MM-DD."}, status=400
                )
        else:
            return super().list(request)

    def perform_create(self, serializer):
        return serializer.save(created_by=self.request.user)
