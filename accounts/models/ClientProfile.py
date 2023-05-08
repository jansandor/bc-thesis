import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from accounts.models import BaseUserProfile
from accounts.utils.user import sex_choices, nationality


class ClientProfile(BaseUserProfile):
    psychologist = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, blank=False, null=True,
                                     verbose_name=_('psycholog'), related_name='psychologist')
    birthdate = models.DateField(_('datum narození'))
    sex = models.CharField(_('pohlaví'), max_length=1, choices=sex_choices.SEX_CHOICES,
                           default=sex_choices.NOTSET)
    nationality = models.CharField(_('státní příslušnost'), max_length=3, choices=nationality.CHOICES,
                                   default=nationality.CZE)
    terms_accepted = models.BooleanField(_('souhlas s účastí ve výzkumu a zpracováním osobních údajů'), default=False)

    @property
    def age(self):
        today = datetime.datetime.utcnow()
        return today.year - self.birthdate.year - int(
            (today.month, today.day) < (self.birthdate.month, self.birthdate.day))

    class Meta:
        verbose_name = _('klient')
        verbose_name_plural = _('klienti')
