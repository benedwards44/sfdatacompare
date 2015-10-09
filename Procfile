web: gunicorn sfdatacompare.wsgi --workers $WEB_CONCURRENCY 
worker: celery -A comparedata.tasks worker -B --loglevel=info