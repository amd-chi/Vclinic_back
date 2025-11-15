import json
from django.core.management.base import BaseCommand, CommandError

from visit.models import MedicineAmount


class Command(BaseCommand):
    help = "Reads data from a JSON file and imports it into the MedicineAmount model"

    def handle(self, *args, **kwargs):
        file_path = "insurance/connection/Requests/medicine/getDrugAmountResponse.json"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                for item in data["data"]["list"]:
                    MedicineAmount.objects.create(
                        concept=item["drugAmntConcept"],
                        tamin_json=item,
                    )

                self.stdout.write(self.style.SUCCESS("Data successfully imported"))

        except FileNotFoundError:
            raise CommandError('File "%s" does not exist' % file_path)
        except json.JSONDecodeError:
            raise CommandError('File "%s" is not a valid JSON file' % file_path)
