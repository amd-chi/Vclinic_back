# app_messages/admin.py
from django.contrib import admin
from .models import AppMessage


@admin.register(AppMessage)
class AppMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "short_content", "created_at", "updated_at", "read_count")
    search_fields = ("content",)
    list_filter = ("created_at",)

    filter_horizontal = ("users_read",)  # ویجت قشنگ‌تر برای انتخاب کاربرها

    def short_content(self, obj):
        # برای اینکه توی لیست، متن کوتاه نشون بده
        return (obj.content[:50] + "...") if len(obj.content) > 50 else obj.content

    short_content.short_description = "Content"

    def read_count(self, obj):
        return obj.users_read.count()

    read_count.short_description = "Users Read"
