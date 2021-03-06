import os
from django.conf import settings

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Diary.settings')

app = Celery('Diary')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS + settings.INSTALLED_APPS_WITH_APPCONFIGS)


app.conf.beat_schedule = {
    'reminder-':{
        'task':'Account.tasks.send_notification',
        'schedule':crontab(minute=0, hour=0),
        
    }
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')