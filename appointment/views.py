from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from patient.models.patient_models import Patient, PreRegisterPatient
from user.permissions import IsSecretary, ReadOnly
from utils.sms import SMSClient
from .models import AppointmentSlot
from .serializers import (
    AppointmentSlotGetSerializer,
    AppointmentSlotPostSerializer,
    CreatePaymentSerializer,
    PaymentInitResponseSerializer,
    PaymentDetailSerializer,
)
from rest_framework.views import APIView
from rest_framework import status, permissions, views
from django.shortcuts import get_object_or_404
from persiantools.jdatetime import JalaliDate
from django.conf import settings
from django.db import transaction
from .models import PaymentTransaction
from django.utils import timezone
import requests
from rest_framework.generics import RetrieveAPIView
from django.shortcuts import redirect
from urllib.parse import urlencode


class AppointmentSlotViewSet(viewsets.ModelViewSet):
    queryset = AppointmentSlot.objects.all()
    serializer_class = AppointmentSlotGetSerializer
    permission_classes = [IsSecretary | ReadOnly]
    # filter_backends = [DjangoFilterBackend]
    filterset_fields = ["date"]

    def get_queryset(self):
        queryset = super().get_queryset()
        date = self.request.query_params.get("date")
        if date:
            queryset = queryset.filter(date=date)
        return queryset

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):  # Bulk creation for MySQL: create one by one
            created_instances = []
            for slot_data in request.data:
                serializer = AppointmentSlotPostSerializer(data=slot_data)
                serializer.is_valid(raise_exception=True)  # Raises error if invalid
                instance = serializer.save(created_by=request.user)
                created_instances.append(instance)
            instances = created_instances
        else:
            serializer = AppointmentSlotPostSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            instances = serializer.save(created_by=request.user)

        return Response(
            AppointmentSlotPostSerializer(instances, many=True).data,
            status=status.HTTP_201_CREATED,
        )

    def get_serializer_class(self):
        if self.action == "partial_update" or self.action == "update":
            return AppointmentSlotPostSerializer
        return super().get_serializer_class()


class ReserveAppointmentSlotView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slot_id):
        """
        Reserve an appointment slot for the authenticated user.
        """
        slot = get_object_or_404(AppointmentSlot, id=slot_id, is_booked=False)
        slot.is_booked = True
        slot.patient = request.user.patient
        slot.save()

        return Response(
            AppointmentSlotGetSerializer(slot).data, status=status.HTTP_200_OK
        )


ZP_REQUEST_URL = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_VERIFY_URL = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_STARTPAY = "https://www.zarinpal.com/pg/StartPay/"


class StartPaymentView(views.APIView):
    """
    POST /api/payments/start/
    body: {slot_id, patient_id, amount}
    """

    permission_classes = [AllowAny]

    def post(self, request):
        ser = CreatePaymentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        slot_id = ser.validated_data["slot_id"]
        patient_id = ser.validated_data["patient_id"]
        is_pre_registered = ser.validated_data["is_pre_registered"]
        amount = settings.BOOKING_FEE

        merchant_id = settings.ZARINPAL_MERCHANT_ID
        is_sandbox = getattr(settings, "ZARINPAL_SANDBOX", False)

        # کال‌بک بک‌اند: بهتره Frontend به این URL هدایت بشه
        callback_url = settings.ZARINPAL_CALLBACK_URL

        # 1) قفل خوش‌رفتاری روی اسلات
        with transaction.atomic():
            slot = AppointmentSlot.objects.select_for_update().get(pk=slot_id)
            if slot.is_booked:
                return Response({"detail": "this slot is reserved"}, status=400)

            patient = (
                Patient.objects.get(pk=patient_id)
                if not is_pre_registered
                else PreRegisterPatient.objects.get(pk=patient_id)
            )

            pay = PaymentTransaction.objects.create(
                slot=slot,
                patient=patient if not is_pre_registered else None,
                pre_registered_patient=patient if is_pre_registered else None,
                amount=amount,
                description=f"Appointment {slot.date} {slot.start_time}-{slot.end_time}",
                is_sandbox=is_sandbox,
            )

        headers = {"Content-Type": "application/json"}
        payload = {
            "merchant_id": merchant_id,
            "amount": amount,
            "callback_url": callback_url,  # زرین‌پال Authority را به این آدرس برمی‌گرداند
            "description": pay.description,
            "metadata": {
                # "email": getattr(patient, "email", None),
                "mobile": getattr(
                    patient,
                    "phone_number" if not is_pre_registered else "mobile_number",
                    None,
                ),
                # می‌تونی custom data هم اضافه کنی
            },
        }

        # اگر سندباکس فعاله، فقط merchant_id باید 36 کاراکتر دلخواه باشه و دامنه‌ها سندباکس‌اند (در کانفیگ)
        # ولی طبق راهنما، برای تست کافیست آدرس‌ها را به sandbox تغییر دهی. (بخش Sandbox) :contentReference[oaicite:2]{index=2}

        r = requests.post(ZP_REQUEST_URL, json=payload, headers=headers, timeout=12)
        # print("req", r.request.body)
        data = r.json()
        # print("data", data)
        # پاسخ v4 معمولاً در data/authority و data/code برمی‌گردد
        # code==100 یعنی موفق
        try:
            code = data["data"]["code"]
        except KeyError:
            # ممکنه در errors باشد
            return Response({"detail": data.get("errors", data)}, status=502)

        if code == 100:
            authority = data["data"]["authority"]
            # ذخیره authority
            PaymentTransaction.objects.filter(pk=pay.pk).update(
                authority=authority, status=PaymentTransaction.Status.PENDING_VERIFY
            )

            start_url = f"{ZP_STARTPAY}{authority}"
            out = {"start_pay_url": start_url, "authority": authority}
            return Response(PaymentInitResponseSerializer(out).data, status=200)
        else:
            # کدهای خطا را می‌تونی با صفحه خطاهای رسمی مپ کنی
            return Response({"detail": data}, status=400)


