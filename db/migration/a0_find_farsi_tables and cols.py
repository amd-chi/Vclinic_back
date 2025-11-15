from db.migration.base import MigrationBase
from patient.models import Patient
from persiantools.jdatetime import JalaliDate
from django.db import transaction


class DBMigration(MigrationBase):
    def __init__(self):
        super().__init__("root", "", "health-two-oct")

    def find(self, table_name):
        # استفاده از SHOW COLUMNS به جای PRAGMA برای دریافت اطلاعات ستون‌ها در MySQL/MariaDB
        cols = self.query(f"SHOW COLUMNS FROM {table_name};")

        # ساخت کوئری
        query = f"SELECT * FROM {table_name} WHERE " + " OR ".join(
            [f"{col[0]} LIKE '%Ø%'" for col in cols]
        )

        print(query)


a = DBMigration()
a.find("para")
