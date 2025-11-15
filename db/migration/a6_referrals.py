from db.migration.base import MigrationBase
from patient.models.patient_models import Patient

from django.db import transaction

from referral_services.models import ReferralDoctor


class DBMigration(MigrationBase):
    def __init__(self):
        super().__init__()

    def import_refferals(self, ids: list = None):
        # self.query(
        #     'update const set date = "1397" where date = "4-96 & Re-visited 4-97"'
        # )
        rows = self.query(
            'SELECT idnum, date, reg_date, subject, dr, result FROM cons where idnum != "" and reg_date != "" and result != "" order by date asc'
        )
        inserted = 0
        ignored = 0
        lenr = len(rows)
        with transaction.atomic(), open(
            "db/migration/logs/6.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                # print(f"{row[1]} converted to => {self.correct_date(row[1])}")
                patient_id, result_date, referral_date, comment, result = (
                    row[0],
                    row[1],
                    row[2],
                    str(row[3]) + " | " + str(row[4]),
                    row[5],
                )
                try:
                    try:
                        result_date = self.convert_persian_date(
                            self.correct_date_system(result_date)
                        )
                    except (ValueError, AttributeError):
                        f.write(f"date problem: {row}\n")
                        ignored += 1
                        continue
                    try:
                        referral_date = self.correct_date_system(referral_date)
                        referral_date = self.convert_persian_date(referral_date)
                    except (ValueError, AttributeError):
                        referral_date = result_date

                    try:
                        patient = Patient.objects.get(id=patient_id)
                    except Patient.DoesNotExist:
                        f.write(f"patient does not exsist: {row}\n")
                        ignored += 1
                        continue
                    if ReferralDoctor.objects.filter(
                        patient=patient, referral_date=referral_date
                    ):
                        continue
                    r = ReferralDoctor(
                        patient=patient,
                        referral_date=referral_date,
                        result_date=result_date,
                        comment=comment,
                        result=result,
                    )
                    r.save()
                    r.referral_date = referral_date
                    r.save()

                    inserted += 1
                    self.print_progress(inserted, lenr, ignored)

                except Exception:
                    print("============================================")
                    print(row)
                    raise Exception("e")

        print(f"done imported {inserted} referral | {ignored} ignored")


# a = DBMigration()
# a.import_refferals()
