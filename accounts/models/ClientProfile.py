from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from accounts.models import BaseUserProfile
from accounts.utils.user import sex_choices


class ClientProfile(BaseUserProfile):
    psychologist = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=False, null=True,
                                     verbose_name=_('psycholog'), related_name='psychologist')
    birthdate = models.DateField(_('datum narození'))
    sex = models.CharField(_('pohlaví'), max_length=1, choices=sex_choices.SEX_CHOICES, default=sex_choices.NOTSET)

    # todo property age
    class Meta:
        verbose_name = _('klient')
        verbose_name_plural = _('klienti')
