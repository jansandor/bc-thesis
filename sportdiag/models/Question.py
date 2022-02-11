from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils.text import slugify

from sportdiag.models import Survey, Category, LikertScale


# dotaznik ma kategorie, kategorie ma otazky
class Question(models.Model):
    SHORT_TEXT = "short_text"
    RADIO = "radio"
    SELECT = "select"
    INTEGER = "integer"
    LIKERT_SCALE = "likert_scale"

    QUESTION_TYPES = (
        (SHORT_TEXT, _("krátký text (jeden řádek)")),
        (RADIO, _("výběr jedné odpovědi")),
        (SELECT, _("výběr jedné odpovědi ze seznamu")),
        (INTEGER, _("celé číslo")),
        (LIKERT_SCALE, _("likertova škála"))
    )

    text = models.TextField(_('text otázky'))
    order = models.PositiveIntegerField(_('pořadí v dotazníku'), default=1)
    required = models.BooleanField(_('povinná odpověď'))
    choices = models.TextField(_('odpovědi'), help_text='Zadejte možné odpovědi na otázku oddělené čárkou.', null=True,
                               blank=True)
    type = models.CharField(_("typ otázky"), max_length=100, choices=QUESTION_TYPES, default=SHORT_TEXT)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name=_('kategorie'), null=True,
                                 blank=True, related_name="questions"
                                 )
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('dotazník'), related_name="questions")
    likert_scale = models.ForeignKey(LikertScale, on_delete=models.SET_NULL, verbose_name=_('likertova škála'),
                                     related_name="questions", blank=True, null=True)

    class Meta:
        verbose_name = _('otázka')
        verbose_name_plural = _('otázky')
        # ordering = ("survey", "order")

    def get_clean_choices(self):
        """Return split and stripped list of choices with no null values."""
        if self.choices is None:
            return []
        choices_list = []
        for choice in self.choices.split(','):
            choice = choice.strip()
            if choice:
                choices_list.append(choice)
        return choices_list

    def get_choices(self):
        """
        Parse the choices field and return a tuple formatted appropriately
        for the 'choices' argument of a form widget.
        """
        choices_list = []
        for choice in self.get_clean_choices():
            choices_list.append((slugify(choice, allow_unicode=True), choice))
        choices_tuple = tuple(choices_list)
        return choices_tuple

    def get_short_name(self):
        return f"Q{self.order}"

    def __str__(self):
        if self.category:
            return f'{self.category}: Otázka {self.order}'
        return f'<Nenastavená kategorie>: Otázka {self.order}'

    # todo validate choices like in django survey?
