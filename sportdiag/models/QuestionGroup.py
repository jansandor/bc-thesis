from django.db import models
from django.utils.translation import gettext_lazy as _

from sportdiag.models import Survey


class QuestionGroup(models.Model):
    name = models.CharField(_('název'), max_length=400, blank=True, default="")
    description = models.TextField(_('popis'), blank=True, default="")
    instructions = models.TextField(_('instrukce'), blank=True, default="")
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('dotazník'),
                               related_name='question_groups')

    class Meta:
        verbose_name = _('skupina')
        verbose_name_plural = _('skupiny')

    def __str__(self):
        return self.name
