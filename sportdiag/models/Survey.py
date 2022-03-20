from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Survey(models.Model):
    name = models.CharField(_('název'), max_length=400)
    short_name = models.CharField(_('zkratka názvu'), max_length=30, help_text=_('Např.: OMSAT-3*, ACSI-28 apod.'))
    description = models.TextField(_('popis'))

    class Meta:
        verbose_name = _('dotazník')
        verbose_name_plural = _('dotazníky')

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("sportdiag:survey_detail", kwargs={"survey_id": self.id})

    def non_empty_categories(self):
        # todo change to return non empty categories
        # return [cat for cat in list(self.categories.order_by("id") if cat.questions.count() > 0]
        return list(self.categories.all())

    def non_empty_likert_scales(self):
        return [ls for ls in self.likert_scales.order_by("id") if ls.questions.count() > 0]

    def get_questions(self):
        return self.questions.all()
