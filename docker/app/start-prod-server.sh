#!/bin/sh
python manage.py showmigrations
# without users demo data in real production, for now it is test production where i need some data to show
python manage.py migrate
python manage.py showmigrations
python manage.py collectstatic --noinput
echo "Starts gunicorn.."
gunicorn --workers 3 bp.wsgi --bind 0.0.0.0:8000 --timeout 60 --access-logfile - --error-logfile -
