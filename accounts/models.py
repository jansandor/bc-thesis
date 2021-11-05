from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from .user_types import CLIENT, PSYCHOLOGIST, RESEARCHER
from datetime import datetime
from .utils import user_specific_upload_dir


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email'), unique=True)
    is_client = models.BooleanField(_('klient'), default=False)
    is_psychologist = models.BooleanField(_('psycholog'), default=False)
    is_researcher = models.BooleanField(_('výzkumník'), default=False)
    first_name = models.CharField(_('jméno'), max_length=150, blank=False)
    last_name = models.CharField(_('příjmení'), max_length=150, blank=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.get_full_name()


# TODO kdyz se smaze v adminu profil, uzivatelsky ucet prezije, ale rozbije se napr. "upravit profil"
# asi by to chtelo podobne jak u uctu, at s profilem zmizi i ucet?
class BaseUserProfile(models.Model):
    USER_TYPES = (
        (CLIENT, _('Klient')),
        (PSYCHOLOGIST, _('Psycholog')),
        (RESEARCHER, _('Výzkumník')),
    )

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True,
                                verbose_name=_('uživatel'))
    user_type = models.CharField(_('typ uživatele'), max_length=12, choices=USER_TYPES, default=CLIENT)

    def __str__(self):
        """zajisti vypsani jmena uzivatele v tabulce profily, pri vyberu psychologa"""
        return self.user.__str__()

    class Meta:
        abstract = True


class ClientProfile(BaseUserProfile):
    NOTSET = ''
    MAN = 'M'
    WOMAN = 'W'

    SEX_CHOICES = (
        (NOTSET, '-'),
        (MAN, 'muž'),
        (WOMAN, 'žena')
    )

    psychologist = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=True, null=True,
                                     verbose_name=_('psycholog'), related_name='psychologist')
    birthdate = models.DateField(_('datum narození'))
    sex = models.CharField(_('pohlaví'), max_length=1, choices=SEX_CHOICES, default=NOTSET)

    class Meta:
        verbose_name = _('klient')
        verbose_name_plural = _('klienti')

    def age(self):
        return (datetime.today() - self.birthdate).year  # TODO test, vrati int?


class PsychologistProfile(BaseUserProfile):
    NO_DEGREE = ''
    BC_DEGREE = 'Bc.'
    MGR_DEGREE = 'Mgr.'
    ING_DEGREE = 'Ing.'
    MUDR_DEGREE = 'MUDr.'
    RNDR_DEGREE = 'RNDr.'
    DOC_DEGREE = 'doc.'
    PROF_DEGREE = 'prof.'
    DR_DEGREE = 'Dr.'

    ACADEMIC_DEGREES_BEFORE_NAME = (
        (NO_DEGREE, '-'),
        (BC_DEGREE, 'Bc.'),
        (MGR_DEGREE, 'Mgr.'),
        (ING_DEGREE, 'Ing.'),
        (MUDR_DEGREE, 'MUDr.'),
        (RNDR_DEGREE, 'RNDr.'),
        (DOC_DEGREE, 'doc.'),
        (PROF_DEGREE, 'prof.'),
        (DR_DEGREE, 'Dr.')
    )

    PHD_DEGREE = 'Ph.D.'
    CSC_DEGREE = 'CSc.'
    DRSC_DEGREE = 'DrSc.'
    DIS_DEGREE = 'DiS.'

    ACADEMIC_DEGREES_AFTER_NAME = (
        (NO_DEGREE, '-'),
        (PHD_DEGREE, 'Ph.D.'),
        (CSC_DEGREE, 'CSc.'),
        (DRSC_DEGREE, 'DrSc.'),
        (DIS_DEGREE, 'DiS.')
    )

    academic_degree_before_name = models.CharField(_('titul před jménem'), max_length=10,
                                                   choices=ACADEMIC_DEGREES_BEFORE_NAME, default=NO_DEGREE)
    academic_degree_after_name = models.CharField(_('titul za jménem'), max_length=10,
                                                  choices=ACADEMIC_DEGREES_AFTER_NAME, default=NO_DEGREE)
    certificate = models.FileField(upload_to=user_specific_upload_dir, verbose_name=_('certifikát'))

    class Meta:
        verbose_name = _('psycholog')
        verbose_name_plural = _('psychologové')  # TODO tady to bude chtit gettext pro plural

    def __str__(self):
        return f'{self.academic_degree_before_name} {self.user.__str__()} {self.academic_degree_after_name}'


# TODO vyzkumnici asi nebudou potrebovat profil, spis permissions atd.
class ResearcherProfile(BaseUserProfile):
    class Meta:
        verbose_name = _('výzkumník')
        verbose_name_plural = _('výzkumníci')
