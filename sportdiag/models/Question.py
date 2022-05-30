from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

from sportdiag.models import Survey, Category, LikertScale, QuestionGroup


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
    number = models.PositiveIntegerField(_("číslo otázky"), default=0, help_text=_(
        "Pokud otázka nespadá do žádné hodnocené kategorie (dimenze, škály, ...), nastavte číslo na 0."))
    order = models.PositiveIntegerField(_('pořadí v dotazníku'), default=1)
    required = models.BooleanField(_('povinná odpověď'))
    choices = models.TextField(_('odpovědi'), help_text='Zadejte možné odpovědi na otázku oddělené čárkou.', null=True,
                               blank=True)
    scores = models.TextField(_('skóre odpovědí'), default=0,
                              help_text='Zadejte bodové hodnocení každé odpovědi na otázku oddělené čárkou. V případě, že otázka není bodově hodnocena, zadejte "0" (bez uvozovek).')
    # todo choices_scores, choices_texts, len scores == len choices
    type = models.CharField(_("typ otázky"), max_length=100, choices=QUESTION_TYPES, default=SHORT_TEXT)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('kategorie'),
                                 related_name="questions", blank=True, null=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('dotazník'), related_name="questions")
    likert_scale = models.ForeignKey(LikertScale, on_delete=models.SET_NULL, verbose_name=_('likertova škála'),
                                     related_name="questions", blank=True, null=True)
    group = models.ForeignKey(QuestionGroup, on_delete=models.SET_NULL, verbose_name=_('skupina'), null=True,
                              blank=True, related_name="questions")

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
                choices_list.append(choice.lower())
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

    def get_clean_scores(self):
        """Return split and stripped list of choices with no null values."""
        if self.scores is None:
            return []
        score_list = []
        for score in self.scores.split(','):
            score = score.strip()
            if score:
                score_list.append(int(score))
        return score_list

    def get_answer_score(self, answer):
        """Returns question choice score for given answer."""
        scores = self.get_clean_scores()
        choices = self.get_clean_choices()
        if answer.body in choices:
            index = choices.index(answer.body)
            return int(scores[index])
        return 0

    @property
    def short_name(self):
        return f"O{self.number}"

    def __str__(self):
        return f'{self.survey.short_name}: O{self.number}P{self.order}{"*" if self.required else ""}: {self.category if self.category is not None else "<Nenastavená kategorie>"}'

    # todo validate choices like in django survey?
