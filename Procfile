web: gunicorn Diary.wsgi
worker: python manage.py celery worker -A Diary -l info

