from rest_framework import serializers
from insurance.connection.tamin_connection import (
    PatientNotFound,
    TaminClient,
    TokenError,
)
from medical_tests.models import (
    Laboratory,
    TestMetric,
    TestResultGroup,
    TestResultItem,
)
from patient.models import Patient
from visit.ascvd.ascvd import ASCVDCalculator
from django.db import models
from visit.models.history_models import PatientImpressionItem
from rest_framework.exceptions import ValidationError


class PatientReducedSerializer(serializers.ModelSerializer):
    """Serializer for patients."""

    class Meta:
        model = Patient
        fields = ["id", "full_name", "national_id", "phone_number", "insurance_company"]
        read_only_fields = ["id"]


class PatientChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing patient password."""

    password = serializers.CharField(write_only=True, required=True, min_length=8)
    patient_id = serializers.IntegerField()


class PatientRegisterSerializer(serializers.Serializer):
    """Serializer for changing patient password."""

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    national_id = serializers.CharField(required=True, min_length=10, max_length=10)
    phone_number = serializers.CharField(required=True)
    otp = serializers.CharField(required=True, min_length=4, max_length=4)


class PatientSearchSerializer(serializers.ModelSerializer):
    """Serializer for search patients."""

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    class Meta:
        model = Patient
        fields = ["id", "full_name", "national_id", "phone_number", "insurance_company"]
        read_only_fields = ["id"]


class PatientSerializer(serializers.ModelSerializer):
    """Serializer for patients."""

    class Meta:
        model = Patient
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "address",
            "phone_number",
            "national_id",
            "birth_date",
            "sex",
            "refferal_reason",
            "phone_number",
            "blood_group",
            "referer",
            "education",
            "occupation",
            "height",
            "weight",
            "insurance_company",
        ]
        read_only_fields = ["id"]

    # def create(self, validated_data):
    #     """Create a Patient."""
    #     patient = Patient.objects.create(**validated_data)
    #     return patient

    # def update(self, instance, validated_data):
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     return instance


class PatientVisitSerializerRequest(serializers.ModelSerializer):
    """Serializer for Patient Visit"""

    use_insurance = serializers.BooleanField(
        required=False, default=False, help_text="Use insurance to check patient"
    )
    insurance_state = serializers.SerializerMethodField(required=False)
    ascvd = serializers.SerializerMethodField(required=False)
    weight = serializers.SerializerMethodField(required=False)
    fib_4 = serializers.SerializerMethodField(required=False)
    bmi = serializers.SerializerMethodField(required=False)
    creatinine = serializers.SerializerMethodField(required=False)
    egfr = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Patient
        fields = [
            "id",
            "use_insurance",
            "birth_date",
            "national_id",
            "sex",
            "height",
            "weight",
            "insurance_state",
            "next_visit_date",
            "creatinine",
            "bmi",
            "fib_4",
            "egfr",
            "ascvd",
        ]

    def get_insurance_state(self, obj):
        request = self.context.get("request")
        token = request.headers.get("Tamin-Token")
        use_insurance = request.query_params.get("use_insurance", False)
        if use_insurance and token:
            try:
                taminClient = TaminClient(token)
                if taminClient.isPatientInsured(obj.national_id):
                    return "yes"
                else:
                    return "no"
            except TokenError:
                # raise 401
                raise ValidationError({"error": "Tamin Token is invalid or expired"})

            except PatientNotFound:
                return "not_found"

        return "not_checked"

    def get_creatinine(self, obj):
        last_creatinine = (
            TestResultItem.objects.filter(group__patient__id=obj.id, metric__name="Cr")
            .annotate(date=models.F("group__date"))
            .order_by("-date")
            .first()
        )
        state = {
            "value": None,
            "msg": None,
            "date": None,
        }
        if last_creatinine:
            state["value"] = last_creatinine.value
            state["date"] = last_creatinine.date
        else:
            state["msg"] = "No creatinine test found"
        return state

    def get_weight(self, obj):
        last_weight = (
            TestResultItem.objects.filter(
                group__patient__id=obj.id, metric__name="weight"
            )
            .annotate(date=models.F("group__date"))
            .order_by("-date")
            .first()
        )

        state = {
            "value": None,
            "date": None,
            "msg": None,
        }
        if last_weight:
            state["value"] = last_weight.value
            state["date"] = last_weight.date
        elif obj.weight:
            state["value"] = obj.weight
        else:
            state["msg"] = "No weight found"
        return state

    def get_bmi(self, obj):
        state = {
            "value": None,
            "msg": None,
            "date": None,
        }
        if not obj.height:
            state["msg"] = "No height found"
            return state

        last_weight_obj = self.get_weight(obj=obj)
        last_weight = last_weight_obj["value"]
        if last_weight:
            state["value"] = round(last_weight / ((obj.height / 100) ** 2), 1)
            state["date"] = last_weight_obj["date"]
        else:
            state["msg"] = "No weight found"
        return state

    def get_fib_4(self, obj):
        state = {
            "value": None,
            "msg": None,
            "date": None,
        }
        age = obj.age()
        if not age:
            state["msg"] = "Age not provided"
            return state
        ast = (
            TestResultItem.objects.filter(group__patient__id=obj.id, metric__name="AST")
            .annotate(date=models.F("group__date"))
            .order_by("-date")
            .first()
        )
        if not ast:
            state["msg"] = "Ast not provided"
            return state
        alt = (
            TestResultItem.objects.filter(group__patient__id=obj.id, metric__name="ALT")
            .annotate(date=models.F("group__date"))
            .order_by("-date")
            .first()
        )
        if not alt:
            state["msg"] = "Alt not provided"
            return state
        platelet = (
            TestResultItem.objects.filter(group__patient__id=obj.id, metric__name="plt")
            .annotate(date=models.F("group__date"))
            .order_by("-date")
            .first()
        )
        if not platelet:
            state["msg"] = "Platelet not provided"
            return state
        state["msg"] = f"AST: {ast.value} \ ALT: {alt.value} \ Plt: {platelet.value}"
        state["date"] = min(ast.date, alt.date, platelet.date)
        state["value"] = round(
            (ast.value / alt.value**0.5) * (1 / platelet.value) * age, 2
        )
        return state

    def get_egfr(self, obj):
        state = {
            "value": None,
            "msg": None,
            "date": None,
        }

        sex = obj.sex
        age = obj.age()

        if not age:
            state["msg"] = "No age found"
            return state

        if not sex:
            state["msg"] = "Sex not found"
            return state

        last_creatinine_obj = self.get_creatinine(obj=obj)
        last_creatinine = last_creatinine_obj["value"]

        if not last_creatinine:
            state["msg"] = "No creatinine test found"
            return state
        state["date"] = last_creatinine_obj["date"]
        # calculate egfr to fixed 2 decimal points
        if sex == "F":
            if last_creatinine <= 0.7:
                egfr = 142 * (last_creatinine / 0.7) ** -0.241 * 0.9938**age * 1.012
            else:
                egfr = 142 * (last_creatinine / 0.7) ** -1.209 * 0.9938**age * 1.012
        else:
            if last_creatinine <= 0.9:
                egfr = 186 * (last_creatinine / 0.9) ** -0.203 * 0.9938**age * 1.012
            else:
                egfr = 186 * (last_creatinine / 0.9) ** -1.154 * 0.9938**age * 1.012
        state["value"] = round(egfr, 1)
        state["msg"] = f"Cr: {last_creatinine}"
        return state

    def get_ascvd(self, obj):
        state = {
            "value": None,
            "msg": None,
            "date": None,
        }
        is_male = obj.sex == "M"
        age = obj.age()
        if not age:
            state["msg"] = "Age not provided"
            return state
        total_chol = (
            TestResultItem.objects.filter(
                group__patient__id=obj.id, metric__name="Cholesterol"
            )
            .annotate(date=models.F("group__date"))
            .order_by("-date")
            .first()
        )
        hdl = (
            TestResultItem.objects.filter(group__patient__id=obj.id, metric__name="HDL")
            .annotate(date=models.F("group__date"))
            .order_by("-date")
            .first()
        )
        ldl = (
            TestResultItem.objects.filter(group__patient__id=obj.id, metric__name="LDL")
            .annotate(date=models.F("group__date"))
            .order_by("-date")
            .first()
        )

        dias_bp = (
            TestResultItem.objects.filter(
                group__patient__id=obj.id, metric__name="Diastolic BP"
            )
            .annotate(date=models.F("group__date"))
            .order_by("-date")
            .first()
        )

        systolic_bp = (
            TestResultItem.objects.filter(
                group__patient__id=obj.id, metric__name="Systolic BP"
            )
            .annotate(date=models.F("group__date"))
            .order_by("-date")
            .first()
        )
        has_diabetes = PatientImpressionItem.objects.filter(
            patient=obj, impression__name__in=["DM2", "DM"]
        ).exists()

        if not hasattr(obj, "basic_history") or not obj.basic_history:
            on_hypertension = False
            smoking = "never"
            on_aspirin = False
            on_statin = False

        else:
            on_hypertension = bool(obj.basic_history.htn)
            smoking = obj.basic_history.smoking
            # smoking_choices = {
            #     "Active": "Active",
            #     "Passive": "Passive",
            #     "Ex-smoker": "Ex-smoker",
            # }
            if smoking in ["Active", "Passive"]:
                smoking = "current"
            elif smoking == "Ex":
                smoking = "former"
            else:
                smoking = "never"

            on_aspirin = bool(obj.basic_history.aspirin)
            on_statin = bool(obj.basic_history.statin)

        if None in [
            total_chol,
            hdl,
            ldl,
            dias_bp,
            systolic_bp,
            age,
            is_male,
            has_diabetes,
            smoking,
            on_hypertension,
            on_aspirin,
            on_statin,
        ]:
            fields = {
                "total_chol": total_chol,
                "hdl": hdl,
                "ldl": ldl,
                "dias_bp": dias_bp,
                "systolic_bp": systolic_bp,
                "age": age,
                "is_male": is_male,
                "has_diabetes": has_diabetes,
                "smoking": smoking,
                "on_hypertension": on_hypertension,
                "on_aspirin": on_aspirin,
                "on_statin": on_statin,
            }

            missing_fields = [key for key, value in fields.items() if value is None]

            state["msg"] = f"These fields are not provided: {', '.join(missing_fields)}"
            return state

        try:
            calculator = ASCVDCalculator.get_instance()

            risk = calculator.calculate_ascvd(
                age,
                is_male,
                int(systolic_bp.value),
                int(dias_bp.value),
                int(total_chol.value),
                int(hdl.value),
                int(ldl.value),
                has_diabetes,
                smoking,
                on_hypertension,
                on_aspirin,
                on_statin,
            )
            ascvd_metric = TestMetric.objects.get(name="ASCVD")
            if risk["tenYear"]:
                risk_number = float(risk["tenYear"].replace("%", ""))
                # today = date.today()

                state["value"] = risk_number
                state["msg"] = (
                    f"Age: {age}, Sex: {'Male' if is_male else 'Female'}, "
                    f"Total Chol: {total_chol.value if total_chol else 'N/A'}, "
                    f"HDL: {hdl.value if hdl else 'N/A'}, LDL: {ldl.value if ldl else 'N/A'}, "
                    f"Sys BP: {systolic_bp.value if systolic_bp else 'N/A'}, "
                    f"Dias BP: {dias_bp.value if dias_bp else 'N/A'}, "
                    f"Has Diabetes: {has_diabetes}, Smoking: {smoking}, "
                    f"On Hypertension: {on_hypertension}, "
                    f"On Aspirin: {on_aspirin}, On Statin: {on_statin}"
                )
                state["date"] = min(
                    metric.date
                    for metric in [total_chol, hdl, ldl, dias_bp, systolic_bp]
                    if metric
                )
                lab = Laboratory.objects.get(name="ASCVD")
                ascvd_group, _ = TestResultGroup.objects.get_or_create(
                    patient=obj, date=state["date"], laboratory=lab
                )
                ascvd_item, created = TestResultItem.objects.get_or_create(
                    group=ascvd_group,
                    metric=ascvd_metric,
                    reference_range=1,
                    defaults={"raw_value": risk_number, "value": risk_number},
                )
                if not created:
                    # Update both raw_value and value
                    ascvd_item.raw_value = risk_number
                    # ascvd_item.value = risk_number
                    ascvd_item.save()

        except Exception:
            state["msg"] = "Unhandled Error calculating ASCVD"
        return state
        # except Exception as e:
        #     print(e)
        #     return None


# def calculate_ascvd_risk(
#     age: int,
#     sex: str,
#     race_african_american: bool,
#     total_cholesterol: float,
#     hdl_cholesterol: float,
#     systolic_bp: float,
#     on_hypertension_treatment: bool,
#     diabetic: bool,
#     smoker: bool,
# ) -> float:
#     # This function calculates 10-year ASCVD risk using the Pooled Cohort Equations.
#     # Inputs:
#     # age: int/float, patient's age in years
#     # sex: 'male' or 'female'
#     # race_african_american: bool, True if African American, False otherwise
#     # total_cholesterol: float, mg/dL
#     # hdl_cholesterol: float, mg/dL
#     # systolic_bp: float, mmHg
#     # on_hypertension_treatment: bool
#     # diabetic: bool
#     # smoker: bool

#     # Convert boolean to int for calculation
#     smoker_int = int(smoker)
#     diabetic_int = int(diabetic)
#     htn_treat_int = int(on_hypertension_treatment)

#     # Natural log of variables
#     ln_age = math.log(age)
#     ln_tc = math.log(total_cholesterol)
#     ln_hdl = math.log(hdl_cholesterol)
#     ln_sbp = math.log(systolic_bp)

#     # Coefficients from ACC/AHA Pooled Cohort Equations
#     # Reference: 2013 ACC/AHA Guideline on the Assessment of Cardiovascular Risk

#     if race_african_american and sex == "female":
#         # African American Female
#         coeff = {
#             "ln_age": 17.1141,
#             "ln_tc": 0.9396,
#             "ln_hdl": -18.9196,
#             "ln_age_hdl": 4.4748,
#             "ln_sbp_treated": 29.2907,
#             "ln_age_sbp_treated": -6.4321,
#             "ln_sbp_untreated": 27.8197,
#             "ln_age_sbp_untreated": -6.0873,
#             "smoker": 0.6908,
#             "diabetic": 0.8738,
#         }
#         baseline_s010 = 0.95334
#         mean_xb = 86.61

#     elif not race_african_american and sex == "female":
#         # Non-African American Female
#         coeff = {
#             "ln_age": -29.799,
#             "ln_age_squared": 4.884,
#             "ln_tc": 13.54,
#             "ln_age_tc": -3.114,
#             "ln_hdl": -13.578,
#             "ln_age_hdl": 3.149,
#             "ln_sbp_treated": 2.019,
#             "ln_sbp_untreated": 1.957,
#             "smoker": 7.574,
#             "ln_age_smoker": -1.665,
#             "diabetic": 0.661,
#         }
#         baseline_s010 = 0.96652
#         mean_xb = -29.18

#     elif race_african_american and sex == "male":
#         # African American Male
#         coeff = {
#             "ln_age": 2.469,
#             "ln_tc": 0.302,
#             "ln_hdl": -0.307,
#             "ln_sbp_treated": 1.916,
#             "ln_sbp_untreated": 1.809,
#             "smoker": 0.549,
#             "diabetic": 0.645,
#         }
#         baseline_s010 = 0.89536
#         mean_xb = 19.54

#     else:
#         # Non-African American Male
#         coeff = {
#             "ln_age": 12.344,
#             "ln_tc": 11.853,
#             "ln_age_tc": -2.664,
#             "ln_hdl": -7.99,
#             "ln_age_hdl": 1.769,
#             "ln_sbp_treated": 1.797,
#             "ln_sbp_untreated": 1.764,
#             "smoker": 7.837,
#             "ln_age_smoker": -1.795,
#             "diabetic": 0.658,
#         }
#         baseline_s010 = 0.91436
#         mean_xb = 61.18

#     # Calculate the linear predictor based on race, sex
#     if race_african_american and sex == "female":
#         # Special formula as per 2013 guideline
#         # Terms related to SBP differ if treated vs untreated
#         sbp_term = (
#             coeff["ln_sbp_treated"] * ln_sbp
#             if htn_treat_int == 1
#             else coeff["ln_sbp_untreated"] * ln_sbp
#         )
#         sbp_age_term = (
#             coeff["ln_age_sbp_treated"] * ln_sbp * ln_age
#             if htn_treat_int == 1
#             else coeff["ln_age_sbp_untreated"] * ln_sbp * ln_age
#         )
#         linear_predictor = (
#             coeff["ln_age"] * ln_age
#             + coeff["ln_tc"] * ln_tc
#             + coeff["ln_hdl"] * ln_hdl
#             + coeff["ln_age_hdl"] * ln_age * ln_hdl
#             + sbp_term
#             + sbp_age_term
#             + coeff["smoker"] * smoker_int
#             + coeff["diabetic"] * diabetic_int
#         )
#     elif not race_african_american and sex == "female":
#         # Non-African American Female
#         sbp_term = coeff["ln_sbp_treated"] * ln_sbp * htn_treat_int + coeff[
#             "ln_sbp_untreated"
#         ] * ln_sbp * (1 - htn_treat_int)
#         linear_predictor = (
#             coeff["ln_age"] * ln_age
#             + coeff["ln_age_squared"] * (ln_age**2)
#             + coeff["ln_tc"] * ln_tc
#             + coeff["ln_age_tc"] * ln_age * ln_tc
#             + coeff["ln_hdl"] * ln_hdl
#             + coeff["ln_age_hdl"] * ln_age * ln_hdl
#             + sbp_term
#             + coeff["smoker"] * smoker_int
#             + coeff["ln_age_smoker"] * ln_age * smoker_int
#             + coeff["diabetic"] * diabetic_int
#         )
#     elif race_african_american and sex == "male":
#         # African American Male
#         sbp_term = coeff["ln_sbp_treated"] * ln_sbp * htn_treat_int + coeff[
#             "ln_sbp_untreated"
#         ] * ln_sbp * (1 - htn_treat_int)
#         linear_predictor = (
#             coeff["ln_age"] * ln_age
#             + coeff["ln_tc"] * ln_tc
#             + coeff["ln_hdl"] * ln_hdl
#             + sbp_term
#             + coeff["smoker"] * smoker_int
#             + coeff["diabetic"] * diabetic_int
#         )
#     else:
#         # Non-African American Male
#         sbp_term = coeff["ln_sbp_treated"] * ln_sbp * htn_treat_int + coeff[
#             "ln_sbp_untreated"
#         ] * ln_sbp * (1 - htn_treat_int)
#         linear_predictor = (
#             coeff["ln_age"] * ln_age
#             + coeff["ln_tc"] * ln_tc
#             + coeff["ln_age_tc"] * ln_age * ln_tc
#             + coeff["ln_hdl"] * ln_hdl
#             + coeff["ln_age_hdl"] * ln_age * ln_hdl
#             + sbp_term
#             + coeff["smoker"] * smoker_int
#             + coeff["ln_age_smoker"] * ln_age * smoker_int
#             + coeff["diabetic"] * diabetic_int
#         )

#     # ASCVD risk calculation
#     risk = 1 - (baseline_s010 ** math.exp(linear_predictor - mean_xb))
#     # Risk is returned as a decimal (e.g., 0.07 = 7% 10-year risk)
#     return risk
