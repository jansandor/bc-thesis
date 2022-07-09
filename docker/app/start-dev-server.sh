#!/bin/sh
echo "Running migrations.."
python manage.py showmigrations
python manage.py migrate
python manage.py showmigrations
echo "Migrations DONE.."
# todo python manage.py createsuperuser
echo "Starting server.."
ls -l
python manage.py runserver 0.0.0.0:8000 --settings=bp.settings.development