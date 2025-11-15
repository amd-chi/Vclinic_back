from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from patient.models.patient_models import Patient
from visit.models.visit_models import Visit
from django.utils.timezone import now
from datetime import timedelta, datetime
from django.db import models
from persiantools.jdatetime import JalaliDate


class VisitCounterView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = []

    def get(self, request):
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        jalali_today = JalaliDate.today()
        start_of_month = jalali_today.replace(day=1).to_gregorian()

        today_count = Visit.objects.filter(date=today).count()
        weekly_count = Visit.objects.filter(date__gte=start_of_week).count()
        monthly_count = Visit.objects.filter(date__gte=start_of_month).count()

        visit_count = {
            "today": today_count,
            "weekly": weekly_count,
            "monthly": monthly_count,
        }

        total_fees = {
            "today": Visit.objects.filter(date=today).aggregate(
                total_fees=models.Sum("fee")
            )["total_fees"]
            or 0,
            "weekly": Visit.objects.filter(date__gte=start_of_week).aggregate(
                total_fees=models.Sum("fee")
            )["total_fees"]
            or 0,
            "monthly": Visit.objects.filter(date__gte=start_of_month).aggregate(
                total_fees=models.Sum("fee")
            )["total_fees"]
            or 0,
        }

        today_obj = datetime.strptime(str(today), "%Y-%m-%d")
        start_of_week_obj = datetime.strptime(str(start_of_week), "%Y-%m-%d")
        start_of_month_obj = datetime.strptime(str(start_of_month), "%Y-%m-%d")

        new_patients = {
            "today": Patient.objects.filter(created_at__gte=today_obj).count(),
            "weekly": Patient.objects.filter(created_at__gte=start_of_week_obj).count(),
            "monthly": Patient.objects.filter(
                created_at__gte=start_of_month_obj
            ).count(),
        }

        return Response(
            {
                "visit_count": visit_count,
                "fees": total_fees,
                "new_patients": new_patients,
            }
        )
