import threading
from rest_framework_simplejwt.authentication import JWTAuthentication

_thread_local = threading.local()


def get_current_database():
    return getattr(_thread_local, "clinic_database", None)


class DatabaseRouterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        auth = JWTAuthentication()
        try:
            # دریافت نام کلینیک از JWT توکن
            token = auth.get_validated_token(
                request.headers.get("Authorization").split(" ")[1]
            )
            clinic_name = token.get("clinic_name", None)
            if clinic_name:
                _thread_local.clinic_database = clinic_name
            else:
                _thread_local.clinic_database = None
        except Exception:
            _thread_local.clinic_database = None

        response = self.get_response(request)
        return response
