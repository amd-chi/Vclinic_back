# حالا می‌توانید به صورت مطلق وارد کنید
from db.migration.base import MigrationBase
from medical_tests.models import (
    MetricUnit,
    TestMetric,
    TestResultGroup,
    TestResultItem,
    Laboratory,
)
from patient.models.patient_models import Patient
from django.db import transaction

# connect to mysql db and read data
import re


class DBMigration(MigrationBase):
    def __init__(self):
        super().__init__()
        first_unit = MetricUnit.objects.first()
        if first_unit:
            self.unit = MetricUnit.objects.first()
        else:
            mu = MetricUnit(name="None")
            mu.save()
            self.unit = mu

    def import_tests_result_groups(self, quartile):
        # delete records
        self.query(
            "DELETE FROM v_test WHERE idnum = '' OR idnum IS NULL OR date IS NULL OR lab = '' OR lab IS NULL or t_name IS NULL or t_name = '' or t_value IS NULL or t_value = '';"
        )
        self.query("""
        update v_test set t_value = '-' where t_value = '_';
                           """)
        rows = self.query(
            f"""
            SELECT Quartile, idnum, date, lab, 
                GROUP_CONCAT(DISTINCT t_name ORDER BY date ASC) AS metrics
            FROM (
                SELECT NTILE(4) OVER (ORDER BY id) AS Quartile,
                    id, idnum, date, lab, t_name
                FROM v_test
                WHERE lab IS NOT NULL AND lab != ''
            ) AS QuartileData
            GROUP BY Quartile, idnum, date, lab
            HAVING Quartile = {quartile};
            """
        )

        lenr = len(rows)
        print(lenr)
        added_groups = 0
        added_items = 0
        ignored_items = 0
        ignored_groups = 0

        with transaction.atomic(), open(
            f"db/migration/logs/2.{quartile}.log", "w", encoding="utf-8"
        ) as f:
            for row in rows:
                if not row[1] or not row[1] or not row[3]:
                    f.write(f"{row}\n")
                    ignored_groups += 1
                    continue

                date = self.convert_persian_date(row[2])
                lab, _ = Laboratory.objects.get_or_create(name=row[3])
                testGroup = TestResultGroup()
                try:
                    patient = Patient.objects.get(id=row[1])
                except Patient.DoesNotExist:
                    ignored_groups += 1
                    f.write(f"patient problem{row}")
                    continue

                if TestResultGroup.objects.filter(
                    patient=patient, laboratory=lab, date=date
                ).exists():
                    continue

                testGroup.patient = patient
                testGroup.laboratory = lab
                testGroup.date = date
                testGroup.save()

                added_groups += 1
                items = self.query(
                    'SELECT t_name, t_value, nlr FROM v_test WHERE idnum = "{}" AND date = "{}" and t_value != ""'.format(
                        row[1], row[2]
                    )
                )
                for item in items:
                    testItem = TestResultItem()
                    testItem.group = testGroup
                    if not item[0]:
                        continue
                    try:
                        # استفاده از regex برای حذف هرچیزی جز عدد و تبدیل به float
                        numeric_value = re.sub(r"[^\d.]", "", item[1])
                        if numeric_value:
                            # testItem.raw_value = float(
                            #     numeric_value
                            # )  # اگر عددی بود در value ذخیره شود
                            testItem.value = float(
                                numeric_value
                            )  # اگر عددی بود در value ذخیره شود
                        else:
                            testItem.comment = item[
                                1
                            ]  # اگر عددی نبود در comment ذخیره شود

                        # چک کردن مقدار item[2] برای reference_range
                        if item[2]:
                            testItem.reference_range = float(
                                re.sub(r"[^\d.]", "", item[2])
                            )
                    except ValueError:
                        # در صورت بروز خطا در تبدیل به float، می‌توانید مدیریت خطا را اینجا اضافه کنید
                        testItem.comment = item[1]
                    try:
                        metric = TestMetric.objects.get(name=item[0])
                        testItem.metric = metric
                    except TestMetric.DoesNotExist:
                        metric = TestMetric.objects.create(name=item[0], unit=self.unit)
                        testItem.metric = metric
                    testItem.save()
                    added_items += 1
                self.print_progress(
                    added_groups,
                    len(rows),
                    f"ignored items: {ignored_items}/ groups: {ignored_groups}",
                )
            print(
                f"DONE importing test result groups {added_groups} inserted, {added_items} items inserted. Ignored items: {ignored_items}, ignored groups: {ignored_groups}"
            )

    def import_metrics(self):
        rows = self.query('SELECT distinct t_name from v_test where t_name != ""')
        metrics_added = 0
        with transaction.atomic():
            for row in rows:
                if TestMetric.objects.filter(name=row[0]).exists():
                    continue
                metric = TestMetric()
                metric.name = row[0]
                metric.unit = self.unit
                metric.save()
                metrics_added += 1
                self.print_progress(metrics_added, len(rows))
        print(f"successfully added {metrics_added}")

    def import_labs(self):
        labs_added = 0
        with transaction.atomic():
            rows = self.query('SELECT distinct lab from v_test where lab != ""')
            for row in rows:
                if Laboratory.objects.filter(name=row[0]).exists():
                    continue
                lab = Laboratory()
                lab.name = row[0]
                lab.save()
                labs_added += 1
                self.print_progress(labs_added, len(rows))
        print(f"successfully added {labs_added} labs")


# a = DBMigration()
# a.import_labs()
# a.import_metrics()
# a.import_tests_result_groups(quartile=1)
# a.import_tests_result_groups(quartile=2)
# a.import_tests_result_groups(quartile=3)
# a.import_tests_result_groups(quartile=4)
