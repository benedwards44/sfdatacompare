web: gunicorn sfdatacompare.wsgi --workers $WEB_CONCURRENCY
worker: celery -A sfdatacompare.tasks worker -B --loglevel=info