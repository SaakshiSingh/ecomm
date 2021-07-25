web: gunicorn Diary.wsgi
worker: celery -A Diary worker --beat -S django -l info


