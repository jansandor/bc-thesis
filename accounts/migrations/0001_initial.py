# Generated by Django 3.2.8 on 2022-04-11 14:33

import accounts.models.UserManager
import accounts.utils.user.functions
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False,
                                                     help_text='Designates that this user has all permissions without explicitly assigning them.',
                                                     verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False,
                                                 help_text='Designates whether the user can log into this admin site.',
                                                 verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True,
                                                  help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.',
                                                  verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('is_client', models.BooleanField(default=False, verbose_name='klient')),
                ('is_psychologist', models.BooleanField(default=False, verbose_name='psycholog')),
                ('is_researcher', models.BooleanField(default=False, verbose_name='výzkumník')),
                ('first_name', models.CharField(max_length=150, verbose_name='jméno')),
                ('last_name', models.CharField(max_length=150, verbose_name='příjmení')),
                ('email_verified', models.BooleanField(default=False, verbose_name='ověřený e-mail')),
                ('confirmed_by_staff', models.BooleanField(default=True, verbose_name='schválený obsluhou')),
                ('groups', models.ManyToManyField(blank=True,
                                                  help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
                                                  related_name='user_set', related_query_name='user', to='auth.Group',
                                                  verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.',
                                                            related_name='user_set', related_query_name='user',
                                                            to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', accounts.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='PsychologistProfile',
            fields=[
                ('user',
                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False,
                                      to='accounts.user', verbose_name='uživatel')),
                ('user_type', models.CharField(
                    choices=[('client', 'Klient'), ('psychologist', 'Psycholog'), ('researcher', 'Výzkumník')],
                    default='client', max_length=12, verbose_name='typ uživatele')),
                ('academic_degree_before_name', models.CharField(blank=True,
                                                                 choices=[('', '-'), ('Bc.', 'Bc.'), ('Mgr.', 'Mgr.'),
                                                                          ('Ing.', 'Ing.'), ('MUDr.', 'MUDr.'),
                                                                          ('RNDr.', 'RNDr.'), ('doc.', 'doc.'),
                                                                          ('prof.', 'prof.'), ('Dr.', 'Dr.')],
                                                                 default='', max_length=10,
                                                                 verbose_name='titul před jménem')),
                ('academic_degree_after_name', models.CharField(blank=True, choices=[('', '-'), ('Ph.D.', 'Ph.D.'),
                                                                                     ('CSc.', 'CSc.'),
                                                                                     ('DrSc.', 'DrSc.'),
                                                                                     ('DiS.', 'DiS.')], default='',
                                                                max_length=10, verbose_name='titul za jménem')),
                ('certificate', models.FileField(upload_to=accounts.utils.user.functions.user_specific_upload_file_path,
                                                 verbose_name='certifikát')),
                ('personal_key',
                 models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='osobní klíč')),
            ],
            options={
                'verbose_name': 'psycholog',
                'verbose_name_plural': 'psychologové',
            },
        ),
        migrations.CreateModel(
            name='ResearcherProfile',
            fields=[
                ('user',
                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False,
                                      to='accounts.user', verbose_name='uživatel')),
                ('user_type', models.CharField(
                    choices=[('client', 'Klient'), ('psychologist', 'Psycholog'), ('researcher', 'Výzkumník')],
                    default='client', max_length=12, verbose_name='typ uživatele')),
            ],
            options={
                'verbose_name': 'výzkumník',
                'verbose_name_plural': 'výzkumníci',
            },
        ),
        migrations.CreateModel(
            name='ClientProfile',
            fields=[
                ('user',
                 models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False,
                                      to='accounts.user', verbose_name='uživatel')),
                ('user_type', models.CharField(
                    choices=[('client', 'Klient'), ('psychologist', 'Psycholog'), ('researcher', 'Výzkumník')],
                    default='client', max_length=12, verbose_name='typ uživatele')),
                ('birthdate', models.DateField(verbose_name='datum narození')),
                ('sex', models.CharField(choices=[('-', 'nechci uvést'), ('M', 'muž'), ('W', 'žena')], default='-',
                                         max_length=1, verbose_name='pohlaví')),
                ('nationality', models.CharField(choices=[('ČR', 'ČR'), ('SK', 'SK')], default='ČR', max_length=3,
                                                 verbose_name='státní příslušnost')),
                ('terms_accepted', models.BooleanField(default=False,
                                                       verbose_name='souhlas s účastí ve výzkumu a zpracováním osobních údajů')),
                ('psychologist',
                 models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='psychologist',
                                   to=settings.AUTH_USER_MODEL, verbose_name='psycholog')),
            ],
            options={
                'verbose_name': 'klient',
                'verbose_name_plural': 'klienti',
            },
        ),
    ]
