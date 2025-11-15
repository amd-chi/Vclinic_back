import json
from django.core.management.base import BaseCommand, CommandError

from other_paraclinic_services.models import Category


class Command(BaseCommand):
    help = "Reads data from a JSON file and imports it into the Category"

    def handle(self, *args, **kwargs):
        file_path = "insurance/connection/Requests/other_paraclinic_services/otherServicesTypeResponse.json"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                for item in data["data"]:
                    Category.objects.create(
                        concept=item["srvTypeDes"],
                        code=item["srvType"],
                    )

                self.stdout.write(self.style.SUCCESS("Data successfully imported"))

        except FileNotFoundError:
            raise CommandError('File "%s" does not exist' % file_path)
        except json.JSONDecodeError:
            raise CommandError('File "%s" is not a valid JSON file' % file_path)
