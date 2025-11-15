from django.core.management.base import BaseCommand

from medical_tests.models import MetricUnit
from visit.models.medicine_models import MedicineRepeat


class Command(BaseCommand):
    help = "Imports some repeats it into MedicineRepeat model"

    def handle(self, *args, **kwargs):
        repeats = [
            {"repeatDaysId": 1, "repeatDaysCode": "1", "repeatDaysDesc": "هر روز"},
            {
                "repeatDaysId": 2,
                "repeatDaysCode": "2",
                "repeatDaysDesc": "دو روز يکبار",
            },
            {"repeatDaysId": 3, "repeatDaysCode": "7", "repeatDaysDesc": "هر هفته"},
            {"repeatDaysId": 4, "repeatDaysCode": "14", "repeatDaysDesc": "هر دو هفته"},
            {"repeatDaysId": 5, "repeatDaysCode": "30", "repeatDaysDesc": "هر ماه"},
            {"repeatDaysId": 6, "repeatDaysCode": "90", "repeatDaysDesc": "هر سه ماه"},
            {"repeatDaysId": 7, "repeatDaysCode": "180", "repeatDaysDesc": "هر شش ماه"},
        ]

        for item in repeats:
            MedicineRepeat.objects.get_or_create(
                concept=item["repeatDaysDesc"],
                tamin_json=item,
            )

        self.stdout.write(self.style.SUCCESS("repeats successfully imported"))
