# Generated by Django 3.2.8 on 2022-07-09 20:58

from django.db import migrations
from django.db import transaction
from decouple import config

app_name = 'accounts'


@transaction.atomic
def add_super_user(apps, schema_editor):
    User = apps.get_model(app_name, 'User')
    User.objects.create_superuser(
        email=config('DJANGO_SUPERUSER_EMAIL'),
        password=config('DJANGO_SUPERUSER_PASSWORD'),
        first_name=config('DJANGO_SUPERUSER_FIRST_NAME'),
        last_name=config('DJANGO_SUPERUSER_LAST_NAME')
    )


@transaction.atomic
def clean(apps, schema_editor):
    User = apps.get_model(app_name, 'User')
    user = User.objects.get(email=config('DJANGO_SUPERUSER_EMAIL'))
    user.delete()


class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_super_user, reverse_code=clean)
    ]
