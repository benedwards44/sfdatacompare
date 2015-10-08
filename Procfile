#web: gunicorn sfdatacompare.wsgi --workers $WEB_CONCURRENCY
web: waitress-serve --port=$PORT sfdatacompare.wsgi:application
worker: celery -A comparedata.tasks worker -B --loglevel=info