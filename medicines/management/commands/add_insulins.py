import json
from django.core.management.base import BaseCommand, CommandError

from visit.models.insulin_prescription_models import Insulin


class Command(BaseCommand):
    help = "Reads data from a JSON file and imports it into the Insulin model"

    def handle(self, *args, **kwargs):
        file_path = "visit/insulins.json"
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

                for item in data["insulins_short_acting"]:
                    Insulin.objects.create(name=item, category="short_acting")
                for item in data["insulins_long_acting"]:
                    Insulin.objects.create(name=item, category="long_acting")
                for item in data["None"]:
                    Insulin.objects.create(name=item, category="None")
                self.stdout.write(self.style.SUCCESS("Data successfully imported"))

        except FileNotFoundError:
            raise CommandError('File "%s" does not exist' % file_path)
        except json.JSONDecodeError:
            raise CommandError('File "%s" is not a valid JSON file' % file_path)
        except KeyError as e:
            raise CommandError("Missing key in JSON data: %s" % str(e))
