from db.migration.base import MigrationBase
from patient.models.patient_models import Patient

from django.db import transaction

from visit.models.history_models import PatientHistoryBasic, Story


class DBMigration(MigrationBase):
    def __init__(self):
        super().__init__()

    def map_ampu(self, term):
        if term == "finger":
            return "Finger"
        elif term == "Below":
            return "Below-Knee"
        elif term == "Ante":
            return "Ante-Knee"
        elif term == "Sims":
            return "Sims"
        raise ValueError("AMPU PROBLEM")

    def map_ihd(self, term):
        """
        Angiography
        Stent
        CABG"""
        if term == "select":
            return None
        elif term == "Angiography":
            return "Angiography"
        elif term == "Stent":
            return "STENT"
        elif term == "CABG":
            return "CABG"
        raise ValueError("IHD PROBLEM")

    def map_smok(self, term):
        """ """
        if term == "select":
            return None
        elif term == "Active":
            return "Active"
        elif term == "Ex":
            return "Ex-smoker"
        elif term == "passive":
            return "Passive"
        raise ValueError(f"SMOKE PROBLEM {term}")

    def import_features(self):
        # self.query(
        #     'update const set date = "1397" where date = "4-96 & Re-visited 4-97"'
        # )
        rows = self.query(
            'SELECT idnum,retino, ihd, eye, ampu,gdm, thysu,op,fx,esrd,alk, gal,htn,hlp,smok FROM pmh where idnum != "" and (retino != "select" or ihd != "select" or eye != "select" or ampu != "select-select" or gdm != "" or thysu != "" or op != "" or fx != "" or esrd != "" or alk != "" or gal != "" or htn != "" or hlp != "" or smok != "select")'
        )
        inserted = 0
        ignored = 0
        lenr = len(rows)
        with transaction.atomic(), open(
            "db/migration/logs/9.2.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                try:
                    # print(f"{row[1]} converted to => {self.correct_date(row[1])}")
                    (
                        patient_id,
                        retino,
                        ihd,
                        eye,
                        ampu,
                        gdm,
                        thysu,
                        op,
                        fx,
                        esrd,
                        alk,
                        gal,
                        htn,
                        hlp,
                        smok,
                    ) = (
                        row[0],
                        row[1] if row[2] != "select" else None,
                        row[2],
                        row[3] if row[3] != "select" else None,
                        row[4].split("-"),
                        row[5] == "on",
                        row[6] == "on",
                        row[7] == "on",
                        row[8] == "on",
                        row[9] == "on",
                        row[10] == "on",
                        row[11] == "on",
                        row[12] == "on",
                        row[13] == "on",
                        row[14],
                    )
                    try:
                        patient = Patient.objects.get(id=patient_id)
                    except Patient.DoesNotExist:
                        f.write(f"patient does not exsist: {row}\n")
                        ignored += 1
                        continue
                    (pat_his_bas, hb_found) = PatientHistoryBasic.objects.get_or_create(
                        patient=patient
                    )

                    if retino is not None:
                        pat_his_bas.retino = retino
                    if ihd is not None:
                        pat_his_bas.ihd = self.map_ihd(ihd)
                    # if eye is not None:
                    #     pat_his_bas.eye_laser = eye
                    if ampu[0] != "select":
                        pat_his_bas.right_amputation = self.map_ampu(ampu[0])
                    if ampu[1] != "select":
                        pat_his_bas.left_amputation = self.map_ampu(ampu[1])
                    if gdm is not None:
                        pat_his_bas.gdm = gdm
                    if thysu is not None:
                        pat_his_bas.thyroid_surgery = thysu
                    if op is not None:
                        pat_his_bas.osteoprosis = op
                    # if fx is not None:
                    #   pat_his_bas.fracture = fx
                    if esrd is not None:
                        pat_his_bas.esrd = esrd

                    if smok is not None:
                        pat_his_bas.smoking = self.map_smok(smok)
                    if htn is not None:
                        pat_his_bas.htn = htn
                    if hlp is not None:
                        pat_his_bas.hlp = hlp

                    pat_his_bas.save()
                    inserted += 1
                    self.print_progress(inserted, lenr, ignored)
                except Exception:
                    print("================================")
                    print(row)
        print(f"done imported {inserted} features | {ignored} ignored")

    def import_stories(self):
        # self.query(
        #     'update const set date = "1397" where date = "4-96 & Re-visited 4-97"'
        # )
        #             if alk is not None:
        #                 pat_his_bas.alcohol = alk
        #             if gal is not None:
        #                 pat_his_bas.galactoreha = gal
        rows = self.query(
            'SELECT idnum, date, story FROM pmh where idnum != "" and story != "" and story is not null'
        )
        inserted = 0
        ignored = 0
        lenr = len(rows)
        found_items = 0
        with transaction.atomic(), open(
            "db/migration/logs/9.1.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                (
                    patient_id,
                    date,
                    comment,
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

                if Story.objects.filter(
                    patient=patient, date=visit_date, story__icontains=comment
                ).exists():
                    continue

                (story, is_found) = Story.objects.get_or_create(
                    patient=patient, date=visit_date
                )

                if is_found:
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
            f"done imported {inserted} stories | {ignored} ignored | {found_items} found"
        )


# a = DBMigration()
# a.import_features()
# a.import_stories()
