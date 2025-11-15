from django.conf import settings
from farapayamak import Rest_Client
from rest_framework.response import Response
from rest_framework import status


class SMSClient:
    def __init__(self):
        self.restClient = Rest_Client(
            username=settings.SMS_USERNAME, password=settings.SMS_PASSWORD
        )

    # def sendSMS(self, phone_number: str, message: str):
    #     self.rest_client.SendSMS(phone_number, message)

    def sendOtpCode(self, otpCode: str, phoneNumber: str):
        try:
            self.restClient.BaseServiceNumber(
                text=otpCode, bodyId=223807, to=phoneNumber
            )
        except Exception:
            return Response(
                {"detail": "SMS sending problem in server"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def sendAppointmentBookingAcknowledge(
        self, phoneNumber: str, doctor: str, customerName: str, time: str, date: str
    ):
        try:
            self.restClient.BaseServiceNumber(
                text=f"{customerName};دکتر {doctor} در تاریخ {date} ساعت {time}",
                bodyId=373521,
                to=phoneNumber,
            )
        except Exception:
            from rest_framework.response import Response
            from rest_framework import status

            return Response(
                {"detail": "SMS sending problem in server"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
