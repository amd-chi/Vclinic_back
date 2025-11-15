import json
from django.core.management.base import BaseCommand, CommandError

from visit.models import MedicineUsage


class Command(BaseCommand):
    help = "Reads data from a JSON file and imports it into the MedicineUsage model"

    def handle(self, *args, **kwargs):
        file_path = "insurance/connection/Requests/medicine/getDrugUsageResponse.json"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                for item in data["data"]["list"]:
                    MedicineUsage.objects.create(
                        concept=item["drugUsageConcept"], tamin_json=item
                    )

                self.stdout.write(self.style.SUCCESS("Data successfully imported"))

        except FileNotFoundError:
            raise CommandError('File "%s" does not exist' % file_path)
        except json.JSONDecodeError:
            raise CommandError('File "%s" is not a valid JSON file' % file_path)
        except KeyError as e:
            raise CommandError("Missing key in JSON data: %s" % str(e))
