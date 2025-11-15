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


class TaminClient:
    def __init__(self, token: str, debug: bool = settings.DEBUG):
        self.debug = debug
        self.baseUrl = "https://ep.tamin.ir/api"
        self.session = requests.Session()
        self.session.headers = {
            "Accept": "application/json, text/plain",
            "Accept-Encoding": "gzip, deflate, zstd",
            "Accept-Language": "en-US,en-GB;q=0.9,en;q=0.8",
            "Authorization": f"Bearer {token}",
            "Connection": "keep-alive",
            "priority": "u=1, i",
            "Host": "ep.tamin.ir",
            "Referer": "https://ep.tamin.ir/view/",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "sec-ch-ua": '"Google Chrome";v="115", "Chromium";v="115", "Not.A/Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
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

        if response.status_code == 401 or (
            response.status_code == 500
            and "data" in response.json()
            and response.json()["data"] == "خطای دسترسی"
        ):
            raise TokenError("Token is invalid or has expired.")
        # response.raise_for_status()
        # print(response.text)
        if "application/json" in response.headers.get("Content-Type", ""):
            response_text = response.text.replace("ي", "ی").replace("ك", "ک")
            response._content = response_text.encode("utf-8")
        return response

    def get(self, url, **kwargs):
        response = self.session.get(url, **kwargs)
        return self.handle_response(response)

    def post(self, url, **kwargs):
        response = self.session.post(url, **kwargs)
        # print(response.text)
        return self.handle_response(response)

    def put(self, url, **kwargs):
        response = self.session.put(url, **kwargs)
        return self.handle_response(response)

    def delete(self, url, **kwargs):
        response = self.session.delete(url, **kwargs)
        return self.handle_response(response)

    def login(self, username, password):
        # https://account.tamin.ir/auth/login
        pass

    def getPrecriptionGroup(self, headId: int, patientNationalId: str):
        # https://ep.tamin.ir/api/noteheadeprscs/get-details/6235778047?sort=%5B%5D
        response = self.get(
            f"{self.baseUrl}/noteheadeprscs/get-details/{headId}/{patientNationalId}?sort=%5B%5D"
        )
        return response.json()

    def getLastYearPrescriptions(
        self, nationalCode: str, year: str, page=1, start=0, limit=40
    ):
        # get current year in jalali
        doctor_id = self.getCurrentUser()["data"]["docId"]
        year_jalali = year
        # https://ep.tamin.ir/api/patients/faph?page=1&start=0&limit=7&filter=%5B%7B%22property%22:%22docId%22,%22value%22:%220000125265%22,%22operator%22:%22EQ%22%7D,%7B%22property%22:%22patient%22,%22value%22:%220072459158%22,%22operator%22:%22EQ%22%7D,%7B%22property%22:%22presctype%22,%22value%22:1,%22operator%22:%22EQ%22%7D,%7B%22property%22:%22PrescYear%22,%22value%22:1403,%22operator%22:%22EQ%22%7D%5D&sort=%5B%5D

        response = self.get(
            f"{self.baseUrl}/patients/faph?page={page}&start={start}&limit={limit}&filter=%5B%7B%22property%22:%22docId%22,%22value%22:%22{doctor_id}%22,%22operator%22:%22EQ%22%7D,%7B%22property%22:%22patient%22,%22value%22:%22{nationalCode}%22,%22operator%22:%22EQ%22%7D,%7B%22property%22:%22presctype%22,%22value%22:1,%22operator%22:%22EQ%22%7D,%7B%22property%22:%22PrescYear%22,%22value%22:{year_jalali},%22operator%22:%22EQ%22%7D%5D&sort=%5B%5D"
        )
        return response.json()

    def getCurrentUser(self):
        """users/get-full-current-user"""
        response = self.get(f"{self.baseUrl}/users/get-full-current-user")
        return response.json()

    def isPatientInsured(self, nationalCode: str) -> bool:
        # https://ep.tamin.ir/api/patients/fetchPatient/0442005921/%20?_dc=1718094536655

        now = datetime.now()
        milliseconds_now = int(now.timestamp() * 1000)

        response = self.get(
            f"{self.baseUrl}/patients/fetchPatient/{nationalCode}/%20?_dc={milliseconds_now}"
        )
        print(response.text)
        if response.status_code == 500:
            raise PatientNotFound("Patient does not exist.")

        if response.json()["data"]["patient"]["hasDesert"]:
            return True
        return False

    def getPatient(self, nationalCode):
        # https://ep.tamin.ir/api/patients/fetchPatient/0442005921/%20?_dc=1718094536655
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        milliseconds_tomorrow = int(tomorrow.timestamp() * 1000)

        response = self.get(
            f"{self.baseUrl}/patients/fetchPatient/{nationalCode}/%20?_dc={milliseconds_tomorrow}"
        )
        # if error 500 type return patient does not exist
        if (
            response.status_code == 500
            or response.json()["data"]["patient"]["errMsg"]
            == "کد ملی در پایگاه هویتی بیمه شدگان سازمان تامین وجود ندارد"
        ):
            raise PatientNotFound("Patient does not exist.")

        return response.json()

    def setOffice(self):
        self.put(f"{self.baseUrl}/users/place/office")

    def getServicesTypesByFilter(self):
        # https://ep.tamin.ir/api/ws-service-type/get-service-types-by-filter?filter=[{"property":"srvType","operator":"IN","value":"01,02,03,04,05,06,13"}]&sort=[]

        response = self.get(
            f"{self.baseUrl}/ws-service-type/get-service-types-by-filter?filter=%5B%7B%22property%22:%22srvType%22,%22operator%22:%22IN%22,%22value%22:%2201,02,03,04,05,06,13%22%7D%5D&sort=%5B%5D"
        )
        return response.json()

    def getNoteDetailsRefferal(self, nationalCode):
        """{"status":200,"family":"SUCCESSFUL","reason":"OK","data":{"size":0}}"""
        response = self.get(f"{self.baseUrl}/noteDetailsReferral/{nationalCode}")
        return response.json()

    def getSupplementaryInsurances(self):
        # supplementary/insurance/list
        response = self.get(f"{self.baseUrl}/supplementary/insurance/list")

        return response.json()

    def searchMedicines(self, value, page=1, start=0, limit=50):
        # https://ep.tamin.ir/api/services/get-services-space-splitting-performance?page=1&start=0&limit=7&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*vit*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2201%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D

        response = self.get(
            f"{self.baseUrl}/services/get-services-space-splitting-performance?page={page}&start={start}&limit={limit}&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*{value}*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2201%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D"
        )
        return response.json()

    def searchRepeatDays(self, value, page=1, start=0, limit=50):
        # https://ep.tamin.ir/api/repeatDays?page=1&start=0&limit=7&filter=%5B%7B%22property%22:%22repeatDaysDesc%22,%22value%22:%22*%D8%B4*%22,%22operator%22:%22LIKE%22%7D%5D&sort=%5B%5D
        """{
            "status": 200,
            "family": "SUCCESSFUL",
            "reason": "OK",
            "data": {
                "total": 1,
                "list": [
                {
                    "repeatDaysId": 6,
                    "repeatDaysCode": "90",
                    "repeatDaysDesc": "هر سه ماه"
                }
                ]
            }
        }"""
        response = self.get(
            f"{self.baseUrl}/repeatDays?page={page}&start={start}&limit={limit}&filter=%5B%7B%22property%22:%22repeatDaysDesc%22,%22value%22:%22*{value}*%22,%22operator%22:%22LIKE%22%7D%5D&sort=%5B%5D"
        )
        return response.json()

    def searchMedicalTests(self, value, page=1, start=0, limit=50):
        # https://ep.tamin.ir/api/services/get-services-space-splitting-performance?page=1&start=0&limit=7&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*cb*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2202%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D

        return self.get(
            f"{self.baseUrl}/services/get-services-space-splitting-performance?page={page}&start={start}&limit={limit}&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*{value}*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2202%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D"
        ).json()

    def searchMedicalImaging(self, value, page=1, start=0, limit=50):
        # https://ep.tamin.ir/api/services/get-services-space-splitting-performance?page=1&start=0&limit=7&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*a*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2299%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D
        response = self.get(
            f"{self.baseUrl}/services/get-services-space-splitting-performance?page={page}&start={start}&limit={limit}&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*{value}*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2299%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D"
        )
        return response.json()

    def searchPhysiotherapy(self, value, page=1, start=0, limit=50):
        # https://ep.tamin.ir/api/services/get-services-space-splitting-performance?page=1&start=0&limit=7&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*%D8%B4*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2213%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D

        response = self.get(
            f"{self.baseUrl}/services/get-services-space-splitting-performance?page={page}&start={start}&limit={limit}&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*{value}*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2213%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D"
        )
        return response.json()

    def searchMedicalServices(self, value, page=1, start=0, limit=50):
        # https://ep.tamin.ir/api/services/get-services-space-splitting-performance?page=1&start=0&limit=7&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*a*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22checkDoctorsCommitmentServices%22,%22value%22:false,%22operator%22:%22EQUAL%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2217%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D

        response = self.get(
            f"{self.baseUrl}/services/get-services-space-splitting-performance?page={page}&start={start}&limit={limit}&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*{value}*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22checkDoctorsCommitmentServices%22,%22value%22:false,%22operator%22:%22EQUAL%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2217%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D"
        )
        return response.json()

    def searchReferalServices(self, value, page=1, start=0, limit=50):
        # https://ep.tamin.ir/api/services/get-services-space-splitting-performance?page=1&start=0&limit=7&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*s*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2217%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D

        response = self.get(
            f"{self.baseUrl}/services/get-services-space-splitting-performance?page={page}&start={start}&limit={limit}&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*{value}*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2217%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D"
        )
        return response.json()

    def searchAutismRehabilitation(self, value, page=1, start=0, limit=50):
        # https://ep.tamin.ir/api/services/get-services-space-splitting-performance?page=1&start=0&limit=7&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*%D8%B4*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2219%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D

        response = self.get(
            f"{self.baseUrl}/services/get-services-space-splitting-performance?page={page}&start={start}&limit={limit}&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*{value}*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2219%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D"
        )
        return response.json()

    def visit(self, nationalCode: str, comment: str):
        # https://ep.tamin.ir/api/noteheadeprscs/save/0

        patient = self.getPatient(nationalCode)
        patientDetail = patient["data"]["patient"]
        birthDateYear = patientDetail["birthDate"]
        isoFormatedBirthDate = f"{int(birthDateYear) + 621}-03-20T20:30:00.000Z"
        response = self.post(
            f"{self.baseUrl}/noteheadeprscs/save/0",
            json={
                "noteDetailEprscs": [],
                "isSaveEprsc": "0",
                "supplementaryInsurance": {},
                "deserveInfo": {
                    "gender": patientDetail["sex"],
                    "hasDesert": patientDetail["hasDesert"],
                    "insuranceType": patientDetail["insuranceType"],
                    "patientBirthDate": patientDetail["birthDate"],
                    "risuid": patientDetail["bimNo"],
                    "trackingCode": patientDetail["trackingCode"],
                },
                "fName": patientDetail["fName"],
                "lName": patientDetail["lName"],
                "mobile": "09120000000",
                "birthDate": isoFormatedBirthDate,
                "patient": patientDetail["nationalCode"],
                "insuranceState": "1",
                "prescDate": "1718262015001",
                "expireDate": "1723462015001",
                "confirmStatus": "0",
                "creatorType": "3",
                "regStatus": "1",
                "prescType": {"prescTypeId": 3},  # visit type
                "comments": comment,
                "noteHeadEprscId": 0,
                "docClinic": None,
                "isSpecialPatient": 1 if patient["data"]["specialPatient"] else 0,
            },
        )
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "status": 500,
                "error": "Internal Server Error",
                "msg": response.text,
            }

    def getDrugInstructions(self):
        # https://ep.tamin.ir/api/druginstructions?filter=%5B%5D&sort=%5B%7B%22property%22:%22drugInstId%22,%22direction%22:%22ASC%22%7D%5D

        response = self.get(
            f"{self.baseUrl}/druginstructions?filter=%5B%5D&sort=%5B%7B%22property%22:%22drugInstId%22,%22direction%22:%22ASC%22%7D%5D"
        )
        return response.json()

    def getDrugAmount(self):
        # https://ep.tamin.ir/api/DrugAmnt?filter=%5B%5D&sort=%5B%7B%22property%22:%22drugAmntId%22,%22direction%22:%22ASC%22%7D%5D

        response = self.get(
            f"{self.baseUrl}/DrugAmnt?filter=%5B%5D&sort=%5B%7B%22property%22:%22drugAmntId%22,%22direction%22:%22ASC%22%7D%5D"
        )
        return response.json()

    def getDrugUsage(self):
        # https://ep.tamin.ir/api/drugUsage?filter=%5B%5D&sort=%5B%7B%22property%22:%22drugUsageId%22,%22direction%22:%22ASC%22%7D%5D

        response = self.get(
            f"{self.baseUrl}/drugUsage?filter=%5B%5D&sort=%5B%7B%22property%22:%22drugUsageId%22,%22direction%22:%22ASC%22%7D%5D"
        )
        return response.json()

    def prescribeMedicine(self, nationalCode: str, comment: str, medicines: list):
        """medicines are list of search medicines with the drugAmount, drugInstruction and quantity"""
        # https://ep.tamin.ir/api/noteheadeprscs/save/0
        prescriptionDate = str(int(time.time() * 1000))
        prescriptionExpireDate = str(int(time.time() * 1000) + 5184000000)

        patient = self.getPatient(nationalCode)
        patientDetail = patient["data"]["patient"]
        birthDateYear = patientDetail["birthDate"]
        isoFormatedBirthDate = f"{int(birthDateYear) + 621}-03-20T20:30:00.000Z"
        noteDetailEprscs = []
        for medicine in medicines:
            noteDetailEprscs.append(
                {
                    "srvRem": int(medicine["status"]),
                    "noteDetailsEprscId": 0,
                    "timesAday": {
                        "drugAmntCode": medicine["drugAmount"]["drugAmntCode"],
                        "drugAmntConcept": medicine["drugAmount"]["drugAmntConcept"],
                        "drugAmntId": medicine["drugAmount"]["drugAmntId"],
                        "drugAmntLatin": medicine["drugAmount"]["drugAmntLatin"],
                        "drugAmntSumry": medicine["drugAmount"]["drugAmntSumry"],
                        "visibled": medicine["drugAmount"]["visibled"],
                    },
                    "drugInstruction": {
                        "drugInstCode": medicine["drugInstruction"]["drugInstCode"],
                        "drugInstConcept": medicine["drugInstruction"][
                            "drugInstConcept"
                        ],
                        "drugInstId": medicine["drugInstruction"]["drugInstId"],
                        "drugInstLatin": medicine["drugInstruction"]["drugInstLatin"],
                        "drugInstSumry": medicine["drugInstruction"]["drugInstSumry"],
                    },
                    "srvId": {
                        "srvId": medicine["srvId"],
                        "wsSrvCode": medicine["wsSrvCode"],
                        "srvType": {"srvType": "01"},
                    },
                    "srvQty": medicine["quantity"],
                    "srvPrice": medicine["srvPrice"],
                    "dose": None,
                    "doseCode": medicine["doseCode"],
                    "repeat": medicine["repeat"],
                    "dateDo": medicine["datedo"],
                    "isBrand": None,
                    "noteHeadEprscId": 1,
                    "isOk": "0",
                    "drugInstId": 0,
                    "drugAmntId": 0,
                    "organDesc": "",
                    "illnessDesc": None,
                    "planDesc": None,
                    "organDetDesc": None,
                    "confirmStatusflag": None,
                    "toothId": "",
                    "status": "",
                    "statusstDate": "",
                    "visible": "",
                    "referenceStatus": 0,
                }
            )
        payload = {
            "noteDetailEprscs": noteDetailEprscs,
            "isSaveEprsc": "0",
            "supplementaryInsurance": {},
            "deserveInfo": {
                "gender": patientDetail["sex"],
                "hasDesert": patientDetail["hasDesert"],
                "insuranceType": patientDetail["insuranceType"],
                "patientBirthDate": patientDetail["birthDate"],
                "risuid": patientDetail["bimNo"],
                "trackingCode": patientDetail["trackingCode"],
            },
            "noteHeadEprscSupplementary": {"complaintIDs": "210"},
            "fName": patientDetail["fName"],
            "lName": patientDetail["lName"],
            "mobile": "09120000000",
            "birthDate": isoFormatedBirthDate,
            "patient": str(nationalCode),
            "insuranceState": "1",
            "prescDate": prescriptionDate,
            "expireDate": prescriptionExpireDate,
            "confirmStatus": "0",
            "creatorType": "3",
            "regStatus": "1",
            "prescType": {
                "prescTypeId": 1  # medicine
            },
            "comments": comment,
            "noteHeadEprscId": 0,
            "docClinic": None,
            "isSpecialPatient": 1 if patient["data"]["specialPatient"] else 0,
        }

        response = self.post(f"{self.baseUrl}/noteheadeprscs/save/0", json=payload)
        # return {"response": response.json(),"body": response.request.body}
        json_response = response.json()
        if (
            response.status_code == 500
            and json_response["data"]
            == "پزشک گرامی، امکان ثبت یک کد خدمت برای یک بیمار در یک روز بیش از یکبار امکان\u200cپذیر نمی باشد"
        ):
            raise PrescriptionCountExceeded("Medicine Prescription Exceeded!")

        return json_response

    def prescribeTest(self, nationalCode: str, comment: str, tests: list):
        # https://ep.tamin.ir/api/noteheadeprscs/save/0
        prescriptionDate = str(int(time.time() * 1000))
        prescriptionExpireDate = str(int(time.time() * 1000) + 5184000000)
        patient = self.getPatient(nationalCode)
        patientDetail = patient["data"]["patient"]
        birthDateYear = patientDetail["birthDate"]
        isoFormatedBirthDate = f"{int(birthDateYear) + 621}-03-20T20:30:00.000Z"
        noteDetailEprscs = []
        for test in tests:
            noteDetailEprscs.append(
                {
                    "srvRem": int(test["status"]),
                    "noteDetailsEprscId": 0,
                    "srvId": {"srvId": test["srvId"], "srvType": {}},
                    "dateDo": test["date"],
                    "srvQty": 1,
                    "srvPrice": test["srvPrice"],
                    "dose": None,
                    "doseCode": test["doseCode"],
                    "repeat": "",
                    "isBrand": None,
                    "noteHeadEprscId": 1,
                    "isOk": "0",
                    "drugInstId": 0,
                    "drugAmntId": 0,
                    "organDesc": "",
                    "illnessDesc": None,
                    "planDesc": None,
                    "organDetDesc": None,
                    "confirmStatusflag": None,
                    "toothId": "",
                    "status": "",
                    "statusstDate": "",
                    "visible": "",
                    "referenceStatus": 0,
                }
            )
        payload = {
            "noteDetailEprscs": noteDetailEprscs,
            "isSaveEprsc": "0",
            "supplementaryInsurance": {},
            "deserveInfo": {
                "gender": patientDetail["sex"],
                "hasDesert": patientDetail["hasDesert"],
                "insuranceType": patientDetail["insuranceType"],
                "patientBirthDate": patientDetail["birthDate"],
                "risuid": patientDetail["bimNo"],
                "trackingCode": patientDetail["trackingCode"],
            },
            "fName": patientDetail["fName"],
            "lName": patientDetail["lName"],
            "mobile": "09120000000",
            "birthDate": isoFormatedBirthDate,
            "patient": str(nationalCode),
            "insuranceState": "1",
            "prescDate": prescriptionDate,
            "expireDate": prescriptionExpireDate,
            "confirmStatus": "0",
            "creatorType": "3",
            "regStatus": "1",
            "prescType": {
                "prescTypeId": 2  # medical test
            },
            "comments": comment,
            "noteHeadEprscId": 0,
            "docClinic": None,
            "isSpecialPatient": 1 if patient["data"]["specialPatient"] else 0,
        }

        response = self.post(f"{self.baseUrl}/noteheadeprscs/save/0", json=payload)
        return response.json()

    def editMedicalTestPrescription(
        self, code: str, nationalCode: str, comment: str, tests: list
    ):
        # https://ep.tamin.ir/api/noteheadeprscs/save/0
        code = int(code)
        if not self.isPrescriptionEditable(code):
            raise PrescriptionNotEditable("Prescription is not editable.")

        prescriptionDate = str(int(time.time() * 1000))
        prescriptionExpireDate = str(int(time.time() * 1000) + 5184000000)
        patient = self.getPatient(nationalCode)
        patientDetail = patient["data"]["patient"]
        birthDateYear = patientDetail["birthDate"]
        isoFormatedBirthDate = f"{int(birthDateYear) + 621}-03-20T20:30:00.000Z"
        noteDetailEprscs = []
        for test in tests:
            noteDetailEprscs.append(
                {
                    "srvRem": int(test["status"]),
                    "noteDetailsEprscId": 0,
                    "srvId": {"srvId": test["srvId"], "srvType": {}},
                    "dateDo": test["date"],
                    "srvQty": 1,
                    "srvPrice": test["srvPrice"],
                    "dose": None,
                    "doseCode": test["doseCode"],
                    "repeat": "",
                    "isBrand": None,
                    "noteHeadEprscId": 1,
                    "isOk": "0",
                    "drugInstId": 0,
                    "drugAmntId": 0,
                    "organDesc": "",
                    "illnessDesc": None,
                    "planDesc": None,
                    "organDetDesc": None,
                    "confirmStatusflag": None,
                    "toothId": "",
                    "status": "",
                    "statusstDate": "",
                    "visible": "",
                    "referenceStatus": 0,
                }
            )
        payload = {
            "noteDetailEprscs": noteDetailEprscs,
            "isSaveEprsc": "0",
            "supplementaryInsurance": {},
            "deserveInfo": {
                "gender": patientDetail["sex"],
                "hasDesert": patientDetail["hasDesert"],
                "insuranceType": patientDetail["insuranceType"],
                "patientBirthDate": patientDetail["birthDate"],
                "risuid": patientDetail["bimNo"],
                "trackingCode": patientDetail["trackingCode"],
            },
            "fName": patientDetail["fName"],
            "lName": patientDetail["lName"],
            "mobile": "09120000000",
            "birthDate": isoFormatedBirthDate,
            "patient": str(nationalCode),
            "insuranceState": "1",
            "prescDate": prescriptionDate,
            "expireDate": prescriptionExpireDate,
            "confirmStatus": "0",
            "creatorType": "3",
            "regStatus": "1",
            "prescType": {
                "prescTypeId": 2  # medical test
            },
            "comments": comment,
            "noteHeadEprscId": code,
            "docClinic": None,
            "isSpecialPatient": 1 if patient["data"]["specialPatient"] else 0,
        }

        response = self.post(f"{self.baseUrl}/noteheadeprscs/save/0", json=payload)
        return response.json()

    def prescribeImaging(self, nationalCode: str, comment: str, prescs: list):
        # https://ep.tamin.ir/api/noteheadeprscs/save/0
        prescriptionDate = str(int(time.time() * 1000))
        prescriptionExpireDate = str(int(time.time() * 1000) + 5184000000)
        patient = self.getPatient(nationalCode)
        patientDetail = patient["data"]["patient"]
        birthDateYear = patientDetail["birthDate"]
        isoFormatedBirthDate = f"{int(birthDateYear) + 621}-03-20T20:30:00.000Z"
        noteDetailEprscs = []
        for presc in prescs:
            noteDetailEprscs.append(
                {
                    "srvRem": int(presc["status"]),
                    "noteDetailsEprscId": 0,
                    "timesAday": None,
                    "drugInstruction": None,
                    "srvId": {
                        "srvId": presc["srvId"],
                        "srvType": {"srvType": presc["srvType"]["srvType"]},
                    },
                    "srvQty": 1,
                    "srvPrice": presc["srvPrice"],
                    "dose": None,
                    "doseCode": presc["doseCode"],
                    "repeat": None,
                    "isBrand": None,
                    "noteHeadEprscId": 1,
                    "dateDo": presc["date"],
                    "isOk": "0",
                    "organId": None,
                    "drugInstId": 0,
                    "drugAmntId": 0,
                    "isPayable": None,
                    "organDesc": "",
                    "illnessId": None,
                    "illnessDesc": None,
                    "planId": None,
                    "planDesc": None,
                    "organDet": None,
                    "organDetDesc": None,
                    "confirmStatusflag": None,
                    "isDentalService": None,
                    "toothId": "",
                    "status": "",
                    "statusstDate": "",
                    "visible": "",
                    "referenceStatus": 0,
                }
            )
        payload = {
            "noteDetailEprscs": noteDetailEprscs,
            "isSaveEprsc": "0",
            "supplementaryInsurance": {},
            "deserveInfo": {
                "gender": patientDetail["sex"],
                "hasDesert": patientDetail["hasDesert"],
                "insuranceType": patientDetail["insuranceType"],
                "patientBirthDate": patientDetail["birthDate"],
                "risuid": patientDetail["bimNo"],
                "trackingCode": patientDetail["trackingCode"],
            },
            "fName": patientDetail["fName"],
            "lName": patientDetail["lName"],
            "mobile": "09120000000",
            "birthDate": isoFormatedBirthDate,
            "patient": str(nationalCode),
            "insuranceState": "1",
            "prescDate": prescriptionDate,
            "expireDate": prescriptionExpireDate,
            "confirmStatus": "0",
            "creatorType": "3",
            "regStatus": "1",
            "prescType": {
                "prescTypeId": 2  # medical imaging
            },
            "comments": comment,
            "noteHeadEprscId": 0,
            "docClinic": None,
            "isSpecialPatient": 1 if patient["data"]["specialPatient"] else 0,
        }

        response = self.post(f"{self.baseUrl}/noteheadeprscs/save/0", json=payload)
        return response.json()

    def editPrescriptionImaging(
        self, editCode: str, nationalCode: str, comment: str, prescs: list
    ):
        editCode = int(editCode)
        # https://ep.tamin.ir/api/noteheadeprscs/save/0
        if editCode and not self.isPrescriptionEditable(editCode):
            raise PrescriptionNotEditable("Prescription is not editable.")

        prescriptionDate = str(int(time.time() * 1000))
        prescriptionExpireDate = str(int(time.time() * 1000) + 5184000000)
        patient = self.getPatient(nationalCode)
        patientDetail = patient["data"]["patient"]
        birthDateYear = patientDetail["birthDate"]
        isoFormatedBirthDate = f"{int(birthDateYear) + 621}-03-20T20:30:00.000Z"
        noteDetailEprscs = []
        for presc in prescs:
            noteDetailEprscs.append(
                {
                    "srvRem": int(presc["status"]),
                    "noteDetailsEprscId": 0,
                    "srvId": {"srvId": presc["srvId"], "srvType": {}},
                    "dateDo": presc["date"],
                    "srvQty": 1,
                    "srvPrice": presc["srvPrice"],
                    "dose": None,
                    "doseCode": presc["doseCode"],
                    "repeat": "",
                    "isBrand": None,
                    "noteHeadEprscId": 1,
                    "isOk": "0",
                    "drugInstId": 0,
                    "drugAmntId": 0,
                    "organDesc": "",
                    "illnessDesc": None,
                    "planDesc": None,
                    "organDetDesc": None,
                    "confirmStatusflag": None,
                    "toothId": "",
                    "status": "",
                    "statusstDate": "",
                    "visible": "",
                    "referenceStatus": 0,
                }
            )
        payload = {
            "noteDetailEprscs": noteDetailEprscs,
            "isSaveEprsc": "0",
            "deserveInfo": {
                "gender": patientDetail["sex"],
                "hasDesert": patientDetail["hasDesert"],
                "insuranceType": patientDetail["insuranceType"],
                "patientBirthDate": patientDetail["birthDate"],
                "risuid": patientDetail["bimNo"],
                "trackingCode": patientDetail["trackingCode"],
            },
            "supplementaryInsurance": {},
            "fName": patientDetail["fName"],
            "lName": patientDetail["lName"],
            "mobile": "09120000000",
            "birthDate": isoFormatedBirthDate,
            "patient": str(nationalCode),
            "insuranceState": "1",
            "prescDate": prescriptionDate,
            "expireDate": prescriptionExpireDate,
            "confirmStatus": "0",
            "creatorType": "3",
            "regStatus": "1",
            "prescType": {
                "prescTypeId": 2  # medical imaging
            },
            "comments": comment,
            "noteHeadEprscId": editCode,
            "docClinic": None,
            "isSpecialPatient": 1 if patient["data"]["specialPatient"] else 0,
        }

        response = self.post(f"{self.baseUrl}/noteheadeprscs/save/0", json=payload)
        return response.json()

    def deletePrescription(self, code: str):
        # https://ep.tamin.ir/api/noteheadeprscs/head/6613503057
        response = self.delete(f"{self.baseUrl}/noteheadeprscs/head/{code}")
        if response.status_code == 400:
            raise DeletePrescriptionError("Prescription can not be deleted.")
        return response.json()

    def editMedicinePrescription(
        self, nationalCode: str, code: str, comment: str, medicines: list
    ):
        """medicines are list of search medicines with the drugAmount, drugInstruction and quantity"""
        # https://ep.tamin.ir/api/noteheadeprscs/save/0
        code = int(code)
        if not self.isPrescriptionEditable(code):
            raise PrescriptionNotEditable("Prescription is not editable.")

        prescriptionDate = str(int(time.time() * 1000))
        prescriptionExpireDate = str(int(time.time() * 1000) + 5184000000)

        patient = self.getPatient(nationalCode)
        patientDetail = patient["data"]["patient"]
        birthDateYear = patientDetail["birthDate"]
        isoFormatedBirthDate = f"{int(birthDateYear) + 621}-03-20T20:30:00.000Z"
        noteDetailEprscs = []
        for medicine in medicines:
            noteDetailEprscs.append(
                {
                    "srvRem": int(medicine["status"]),
                    "noteDetailsEprscId": 0,
                    "timesAday": {
                        "drugAmntCode": medicine["drugAmount"]["drugAmntCode"],
                        "drugAmntConcept": medicine["drugAmount"]["drugAmntConcept"],
                        "drugAmntId": medicine["drugAmount"]["drugAmntId"],
                        "drugAmntLatin": medicine["drugAmount"]["drugAmntLatin"],
                        "drugAmntSumry": medicine["drugAmount"]["drugAmntSumry"],
                        "visibled": medicine["drugAmount"]["visibled"],
                    },
                    "drugInstruction": {
                        "drugInstCode": medicine["drugInstruction"]["drugInstCode"],
                        "drugInstConcept": medicine["drugInstruction"][
                            "drugInstConcept"
                        ],
                        "drugInstId": medicine["drugInstruction"]["drugInstId"],
                        "drugInstLatin": medicine["drugInstruction"]["drugInstLatin"],
                        "drugInstSumry": medicine["drugInstruction"]["drugInstSumry"],
                    },
                    "srvId": {
                        "srvId": medicine["srvId"],
                        "wsSrvCode": medicine["wsSrvCode"],
                        "srvType": {"srvType": "01"},
                    },
                    "srvQty": medicine["quantity"],
                    "srvPrice": medicine["srvPrice"],
                    "dose": None,
                    "doseCode": medicine["doseCode"],
                    "repeat": "",
                    "isBrand": None,
                    "noteHeadEprscId": 1,
                    "isOk": "0",
                    "drugInstId": 0,
                    "drugAmntId": 0,
                    "organDesc": "",
                    "illnessDesc": None,
                    "planDesc": None,
                    "organDetDesc": None,
                    "confirmStatusflag": None,
                    "toothId": "",
                    "status": "",
                    "statusstDate": "",
                    "visible": "",
                    "referenceStatus": 0,
                }
            )
        payload = {
            "noteDetailEprscs": noteDetailEprscs,
            "isSaveEprsc": "0",
            "supplementaryInsurance": {},
            "deserveInfo": {
                "gender": patientDetail["sex"],
                "hasDesert": patientDetail["hasDesert"],
                "insuranceType": patientDetail["insuranceType"],
                "patientBirthDate": patientDetail["birthDate"],
                "risuid": patientDetail["bimNo"],
                "trackingCode": patientDetail["trackingCode"],
            },
            "fName": patientDetail["fName"],
            "lName": patientDetail["lName"],
            "mobile": "09120000000",
            "birthDate": isoFormatedBirthDate,
            "patient": str(nationalCode),
            "insuranceState": "1",
            "prescDate": prescriptionDate,
            "expireDate": prescriptionExpireDate,
            "confirmStatus": "0",
            "creatorType": "3",
            "regStatus": "1",
            "prescType": {
                "prescTypeId": 1  # medicine
            },
            "comments": comment,
            "noteHeadEprscId": code,
            "docClinic": None,
            "isSpecialPatient": 1 if patient["data"]["specialPatient"] else 0,
        }

        response = self.post(f"{self.baseUrl}/noteheadeprscs/save/0", json=payload)
        # return {"response": response.json(),"body": response.request.body}
        json_response = response.json()
        return json_response

    def isPrescriptionEditable(self, code: str):
        # https://ep.tamin.ir/api/noteheadeprscs/noteHeadWithDetails?noteHeadEprscId=6615113649&nationCode=0072459158
        nationalCode = self.getCurrentUser()["data"]["nationalCode"]
        response = self.get(
            f"{self.baseUrl}/noteheadeprscs/noteHeadWithDetails?noteHeadEprscId={code}&nationCode={nationalCode}"
        )
        isEditable = True
        for item in response.json()["data"]["noteDetail"]:
            if item["isOk"] == "1":
                isEditable = False
                break

        return isEditable

    def searchOtherParaclinicServices(
        self, value: str, category_code: str, page=1, start=0, limit=10
    ):
        # https://ep.tamin.ir/api/services/get-services-space-splitting-performance?page=1&start=0&limit=8&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*a*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%2214%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D

        response = self.get(
            f"{self.baseUrl}/services/get-services-space-splitting-performance?page={page}&start={start}&limit={limit}&filter=%5B%7B%22property%22:%22srvName%22,%22value%22:%22*{value}*%22,%22operator%22:%22LIKE%22%7D,%7B%22property%22:%22srvType%22,%22value%22:%22{category_code}%22,%22operator%22:%22EQUAL%22%7D%5D&sort=%5B%5D"
        )
        return response.json()

    def prescribeOtherParaclinicServices(
        self, nationalCode: str, comment: str, prescs: list
    ):
        # https://ep.tamin.ir/api/noteheadeprscs/save/0
        prescriptionDate = str(int(time.time() * 1000))
        prescriptionExpireDate = str(int(time.time() * 1000) + 5184000000)
        patient = self.getPatient(nationalCode)
        patientDetail = patient["data"]["patient"]
        birthDateYear = patientDetail["birthDate"]
        isoFormatedBirthDate = f"{int(birthDateYear) + 621}-03-20T20:30:00.000Z"
        noteDetailEprscs = []
        for presc in prescs:
            noteDetailEprscs.append(
                {
                    "srvRem": int(presc["status"]),
                    "noteDetailsEprscId": 0,
                    "srvId": {"srvId": presc["srvId"], "srvType": {}},
                    "srvQty": 1,
                    "srvPrice": presc["srvPrice"],
                    "noteHeadEprscId": 1,
                    "dateDo": presc["date"],
                    "isOk": "0",
                    "drugInstId": 0,
                    "drugAmntId": 0,
                    "organDesc": "",
                    "illnessDesc": None,
                    "planDesc": None,
                    "organDetDesc": None,
                    "confirmStatusflag": None,
                    "toothId": "",
                    "status": "",
                    "statusstDate": "",
                    "visible": "",
                    "referenceStatus": 0,
                }
            )
        payload = {
            "noteDetailEprscs": noteDetailEprscs,
            "isSaveEprsc": "0",
            "supplementaryInsurance": {},
            "deserveInfo": {
                "gender": patientDetail["sex"],
                "hasDesert": patientDetail["hasDesert"],
                "insuranceType": patientDetail["insuranceType"],
                "patientBirthDate": patientDetail["birthDate"],
                "risuid": patientDetail["bimNo"],
                "trackingCode": patientDetail["trackingCode"],
            },
            "fName": patientDetail["fName"],
            "lName": patientDetail["lName"],
            "mobile": "09120000000",
            "birthDate": isoFormatedBirthDate,
            "patient": str(nationalCode),
            "insuranceState": "1",
            "prescDate": prescriptionDate,
            "expireDate": prescriptionExpireDate,
            "confirmStatus": "0",
            "creatorType": "3",
            "regStatus": "1",
            "prescType": {"prescTypeId": 2},
            "comments": comment,
            "noteHeadEprscId": 0,
            "docClinic": None,
            "isSpecialPatient": 1 if patient["data"]["specialPatient"] else 0,
        }

        response = self.post(f"{self.baseUrl}/noteheadeprscs/save/0", json=payload)
        return response.json()

    def editOtherParaclinicServicesPrescription(
        self, editCode: str, nationalCode: str, comment: str, prescs: list
    ):
        editCode = int(editCode)
        # https://ep.tamin.ir/api/noteheadeprscs/save/0
        if editCode and not self.isPrescriptionEditable(editCode):
            raise PrescriptionNotEditable("Prescription is not editable.")

        prescriptionDate = str(int(time.time() * 1000))
        prescriptionExpireDate = str(int(time.time() * 1000) + 5184000000)
        patient = self.getPatient(nationalCode)
        patientDetail = patient["data"]["patient"]
        birthDateYear = patientDetail["birthDate"]
        isoFormatedBirthDate = f"{int(birthDateYear) + 621}-03-20T20:30:00.000Z"
        noteDetailEprscs = []
        for presc in prescs:
            noteDetailEprscs.append(
                {
                    "srvRem": int(presc["status"]),
                    "noteDetailsEprscId": 0,
                    "srvId": {"srvId": presc["srvId"], "srvType": {}},
                    "srvQty": 1,
                    "srvPrice": presc["srvPrice"],
                    "noteHeadEprscId": 1,
                    "dateDo": presc["date"],
                    "isOk": "0",
                    "drugInstId": 0,
                    "drugAmntId": 0,
                    "organDesc": "",
                    "illnessDesc": None,
                    "planDesc": None,
                    "organDetDesc": None,
                    "confirmStatusflag": None,
                    "toothId": "",
                    "status": "",
                    "statusstDate": "",
                    "visible": "",
                    "referenceStatus": 0,
                }
            )
        payload = {
            "noteDetailEprscs": noteDetailEprscs,
            "supplementaryInsurance": {},
            "deserveInfo": {
                "gender": patientDetail["sex"],
                "hasDesert": patientDetail["hasDesert"],
                "insuranceType": patientDetail["insuranceType"],
                "patientBirthDate": patientDetail["birthDate"],
                "risuid": patientDetail["bimNo"],
                "trackingCode": patientDetail["trackingCode"],
            },
            "fName": patientDetail["fName"],
            "lName": patientDetail["lName"],
            "mobile": "09120000000",
            "birthDate": isoFormatedBirthDate,
            "patient": str(nationalCode),
            "insuranceState": "1",
            "prescDate": prescriptionDate,
            "expireDate": prescriptionExpireDate,
            "confirmStatus": "0",
            "creatorType": "3",
            "regStatus": "1",
            "prescType": {"prescTypeId": 2},
            "comments": comment,
            "noteHeadEprscId": editCode,
            "docClinic": None,
            "isSpecialPatient": 1 if patient["data"]["specialPatient"] else 0,
        }

        response = self.post(f"{self.baseUrl}/noteheadeprscs/save/0", json=payload)
        return response.json()
