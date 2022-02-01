from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from sportdiag.models import Survey, Category


class LikertScale(models.Model):
    name = models.CharField(_('název'), max_length=400)
    # order = models.PositiveIntegerField(_('pořadí zobrazení'), default=1)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('dotazník'),
                               related_name='likert_scales')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name=_('kategorie'), null=True,
                                 blank=True, related_name="likert_scales")

    class Meta:
        verbose_name = _('likertova škála')
        verbose_name_plural = _('likertovy škály')

    def __str__(self):
        return self.name
