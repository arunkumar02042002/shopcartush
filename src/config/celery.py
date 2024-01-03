from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# To update the timezone.
# app.conf.enable_utc = False
# app.conf.update(timezone="Asia/Kolkata")

app.config_from_object(settings, namespace='CELERY')

app.conf.beat_schedule = {
    "delete-expired-tokens": {
        "task": "authentication.tasks.delete_expired_tokens",
        "schedule": 15 # In seconds
        # "schedule": crontab(hour=1, minute=15), If we want to schedule task at a perticular time
        # "options": {"queue": "tokens"} - Give the name of the queue
    }
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

# To run celery
# celery -A config.celery worker -E --pool=solo -l INFO

'''This worker is dedicated to tokens queue!'''
# celery -A config.celery worker -E --pool=solo -l INFO -Q tokens
    
    
# To run celery beat
# celery -A config beat -l info 