from .middleware import get_current_database


class MultiTenantRouter:
    def db_for_read(self, model, **hints):
        # اپ‌های مشترک به دیتابیس پیش‌فرض هدایت شوند
        if model._meta.app_label in [
            "auth",
            "contenttypes",
            "sessions",
            "admin",
            "user",
        ]:
            return "default"

        # اپ‌های دیگر بر اساس کلینیک به دیتابیس مربوطه هدایت شوند
        clinic_db = get_current_database()
        return clinic_db if clinic_db else "default"

    def db_for_write(self, model, **hints):
        # اپ‌های مشترک به دیتابیس پیش‌فرض هدایت شوند
        if model._meta.app_label in [
            "auth",
            "contenttypes",
            "sessions",
            "admin",
            "user",
        ]:
            return "default"

        # اپ‌های دیگر بر اساس کلینیک به دیتابیس مربوطه هدایت شوند
        clinic_db = get_current_database()
        return clinic_db if clinic_db else "default"

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # فقط اپ‌های مشترک به دیتابیس پیش‌فرض مایگریت شوند
        if app_label in ["auth", "contenttypes", "sessions", "admin", "user"]:
            return db == "default"

        # اپ‌های دیگر به دیتابیس کلینیک‌ها مایگریت شوند
        return db != "default"
