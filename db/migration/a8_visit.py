from db.migration.base import MigrationBase
from patient.models.patient_models import Patient

from django.db import transaction

# from visit.models.history_models import ThyroidHistory
from visit.models.visit_models import Visit


class DBMigration(MigrationBase):
    def __init__(self):
        super().__init__()

    def import_visit(self):
        # self.query(
        #     'update const set date = "1397" where date = "4-96 & Re-visited 4-97"'
        # )
        rows = self.query(
            'SELECT idnum, year, month, day, paymentfee FROM visited where idnum != "" order by year, month, day'
        )
        inserted = 0
        ignored = 0
        lenr = len(rows)
        with transaction.atomic(), open(
            "db/migration/logs/8.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                # print(f"{row[1]} converted to => {self.correct_date(row[1])}")
                (patient_id, year, month, day, fee) = (
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    row[4],
                )
                try:
                    visit_date = self.correct_date_system(f"{year}-{month}-{day}")
                    visit_date = self.convert_persian_date(visit_date)
                except (ValueError, AttributeError):
                    f.write(f"date problem: {row}\n")
                    ignored += 1
                    continue
                try:
                    patient = Patient.objects.get(id=patient_id)

                except Patient.DoesNotExist:
                    f.write(f"patient does not exsist: {row}\n")
                    ignored += 1
                    continue
                if Visit.objects.filter(patient=patient, date=visit_date):
                    continue

                r = Visit(
                    patient=patient,
                    fee=fee if fee else 0,
                )
                r.save()
                r.date = visit_date
                r.save()

                inserted += 1
                self.print_progress(inserted, lenr, ignored)
        print(f"done imported {inserted} visit | {ignored} ignored")


# a = DBMigration()
# a.import_visit()
