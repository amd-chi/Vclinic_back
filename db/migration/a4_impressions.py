from db.migration.base import MigrationBase
from patient.models.patient_models import Patient
from visit.models.history_models import (
    MedicalImpression,
    PatientImpressionItem,
)
from django.db import transaction


class DBMigration(MigrationBase):
    def __init__(self):
        super().__init__()

    def import_impressions_titles(self):
        rows = self.query(
            'SELECT distinct imp from imp where imp not like "%,%" and imp != ""'
        )
        inserted = 0
        lenr = len(rows)
        print(lenr)
        with transaction.atomic():
            for row in rows:
                if "," not in row[0]:
                    if MedicalImpression.objects.filter(name=row[0]).exists():
                        continue
                    impression = MedicalImpression()
                    impression.name = row[0]
                    impression.save()
                inserted += 1
                self.print_progress(inserted, len(row), lenr)

        print("done imported {} impressions".format(inserted))

    def import_impressions_titles_containing_comma(self):
        rows = self.query('SELECT distinct imp from imp where imp like "%,%" != ""')
        inserted = 0
        with transaction.atomic():
            for row in rows:
                impList = [imp.replace(" ", "") for imp in row[0].split(",")]
                for imp in impList:
                    if MedicalImpression.objects.filter(name=imp).exists():
                        continue
                    impression = MedicalImpression()
                    impression.name = imp
                    impression.save()
                    inserted += 1

        print("done imported {} impressions".format(inserted))

    def import_impressions(self):
        rows = self.query(
            'SELECT idnum, date, group_concat(imp) as imps FROM imp where idnum != "" and date != "" and imp != "" and imp not like "%,%" group by idnum, date order by date asc'
        )
        inserted = 0
        ignored_groups = 0
        lenr = len(rows)
        with transaction.atomic(), open("db/migration/logs/4.log", "w") as f:
            for row in rows:
                date = self.correct_date_system(row[1])
                gregorian_date = self.convert_persian_date(date)
                try:
                    patient = Patient.objects.get(id=row[0])
                except Exception:
                    ignored_groups += 1
                    f.write(f"patient not found: {row}")
                    continue
                if PatientImpressionItem.objects.filter(
                    patient=patient, date=gregorian_date
                ).exists():
                    continue
                impressionTitles = row[2]
                impressionTitles = impressionTitles.split(",")
                impTitles = []
                for title in impressionTitles:
                    try:
                        impTitles.append(
                            MedicalImpression.objects.get_or_create(name=title)
                        )
                    except Exception:
                        continue

                for impTitle, _ in impTitles:
                    impression = PatientImpressionItem()
                    impression.patient = patient
                    impression.impression = impTitle
                    impression.date = gregorian_date
                    impression.save()

                inserted += len(impTitles)
                self.print_progress(inserted, lenr)
        print(f"done imported {inserted} impression items | {ignored_groups} ignored")


# a = DBMigration()
# a.import_impressions_titles()
# a.import_impressions_titles_containing_comma()
# a.import_impressions()
