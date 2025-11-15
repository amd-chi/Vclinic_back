from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from patient.models.patient_models import Patient


# class Clinic(models.Model):
#     name = models.CharField(max_length=150, unique=True)

#     def __str__(self):
#         return self.name


class UserManager(BaseUserManager):
    """Manager for users."""

    def normalize_phone_number(self, phone_number):
        """Normalize the phone number."""
        return phone_number.lower()

    def create_user(self, phone_number, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not phone_number:
            raise ValueError("User must have an phone number")
        user = self.model(
            phone_number=self.normalize_phone_number(phone_number), **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password):
        """Create and return a new superuser."""
        user = self.create_user(phone_number, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


ROLE_CHOICES = [
    ("admin", "admin"),
    ("doctor", "doctor"),
    ("secretary", "secretary"),
    ("patient", "patient"),
]


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    address = models.TextField(max_length=255)
    phone_number = models.CharField(max_length=15, unique=True)
    national_id = models.CharField(max_length=15)
    email = models.EmailField(max_length=255, null=True, blank=True)
    # avatar = models.FileField(upload_to="avatars/", null=True, blank=True)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="patient"
    )  # New role field

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    # clinic = models.ForeignKey(
    #     Clinic,
    #     on_delete=models.CASCADE,
    #     null=True,
    #     blank=True,
    #     related_name="users",
    # )

    USERNAME_FIELD = "phone_number"
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="user",
    )
    objects = UserManager()

    def __str__(self):
        return self.phone_number
