from db.migration.base import MigrationBase
from patient.models.patient_models import Patient

from django.db import transaction

from visit.models.history_models import ThyroidHistory


class DBMigration(MigrationBase):
    def __init__(self):
        super().__init__()

    def mng_right_left_map(self, term):
        if term == "Larger than":
            return "Right > Left"
        elif term == "Smaller than":
            return "Left > Right"
        elif term == "Equal":
            return "Equal"
        raise ValueError("MNG RIGHT LEFT PROBLEM")

    def import_thyroid(self, ids: list = None):
        # self.query(
        #     'update const set date = "1397" where date = "4-96 & Re-visited 4-97"'
        # )
        rows = self.query(
            'SELECT idnum, date, normal, sguw, sgun, mngw, mngc, mnglr,mngll,thtomy FROM examin where idnum != "" and date != "" order by date asc'
        )
        inserted = 0
        ignored = 0
        lenr = len(rows)
        with transaction.atomic(), open(
            "db/migration/logs/7.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                # print(f"{row[1]} converted to => {self.correct_date(row[1])}")
                props = {}
                (
                    patient_id,
                    result_date,
                    props["is_normal"],
                    props["simple_goiter_gram"],
                    props["simple_goiter_times_normal"],
                    props["mng_gram"],
                    props["mng_right_left_term"],
                    props["mnglr"],
                    props["mngll"],
                    props["thtomy"],
                ) = (
                    row[0],
                    row[1],
                    row[2] == "on",
                    row[3],
                    row[4],
                    row[5],
                    row[6],
                    row[7],
                    row[8],
                    row[9],
                )
                try:
                    try:
                        result_date = self.correct_date_system(result_date)
                        result_date = self.convert_persian_date(result_date)
                    except (ValueError, AttributeError) as e:
                        print(e)
                        f.write(f"date problem: {row}\n")
                        ignored += 1
                        continue
                    try:
                        patient = Patient.objects.get(id=patient_id)

                    except Patient.DoesNotExist:
                        f.write(f"patient does not exsist: {row}\n")
                        ignored += 1
                        continue

                    if ThyroidHistory.objects.filter(
                        patient=patient, date=result_date
                    ).exists():
                        continue
                    if props["mng_right_left_term"]:
                        props["mng_right_left"] = self.mng_right_left_map(
                            props["mng_right_left_term"]
                        )

                    if props["mnglr"] != "*":
                        mnglr_list = props["mnglr"].replace("**", "*").split("*")
                        props["mng_largest_right_size_width"] = mnglr_list[0]
                        props["mng_largest_right_size_height"] = mnglr_list[1]
                    if props["mngll"] != "*":
                        mngll_list = props["mngll"].split("*")
                        props["mng_largest_left_size_width"] = mngll_list[0]
                        props["mng_largest_left_size_height"] = mngll_list[1]
                    if props["thtomy"] != "":
                        props["thyroidectomy"] = props["thtomy"]

                    r = ThyroidHistory(
                        patient=patient,
                        is_normal=props.get("is_normal"),
                        simple_goiter_gram=props.get("simple_goiter_gram"),
                        # simple_goiter_times_normal=props.get(
                        #     "simple_goiter_times_normal"
                        # ),
                        mng_gram=props.get("mng_gram"),
                        mng_right_left=props.get("mng_right_left"),
                        mng_largest_right_size_width=props.get(
                            "mng_largest_right_size_width"
                        ),
                        mng_largest_right_size_height=props.get(
                            "mng_largest_right_size_height"
                        ),
                        mng_largest_left_size_width=props.get(
                            "mng_largest_left_size_width"
                        ),
                        mng_largest_left_size_height=props.get(
                            "mng_largest_left_size_height"
                        ),
                        thyroidectomy=props.get("thyroidectomy"),
                    )
                    r.save()
                    r.date = result_date
                    r.save()

                    inserted += 1
                    self.print_progress(inserted, lenr, ignored)

                except Exception:
                    print("============================================")
                    print(row)
                    raise Exception("e")

        print(f"done imported {inserted} thryoid | {ignored} ignored")


# a = DBMigration()

# a.import_thyroid()
