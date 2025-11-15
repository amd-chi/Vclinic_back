from db.migration.base import MigrationBase
from patient.models.patient_models import Patient
from medical_imaging.models import (
    MedicalImagingCenter,
    MedicalImagingInsurance,
    MedicalImagingResult,
)
from django.db import transaction


class DBMigration(MigrationBase):
    def __init__(self):
        super().__init__()

    def import_imaging_centers(self):
        rows = self.query('SELECT distinct center from para where center != ""')
        inserted = 0
        print(len(rows))
        with transaction.atomic():
            for row in rows:
                if MedicalImagingCenter.objects.filter(name=row[0]).exists():
                    continue
                center = MedicalImagingCenter()
                center.name = row[0]
                center.save()
                inserted += 1

        print("done imported {} imaging centers".format(inserted))

    def import_imaging_titles(self):
        rows = self.query("select distinct type subject from para where type != ''")
        lenr = len(rows)
        for i, row in enumerate(rows):
            if MedicalImagingInsurance.objects.filter(name=row[0]).exists():
                continue
            m = MedicalImagingInsurance()
            m.name = row[0]
            m.save()
            self.print_progress(i, lenr)
        print(f"inserted {lenr} titles")

    def import_imaging_results(self, ids: list = None):
        self.query('update para set date = "1396" where date = "1393 to 96"')
        self.query('update para set date = "1397" where date = "27/3/397"')
        self.query('update para set date = "1300" where date = "5-9"')
        self.query('update para set date = "1398-12-03" where date = "10 june 2019"')
        self.query(
            'update para set date = "1397-06-29" where date = "20 December 2018"'
        )
        self.query('update para set date = "1398-03-27" where date = "17 june 2019"')
        self.query(
            'update para set date = "1397" where date = "4-96 & Re-visited 4-97"'
        )
        rows = self.query(
            'SELECT idnum, date, type, subject, result, center FROM para where idnum != "" and date != "" and type != "" and result != "" order by date'
        )
        inserted = 0
        ignored_groups = 0
        lenr = len(rows)
        with transaction.atomic(), open(
            "db/migration/logs/5.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                # print(f"{row[1]} converted to => {self.correct_date(row[1])}")
                try:
                    try:
                        date = self.correct_date_system(row[1])
                        gregorian_date = self.convert_persian_date(date)
                    except ValueError:
                        f.write(f"{row}\n")
                        ignored_groups += 1
                        continue
                    try:
                        patient = Patient.objects.get(id=row[0])
                    except Patient.DoesNotExist:
                        f.write(f"patient does not exsist: {row}\n")
                        ignored_groups += 1
                        continue
                    if MedicalImagingResult.objects.filter(
                        patient=patient, date=gregorian_date
                    ).exists():
                        continue
                    imaging_result = MedicalImagingResult()
                    imaging_result.patient = patient
                    imaging_result.date = gregorian_date
                    result_type = row[2]
                    result_subject = row[3]
                    result_comment = row[4]
                    if row[5]:
                        center, _ = MedicalImagingCenter.objects.get_or_create(
                            name=row[5]
                        )
                        imaging_result.imaging_center = center
                    imaging_result.comment = (
                        result_subject + " - " if result_subject else ""
                    ) + result_comment
                    imaging, _ = MedicalImagingInsurance.objects.get_or_create(
                        name=result_type
                    )
                    imaging_result.imaging = imaging
                    imaging_result.save()
                    inserted += 1
                    self.print_progress(inserted, lenr, ignored_groups)

                except Exception:
                    print("============================================")
                    print(row)
                    raise Exception("e")

        print(f"done imported {inserted} imagings | {ignored_groups} ignored")


# a = DBMigration()
# # a.import_imaging_centers()
# a.import_imaging_titles()
# a.import_imaging_results()
