web: gunicorn Diary.wsgi
worker: celery -A Diary worker -l INFO --beat -S django -l info
beat: celery -A Diary beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler


