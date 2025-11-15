from db.migration.base import MigrationBase
from medicines.models import Medicine
from patient.models.patient_models import Patient
from visit.models.medicine_models import (
    MedicineAmount,
    MedicineInstruction,
    MedicinePrescriptionGroup,
    MedicinePrescriptionItem,
)
from datetime import datetime
from django.db import transaction


class Migration(MigrationBase):
    def __init__(self):
        super().__init__()
        self.instructions = MedicineInstruction.objects.all()
        self.amount_other = MedicineAmount.objects.first()

    def import_drugs(self):
        rows = self.query(
            "SELECT distinct drug FROM vdrug where drug != '' and drug is not null;"
        )
        lenr = len(rows)
        added_drugs = 0
        for row in rows:
            if Medicine.objects.filter(name=row[0]).exists():
                continue
            med = Medicine()
            med.name = row[0]
            med.save()
            added_drugs += 1
            self.print_progress(added_drugs, lenr)
        print(f"done imported {added_drugs} drugs")

    def map_dose(self, dose: str) -> str:
        if dose == "SD":
            return self.instructions.get(concept="یک بار در روز")
        elif dose == "BD":
            return self.instructions.get(concept="دو بار در روز")
        elif dose == "TDS":
            return self.instructions.get(concept="سه بار در روز")
        elif dose == "QID":
            return self.instructions.get(concept="چهار بار در روز")
        else:
            return self.instructions.get(concept="قبل از خواب")

    def import_medicine_prescs(self):
        self.query("update vdrug set date = '1300-01-01' where date = '0000-00-00'")
        self.query("update vdrug set date = '1399-10-30' where date = '1399-10-31'")
        # self.query(
        #     """update vdrug set remark=NULL WHERE drug != "" and idnum != "" and date != "" and remark = "" """
        # )
        rows = self.query(
            """ SELECT idnum, date,
                GROUP_CONCAT(CONCAT(drug, ":", dose) ORDER BY date ASC SEPARATOR "&") AS drugs_doses,
                GROUP_CONCAT(IFNULL(remark, "-") ORDER BY date ASC SEPARATOR "&") AS comments
                FROM vdrug
                WHERE drug != "" and idnum != "" and date != ""
                GROUP BY idnum, date
            ;"""
        )
        lenr = len(rows)
        print(lenr)
        with transaction.atomic(), open("db/migration/logs/3.log", "w") as log:
            inserted_groups = 0
            inserted_items = 0
            ignored_groups = 0

            for row in rows:
                try:
                    patient = Patient.objects.get(id=row[0])
                except Exception:
                    log.write(f"patient problem at: {row}\n")
                    ignored_groups += 1
                    continue

                presc = MedicinePrescriptionGroup()
                presc.patient = patient
                try:
                    date = self.convert_persian_date(self.correct_date_system(row[1]))
                except Exception:
                    log.write(f"date problem at: {row}\n")
                    ignored_groups += 1
                    continue

                if MedicinePrescriptionGroup.objects.filter(
                    patient=patient, date=date
                ).exists():
                    continue
                presc.save()
                presc.date = date
                presc.save()
                inserted_groups += 1

                drugs_doses = None if not row[2] else row[2].split("&")
                drug_comments = None if not row[3] else row[3].split("&")
                # print(drug_comments)
                # print(drugs_doses)
                for index, drug_dose in enumerate(drugs_doses):
                    drug, dose = drug_dose.split(":")
                    med, _ = Medicine.objects.get_or_create(name=drug)
                    presc_item = MedicinePrescriptionItem()
                    presc_item.group = presc
                    presc_item.medicine = med
                    presc_item.amount = self.amount_other
                    presc_item.instruction = self.map_dose(dose)
                    if drug_comments:
                        presc_item.comment = (
                            drug_comments[index]
                            if drug_comments[index] != "-"
                            else None
                        )
                    presc_item.usage = None
                    presc_item.quantity = 1
                    presc_item.save()
                    inserted_items += 1
                self.print_progress(inserted_groups, lenr, f" {ignored_groups} ignored")
        print(
            f"Done imported {inserted_groups} groups | {inserted_items} items | {ignored_groups} ignored groups"
        )

    def import_next_visits(self):
        rows = self.query(
            """
            SELECT idnum, MAX(next_d) AS latest_next_d
            FROM vdrug
            WHERE next_d != '' AND next_d IS NOT NULL AND next_d
            GROUP BY idnum;
            """
        )
        inserted = 0
        ignored = 0
        lenr = len(rows)
        with transaction.atomic(), open(
            "db/migration/logs/3.next_visit.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                (
                    patient_id,
                    next_visit_date,
                ) = row
                try:
                    patient = Patient.objects.get(id=patient_id)
                except Patient.DoesNotExist:
                    f.write(f"patient does not exsist: {row}\n")
                    ignored += 1
                    continue
                try:
                    visit_date = self.correct_date_system(next_visit_date)
                    visit_date = self.convert_persian_date(visit_date)
                except (ValueError, AttributeError):
                    f.write(f"date problem: {row}\n")
                    ignored += 1
                    continue
                date_obj = datetime.strptime(visit_date, "%Y-%m-%d").date()
                today = datetime.today().date()

                if date_obj < today:
                    continue

                patient.next_visit_date = visit_date
                patient.save()
                inserted += 1
                self.print_progress(inserted, lenr, ignored)

        print(f"done imported {inserted} next visits | {ignored} ignored")


# a = Migration()
# print(a.map_dose("SD"))
# print(a.correct_date("1403-3-9"))
# print(a.convert_persian_date("1399-10-31"))
# a.import_drugs()
# a.import_medicine_prescs()
# a.import_next_visits()
