from django.apps import AppConfig


class MedicinesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "medicines"

    def ready(self):
        # Import and register the management command
        from .management.commands import generate_dummy_medicines
