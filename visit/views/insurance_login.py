from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication

# from rest_framework.permissions import IsAuthenticated
from insurance.connection.tamin_connection import TaminClient, TokenError
from user.permissions import IsSecretary
from insurance.connection.tamin_login import (
    PasscodeIncorrect,
    TaminLogin,
    UnexpectedProblem,
    UsernamePasswordIncorrect,
)
from drf_spectacular.utils import extend_schema


# login_manager = LoginManager()
# taminLogin = TaminLogin()


# @extend_schema(tags=["Visit - Tamin Login"])
@extend_schema(
    tags=["Visit - Tamin Login"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
            "required": ["username", "password"],
        }
    },
)
class Phase1APIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # thread = login_manager.create_thread()
            # thread.login_phase1(username, password)
            token = TaminLogin.get_instance().login_phase1(username, password)
            message = "Token is ready" if token else "Otp sent successfully"
            if token:
                taminClient = TaminClient(token)
                user = taminClient.getCurrentUser()["data"]
                first_name = user["firstName"]
                last_name = user["lastName"]
                gender = user["gender"]
                spec = user["docSpec"]["specDesc"]
                doc_id = user["docId"]

            return Response(
                {
                    "message": message,
                    "token": token,
                    "doctor": {
                        "first_name": first_name,
                        "last_name": last_name,
                        "gender": gender,
                        "speciality": spec,
                        "doc_id": doc_id,
                    },
                    "id": "1",
                },
                status=201,
            )
        except UsernamePasswordIncorrect:
            return Response(
                {"error": "Username or password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except UnexpectedProblem as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@extend_schema(
    tags=["Visit - Tamin Login"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "thread_id": {"type": "string"},
                "passcode": {"type": "string"},
            },
            "required": ["thread_id", "passcode"],
        }
    },
)
class Phase2APIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def post(self, request):
        thread_id = request.data.get("thread_id")
        passcode = request.data.get("passcode")

        if not thread_id or not passcode:
            return Response(
                {"error": "Thread ID and passcode are required"}, status=400
            )

        # پیدا کردن ترد بر اساس thread_id
        # thread = login_manager.get_thread(thread_id)
        # if not thread:
        #     return Response({"error": "Thread not found"}, status=404)

        # # اجرای فاز دوم
        try:
            #     token = thread.login_phase2(passcode)
            token = TaminLogin.get_instance().login_phase2(passcode)

        except PasscodeIncorrect:
            return Response({"error": "Passcode Incorrect"}, status=400)
        except UnexpectedProblem as e:
            return Response({"error": str(e)}, status=500)

        # پاک کردن ترد از دیکشنری
        # login_manager.stop_thread(thread_id)
        taminClient = TaminClient(token)
        user = taminClient.getCurrentUser()["data"]
        first_name = user["firstName"]
        last_name = user["lastName"]
        gender = user["gender"]
        spec = user["docSpec"]["specDesc"]
        doc_id = user["docId"]

        return Response(
            {
                "message": "login_phase2 completed",
                "token": token,
                "doctor": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "speciality": spec,
                    "doc_id": doc_id,
                },
            },
            status=200,
        )


@extend_schema(
    tags=["Visit - Tamin Login"],
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
            },
            "required": ["token"],
        }
    },
)
class CheckTaminTokenApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsSecretary]

    def post(self, request):
        token = request.data.get("token")
        client = TaminClient(token)
        try:
            user = client.getCurrentUser()["data"]
            first_name = user["firstName"]
            last_name = user["lastName"]
            gender = user["gender"]
            spec = user["docSpec"]["specDesc"]
            doc_id = user["docId"]

            return Response(
                {
                    "first_name": first_name,
                    "last_name": last_name,
                    "gender": gender,
                    "speciality": spec,
                    "doc_id": doc_id,
                },
                status=200,
            )
        except TokenError:
            return Response({"error": "Tamin Token is invalid or expired"}, status=400)
