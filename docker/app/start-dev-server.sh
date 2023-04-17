#!/bin/sh
echo "Running migrations.."
python manage.py showmigrations
python manage.py migrate
python manage.py showmigrations
echo "Migrations DONE.."
echo "Starting server.."
python manage.py runserver 0.0.0.0:8000 --settings=bp.settings.development
# gunicorn bp.wsgi --bind 0.0.0.0:8000 --timeout 60 --access-logfile - --error-logfile -
