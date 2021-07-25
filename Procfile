web: gunicorn Diary.wsgi
worker: celery -A Diary worker -l INFO
beat: celery -A Diary beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler


