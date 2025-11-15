from db.migration.base import MigrationBase
from patient.models.patient_models import Patient

from django.db import transaction

from visit.models.history_models import Story
from visit.models.insulin_prescription_models import (
    Insulin,
    InsulinPrescriptionGroup,
    InsulinPrescriptionItem,
)


class DBMigration(MigrationBase):
    def __init__(self):
        super().__init__()
        self.insulins = Insulin.objects.all()

    def get_insulin_model(self, name: str) -> Insulin:
        return self.insulins.get(name=name)

    def import_insulin(self):
        # self.query(
        #     'update const set date = "1397" where date = "4-96 & Re-visited 4-97"'
        # )

        rows = self.query(
            """SELECT idnum, date, morn1, morn1_d, morn2, morn2_d, lunch1,
                lunch1_d, lunch2, lunch2_d, night1, night1_d, night2, night2_d,
                5pm, 5pm_d
              FROM vdrug
              where idnum != '' and morn1 = 'Aspart' and (morn1_d != 0 or morn2_d != 0 or lunch1_d != 0 or lunch2_d != 0 or night1_d != 0 or night2_d != 0 or 5pm_d != 0)"""
        )

        inserted_items = 0
        inserted_groups = 0
        ignored = 0
        lenr = len(rows)
        with transaction.atomic(), open(
            "db/migration/logs/11_insulin.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                # print(f"{row[1]} converted to => {self.correct_date(row[1])}")
                (
                    patient_id,
                    date,
                    morning_short,
                    morn_short_dose,
                    morning_long,
                    morning_long_dose,
                    lunch_short,
                    lunch_short_dose,
                    lunch_long,
                    lunch_long_dose,
                    night_short,
                    night_short_dose,
                    night_long,
                    night_long_dose,
                    five_am_short,
                    five_am_short_dose,
                ) = row

                try:
                    visit_date = self.correct_date_system(date)
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
                if InsulinPrescriptionGroup.objects.filter(
                    patient=patient, date=visit_date
                ).exists():
                    continue

                ins_group = InsulinPrescriptionGroup(
                    patient=patient,
                )
                ins_group.save()
                ins_group.date = visit_date
                ins_group.save()

                if morn_short_dose:
                    try:
                        insulin = self.get_insulin_model(morning_short)
                    except Insulin.DoesNotExist:
                        f.write(f"insulin does not exsist: {row}\n")
                        ignored += 1
                    ins_item = InsulinPrescriptionItem(
                        insulin=insulin,
                        meal="Morning",
                        dose=morn_short_dose,
                        group=ins_group,
                    )
                    ins_item.save()
                    inserted_items += 1
                if morning_long_dose:
                    try:
                        insulin = self.get_insulin_model(morning_long)
                    except Insulin.DoesNotExist:
                        f.write(f"insulin does not exsist: {row}\n")
                        ignored += 1
                    ins_item = InsulinPrescriptionItem(
                        insulin=insulin,
                        meal="Morning",
                        dose=morning_long_dose,
                        group=ins_group,
                    )
                    ins_item.save()
                    inserted_items += 1
                if lunch_short_dose:
                    try:
                        insulin = self.get_insulin_model(lunch_short)
                    except Insulin.DoesNotExist:
                        f.write(f"insulin does not exsist: {row}\n")
                        ignored += 1
                    ins_item = InsulinPrescriptionItem(
                        insulin=insulin,
                        meal="Lunch",
                        dose=lunch_short_dose,
                        group=ins_group,
                    )
                    ins_item.save()
                    inserted_items += 1

                if lunch_long_dose:
                    try:
                        insulin = self.get_insulin_model(lunch_long)
                    except Insulin.DoesNotExist:
                        f.write(f"insulin does not exsist: {row}\n")
                        ignored += 1
                    ins_item = InsulinPrescriptionItem(
                        insulin=insulin,
                        meal="Lunch",
                        dose=lunch_long_dose,
                        group=ins_group,
                    )
                    ins_item.save()
                    inserted_items += 1
                if night_short_dose:
                    try:
                        insulin = self.get_insulin_model(night_short)
                    except Insulin.DoesNotExist:
                        f.write(f"insulin does not exsist: {row}\n")
                        ignored += 1
                    ins_item = InsulinPrescriptionItem(
                        insulin=insulin,
                        meal="Dinner",
                        dose=night_short_dose,
                        group=ins_group,
                    )
                    ins_item.save()
                    inserted_items += 1
                if night_long_dose:
                    try:
                        insulin = self.get_insulin_model(night_long)
                    except Insulin.DoesNotExist:
                        f.write(f"insulin does not exsist: {row}\n")
                        ignored += 1
                    ins_item = InsulinPrescriptionItem(
                        insulin=insulin,
                        meal="Dinner",
                        dose=night_long_dose,
                        group=ins_group,
                    )
                    ins_item.save()
                    inserted_items += 1
                if five_am_short_dose:
                    try:
                        insulin = self.get_insulin_model(five_am_short)
                    except Insulin.DoesNotExist:
                        f.write(f"insulin does not exsist: {row}\n")
                        ignored += 1
                    ins_item = InsulinPrescriptionItem(
                        insulin=insulin,
                        meal="5AM",
                        dose=five_am_short_dose,
                        group=ins_group,
                    )
                    ins_item.save()
                    inserted_items += 1
                inserted_groups += 1
                self.print_progress(inserted_groups, lenr, ignored)
        print(f"done imported {inserted_items} insulins | {ignored} ignored")

    def import_plans(self):
        # self.query(
        #     'update const set date = "1397" where date = "4-96 & Re-visited 4-97"'
        # )
        rows = self.query(
            'SELECT idnum, date, plan FROM vdrug where idnum != "" and plan != ""'
        )
        inserted = 0
        ignored = 0
        lenr = len(rows)
        found_items = 0
        with transaction.atomic(), open(
            "db/migration/logs/11_comments.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                (
                    patient_id,
                    date,
                    comment,
                ) = row
                if not comment:
                    continue
                try:
                    visit_date = self.correct_date_system(date)
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
                if Story.objects.filter(
                    patient=patient, date=visit_date, story__icontains=comment
                ).exists():
                    continue

                story, is_found = Story.objects.get_or_create(
                    patient=patient, date=visit_date
                )

                if is_found and story.story:
                    found_items += 1
                story.story = f"{comment}\n{story.story}"
                story.date = visit_date
                story.save()
                if not is_found:
                    story.date = visit_date
                    story.save()
                inserted += 1
                self.print_progress(inserted, lenr, ignored)

        print(
            f"done imported {inserted} story comments | {ignored} ignored | {found_items} found"
        )


# a = DBMigration()
# a.import_insulin()
# a.import_plans()
