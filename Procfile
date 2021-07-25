web: gunicorn Diary.wsgi
worker: python manage.py celery worker --loglevel=info
beat: python manage.py celery beat --loglevel=info