class VerifyPaymentView(views.APIView):
    """
    GET /api/payments/verify/?Authority=XYZ&Status=OK
    این ویو هم برای رندر صفحه موفق/ناموفق می‌تونه JSON بده و هم
    فرانت‌اندت می‌تونه با Authority بیاد سراغش.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        authority = request.query_params.get("Authority")
        status_q = request.query_params.get("Status")

        if not authority:
            return Response({"detail": "Authority is required"}, status=400)

        try:
            pay = PaymentTransaction.objects.select_related("slot").get(
                authority=authority
            )
        except PaymentTransaction.DoesNotExist:
            return Response({"detail": "Transaction not found"}, status=404)

        if status_q != "OK":
            pay.status = PaymentTransaction.Status.CANCELED
            pay.save(update_fields=["status"])
            return Response({"status": "canceled"}, status=200)

        payload = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": pay.amount,  # باید با مبلغ اولیه یکی باشد (طبق داک) :contentReference[oaicite:3]{index=3}
            "authority": authority,
        }
        headers = {"Content-Type": "application/json"}

        r = requests.post(ZP_VERIFY_URL, json=payload, headers=headers, timeout=12)
        # print("req", r.request.body)
        data = r.json()
        # print("data", data)

        try:
            code = data["data"]["code"]
        except KeyError:
            return Response({"detail": data.get("errors", data)}, status=502)

        if code in (100, 101):  # 100: موفق، 101: پرداخت قبلاً تأیید شده
            ref_id = data["data"]["ref_id"]
            with transaction.atomic():
                # نهایی‌کردن رزرو
                slot = pay.slot
                if not slot.is_booked:
                    slot.is_booked = True
                    if pay.pre_registered_patient:
                        print("hi", pay.pre_registered_patient.first_name)
                        slot.pre_registered_patient = pay.pre_registered_patient
                    else:
                        slot.patient_id = pay.patient_id
                    slot.save(
                        update_fields=["is_booked", "patient", "pre_registered_patient"]
                    )

                pay.status = PaymentTransaction.Status.PAID
                pay.ref_id = ref_id
                pay.verified_at = timezone.now()
                pay.save(update_fields=["status", "ref_id", "verified_at"])

            s = SMSClient()
            jalaliDate = JalaliDate(slot.date)
            s.sendAppointmentBookingAcknowledge(
                phoneNumber=pay.patient.phone_number
                if not pay.pre_registered_patient
                else pay.pre_registered_patient.mobile_number,
                doctor="سید عادل جاهد",
                customerName=pay.patient.full_name()
                if not pay.pre_registered_patient
                else pay.pre_registered_patient.first_name
                + " "
                + pay.pre_registered_patient.last_name,
                date=jalaliDate.isoformat().replace("-", "/"),
                time=f"{slot.start_time.hour}:{slot.start_time.minute}",
            )
            # print(
            #     pay.patient.phone_number,
            #     pay.patient.full_name(),
            #     jalaliDate.isoformat(),
            #     slot.start_time,
            # )
            params = {
                "status": "paid",
                "ref_id": ref_id,
                "tx": pay.id,  # آیدی تراکنش داخلی؛ فرانت می‌تونه باهاش دیتیل رو بگیره
                "authority": authority,  # اگر خواستی به UI بدهی
                "date": slot.date,
                "time": slot.start_time,
            }
            url = f"{settings.FRONTEND_PAYMENT_RESULT_URL}?{urlencode(params)}"
            return redirect(url)
        else:
            # شکست در verify
            pay.status = PaymentTransaction.Status.FAILED
            err_code = (data.get("errors", {}) or {}).get("code") or (
                data.get("data", {}) or {}
            ).get("code")
            err_msg = (data.get("errors", {}) or {}).get("message")

            pay.save(update_fields=["status"])
            params = {
                "status": "failed",
                "tx": pay.id,
                "authority": authority,
            }
            if err_code:
                params["code"] = err_code
            if err_msg:
                params["msg"] = err_msg

            url = f"{settings.FRONTEND_PAYMENT_RESULT_URL}?{urlencode(params)}"
            return redirect(url)


class PaymentDetailView(RetrieveAPIView):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentDetailSerializer
    lookup_field = "id"


class FirstAvailableSlotView(APIView):
    """
    GET /api/appointments/first-available/
    خروجی:
    {
      "is_found": true,
      "date": "2025-02-04"
    }
    """

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        today = timezone.localdate()

        qs = AppointmentSlot.objects.filter(
            is_booked=False,
            date__gte=today,
        ).order_by("date", "start_time")

        slot = qs.first()
        if slot:
            return Response({"is_found": True, "date": slot.date.isoformat()})
        return Response({"is_found": False, "date": None})
