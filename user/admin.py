from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from user import models


# Register your models here.
class UserAdmin(BaseUserAdmin):
    """Define the admin pages for users."""

    ordering = ["id"]
    list_display = ["phone_number", "first_name", "last_name", "role"]
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (
            _("Personal Info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "address",
                    "national_id",
                )
            },
        ),
        (
            _("Permissions"),
            {"fields": ("is_active", "is_superuser", "is_staff", "role")},
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    readonly_fields = ["last_login"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "first_name",
                    "last_name",
                    "national_id",
                    "phone_number",
                    "password1",
                    "password2",
                    "address",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "role",
                ),
            },
        ),
    )


admin.site.register(models.User, UserAdmin)
