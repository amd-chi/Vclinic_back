import time
import requests
from datetime import datetime, timedelta
from rest_framework.exceptions import APIException
from rest_framework import status
from django.conf import settings
# from persiantools.jdatetime import JalaliDate


class DeletePrescriptionError(Exception):
    pass


class InvalidTokenError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Tamin Token is invalid or expired"
    default_code = "invalid_token"


class TokenError(Exception):
    """Custom exception for token errors."""

    pass


class PatientNotFound(Exception):
    pass


class PrescriptionCountExceeded(Exception):
    pass


class PrescriptionNotEditable(Exception):
    pass


class SalamatClient:
    def __init__(self, cookies: str, debug: bool = settings.DEBUG):
        self.debug = debug
        self.baseUrl = "https://eservices.ihio.gov.ir/nrx"
        self.session = requests.Session()
        self.session.verify = False
        self.session.headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
            "Connection": "keep-alive",
            "Content-Length": "1274",
            "Content-Type": "application/json",
            "Cookie": (
                "SRVID-ihioerx=036ca9f2d89ea6b5; "
                "SRVID-sso=8340bae4ed794a29; "
                "JAuthdUser=true; "
                "SRVID-nrx=3c502c7e6d337f3e; "
                "JAuthdUserInfo=d60e0dd6baba28da3e26162432785facd1af6dcbb01dd71ee68b53c0c6fe7294c7a0160747bcffe551ebd33594336a6bd25ae3b45b65d2ee2e7c06d68d49ce1b8a8d9bbfd339a0a68d5de0b675de6df9d09acae5af9bbaabf7c00d166cf516a996e73e2ce39cca0a3e1ddda91fb089ade662a30aaf8609f866bc6038dc0e299309955407391d5bca15fc43935366108fcb6ba30516bcdd443d3ab514cea176c1ebe3e54fb673b60e28452e91e8774230; "
                "ajt=0d29d6f5767bf97222a0cc06ae02c9ae; "
                "nrx-session=0d29d6f5767bf97222a0cc06ae02c9ae; "
                "SRVID-fmp=17d6801d949f6c8b"
            ),
            "Host": "eservices.ihio.gov.ir",
            "Origin": "https://eservices.ihio.gov.ir",
            "Referer": "https://eservices.ihio.gov.ir/nrx/",
            "Sec-Ch-Ua": '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": '"Windows"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
        }

        # self.setOffice()

    def handle_response(self, response: requests.Response):
        """Handle the response, raise errors if needed."""
        if self.debug:
            # response.encoding = "utf-8"
            # print(response.status_code)
            # print(response.request.body)
            # print(response.request.headers)
            # print(response.headers)
            print(response.text)

        if response.status_code == 401:
            raise TokenError("Session has expired.")

        if "application/json" in response.headers.get("Content-Type", ""):
            response_text = response.text.replace("ي", "ی").replace("ك", "ک")
            response._content = response_text.encode("utf-8")
        return response

    def post(self, url, **kwargs):
        response = self.session.post(url, **kwargs, verify=False)
        # print(response.text)

        return self.handle_response(response)

    def getPatient(self, nationalId: str):
        # https://eservices.ihio.gov.ir/nrx/v1/services/session/citizen/open
        response = self.post(
            f"{self.baseUrl}/v1/services/session/citizen/open",
            json={
                "nationalNumber": nationalId,
            },
        )
        return response.json()
