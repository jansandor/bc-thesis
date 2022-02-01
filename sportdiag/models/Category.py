from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from sportdiag.models import Survey


class Category(models.Model):
    name = models.CharField(_('název'), max_length=400)
    description = models.CharField(_('popis'), max_length=2000, blank=True, null=True)
    # order = models.PositiveIntegerField(_('pořadí zobrazení'), default=1)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('dotazník'), related_name='categories')

    class Meta:
        # pylint: disable=too-few-public-methods
        verbose_name = _('kategorie')
        verbose_name_plural = _('kategorie')

    def __str__(self):
        return self.name
