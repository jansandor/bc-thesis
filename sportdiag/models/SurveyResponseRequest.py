from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from sportdiag.models import Survey


class SurveyResponseRequest(models.Model):
    client = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('klient'),
                               related_name='clients')
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('dotazník'), related_name='surveys')
    requested_on_date = models.DateTimeField(_('datum vyžádání responze'), auto_now_add=True)
    responded_on_date = models.DateTimeField(_('datum responze'), null=True)
    is_pending = models.BooleanField(_('čeká se na reponzi'), default=True)

    class Meta:
        verbose_name = _('žádost o responzi')
        verbose_name_plural = _('žádosti o responze')

    def __str__(self):
        return f"CID: {self.client_id} SID: {self.survey_id} is_pending: {self.is_pending}"
