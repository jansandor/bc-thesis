from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

from accounts.models.UserManager import UserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email'), unique=True)
    is_client = models.BooleanField(_('klient'), default=False)
    is_psychologist = models.BooleanField(_('psycholog'), default=False)
    is_researcher = models.BooleanField(_('výzkumník'), default=False)
    first_name = models.CharField(_('jméno'), max_length=150, blank=False)
    last_name = models.CharField(_('příjmení'), max_length=150, blank=False)
    email_verified = models.BooleanField(_('ověřený e-mail'), default=False)
    # todo move confirmed_by_staff attribute to PsychologistProfile?
    confirmed_by_staff = models.BooleanField(_('schválený hlavním výzkumníkem'), default=False)
    is_active = models.BooleanField(_('active'), default=False,
                                    help_text=_(
                                        'Designates whether this user should be treated as active. '
                                        'Unselect this instead of deleting accounts.'
                                    ), )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.get_full_name()
