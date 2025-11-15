from django.core.cache import cache
from celery import shared_task
import time


@shared_task(bind=True)
def background_process_1(self, identifier, input_data):
    cache.set(identifier, self.request.id, timeout=5 * 60)
    try:
        for i in range(5):
            print(f"Processing {input_data} - Step {i+1}/5")
            time.sleep(60)
    except Exception as e:
        print(f"Task failed: {e}")
        return "Failed"

    return "Success"
