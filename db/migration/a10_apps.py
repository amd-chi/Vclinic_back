from db.migration.base import MigrationBase
from patient.models.appointment_models import Appointment
from patient.models.patient_models import Patient
from django.db import transaction
from django.utils import timezone
from datetime import datetime


class DBMigration(MigrationBase):
    def __init__(self):
        super().__init__()
        self.months_dict = {
            "فروردین": "01",
            "اردیبهشت": "02",
            "خرداد": "03",
            "تیر": "04",
            "مرداد": "05",
            "شهریور": "06",
            "مهر": "07",
            "آبان": "08",
            "آذر": "09",
            "دی": "10",
            "بهمن": "11",
            "اسفند": "12",
        }

    def map_status(self, term: str) -> str:
        if term == "n":
            return "Confirmed"
        elif term == "p":
            return "Canceld_by_patient"
        elif term == "u":
            return "Canceled_by_secretary"
        raise ValueError(f"STATUS PROBLEM {term}")

    def _import(self):
        self.query("""
        DELETE FROM app
        WHERE place NOT REGEXP '^[0-9]+$' or `year` = '' or month = '' or day = '' or `year` < 1360 or deleted = 'o';            
                   
                   """)
        self.query("""
        update app
        set deleted = "n" where deleted = "v";            
                   
                   """)
        rows = self.query(
            "SELECT place,year, month, day,hour, min, date, deleted,canc_date FROM app"
        )
        inserted = 0
        ignored = 0
        lenr = len(rows)
        with transaction.atomic(), open(
            "db/migration/logs/10.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                (
                    patient_id,
                    year,
                    month,
                    day,
                    hour,
                    min,
                    created_at,
                    deleted,
                    canc_time,
                ) = (
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                )
                try:
                    app_date_jalali = self.correct_date_system(
                        f"{year}-{self.months_dict[month]}-{day}"
                    )
                    app_date_gregorian = self.convert_persian_date(app_date_jalali)
                    year, month, day = app_date_gregorian.split("-")
                    if not min:
                        min = "00"
                    if not hour:
                        hour = "00"
                    # فرض کنید که `naive_datetime` یک شیء datetime نا‌آگاه است
                    naive_datetime = datetime(
                        year=int(year),
                        month=int(month),
                        day=int(day),
                        hour=int(hour),
                        minute=int(min),
                    )
                    aware_datetime = timezone.make_aware(naive_datetime)
                except (ValueError, AttributeError) as e:
                    f.write(f"date problem: {naive_datetime} {str(e)} | {row}\n")
                    ignored += 1
                    continue

                try:
                    patient = Patient.objects.get(id=patient_id)
                except Patient.DoesNotExist:
                    f.write(f"patient does not exsist: {row}\n")
                    ignored += 1
                    continue

                if Appointment.objects.filter(
                    patient=patient, datetime=aware_datetime
                ).exists():
                    continue

                r = Appointment(
                    patient=patient,
                    datetime=aware_datetime,
                    # created_at=created_at,
                    status=self.map_status(deleted),
                    canceled_at=self.convert_persian_date(
                        self.correct_date_system(canc_time)
                    )
                    if canc_time
                    else None,
                )
                r.save()

                inserted += 1
                self.print_progress(inserted, lenr, ignored)
        print(f"done imported {inserted} visit | {ignored} ignored")


# a = DBMigration()
# a._import()
