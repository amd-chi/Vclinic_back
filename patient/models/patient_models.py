from django.db import models

from datetime import datetime

GENDER_CHOICES = (("M", "Male"), ("F", "Female"), ("O", "Other"))

BlOOD_TYPES = (
    ("A+", "A+"),
    ("A-", "A-"),
    ("B+", "B+"),
    ("B-", "B-"),
    ("AB+", "AB+"),
    ("AB-", "AB-"),
    ("O+", "O+"),
    ("O-", "O-"),
)

EDUCATION_CHOICES = (
    ("illiterate", "illiterate"),
    ("elementary", "elementary"),
    ("middle_school", "middle_school"),
    ("high_school", "high_school"),
    ("diploma", "diploma"),
    ("associate", "associate"),
    ("bachelor", "bachelor"),
    ("master", "master"),
    ("phd", "phd"),
)

OCCUPATION_CHOICES = (
    ("employee", "employee"),
    ("self_employed", "self_employed"),
    ("student", "student"),
    ("unemployed", "unemployed"),
    ("retired", "retired"),
    ("housewife", "housewife"),
    ("other", "other"),
)

# INSURANCE_CHOICES = {
#     ("tamin", "tamin"),
#     ("salamat", "salamat"),
#     ("military", "military"),
#     ("bank", "bank"),
#     ("azad", "azad"),
#     ("sedasima", "sedasima"),
#     ("shahrdari", "shahrdari"),
# }


class Patient(models.Model):
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    first_name = models.CharField(max_length=150, null=True, blank=True)
    last_name = models.CharField(max_length=150, null=True, blank=True)
    address = models.TextField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    telephone = models.CharField(max_length=255, blank=True, null=True)
    national_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    refferal_reason = models.TextField(max_length=255, null=True, blank=True)
    blood_group = models.CharField(
        max_length=3, choices=BlOOD_TYPES, blank=True, null=True
    )
    referer = models.CharField(max_length=255, blank=True, null=True)
    education = models.CharField(
        max_length=255, choices=EDUCATION_CHOICES, blank=True, null=True
    )
    occupation = models.CharField(max_length=255, blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)
    insurance_company = models.CharField(max_length=255, blank=True, null=True)
    # avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    next_visit_date = models.DateField(blank=True, null=True)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_patients",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.full_name()

    def age(self):
        if not self.birth_date:
            return None
        return (datetime.now().date() - self.birth_date).days // 365

    def full_name(self):
        return self.first_name + " " + self.last_name

    class Meta:
        indexes = [
            models.Index(fields=["national_id", "phone_number"]),
        ]


class PreRegisterPatient(models.Model):
    first_name = models.CharField(max_length=512, null=True, blank=True)
    last_name = models.CharField(max_length=512, null=True, blank=True)
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    national_id = models.CharField(max_length=20, null=True, blank=True)
