from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from sportdiag.models import Survey


class Category(models.Model):
    name = models.CharField(_('název'), max_length=400)
    description = models.TextField(_('popis'), blank=True, null=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('dotazník'), related_name='categories')

    class Meta:
        verbose_name = _('kategorie')
        verbose_name_plural = _('kategorie')

    def __str__(self):
        return self.name
