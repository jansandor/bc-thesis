from django.db import models
from django.utils.translation import gettext_lazy as _
from sportdiag.models import Survey, QuestionGroup


class LikertScale(models.Model):
    name = models.CharField(_('název'), max_length=400)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('dotazník'),
                               related_name='likert_scales')
    choices = models.TextField(_('odpovědi'),
                               help_text='Zadejte možné odpovědi likertovi škály oddělené čárkou. Např. téměř nikdy, někdy, často, téměř vždy')
    scores = models.TextField(_('skóre odpovědí'),
                              help_text='Zadejte bodové hodnocení každé odpovědi oddělené čárkou. Např. 0,1,2,3')
    group = models.ForeignKey(QuestionGroup, on_delete=models.SET_NULL, verbose_name=_('skupina'), null=True,
                              blank=True, related_name="likert_scales")

    class Meta:
        verbose_name = _('likertova škála')
        verbose_name_plural = _('likertovy škály')

    def __str__(self):
        return self.name

    def get_choices(self):
        choices = [choice.strip() for choice in self.choices.split(",")]
        print("LS choices", choices)
        return choices
