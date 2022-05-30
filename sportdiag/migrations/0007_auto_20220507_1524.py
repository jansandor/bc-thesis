# Generated by Django 3.2.8 on 2022-05-07 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sportdiag', '0006_auto_20220416_1409'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questiongroup',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='popis'),
        ),
        migrations.AlterField(
            model_name='questiongroup',
            name='instructions',
            field=models.TextField(blank=True, default='', verbose_name='instrukce'),
        ),
        migrations.AlterField(
            model_name='questiongroup',
            name='name',
            field=models.CharField(blank=True, default='', max_length=400, verbose_name='název'),
        ),
    ]