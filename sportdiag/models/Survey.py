from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Survey(models.Model):
    ACSI28_REFEREE = "ACSI-28-REFEREE"
    ACSI28_ATHLETE = "ACSI-28-ATHLETE"
    PCDEQ = "PCDEQ"
    VMIQ2 = "VMIQ-2"
    OMSAT3_MODIFIED = "OMSAT-3*"

    SURVEY_TYPES = (
        (ACSI28_REFEREE, _("ASCI-28 pro rozhodčí")),
        (ACSI28_ATHLETE, _("ASCI-28 pro sportovce")),
        (PCDEQ, _("PCDEQ")),
        (VMIQ2, _("VIMQ-2")),
        (OMSAT3_MODIFIED, _("OMSAT-3* modifikovaná verze"))
    )

    name = models.CharField(_('název'), max_length=400)
    type = models.CharField(_('Typ/Metoda'), max_length=60, choices=SURVEY_TYPES, default=ACSI28_REFEREE)
    description = models.TextField(_('popis'))
    instructions = models.TextField(_('instrukce'), blank=True, null=True)
    is_published = models.BooleanField(_("zvěřejněný"), default=False)
    # todo last_published_date
    is_deleted = models.BooleanField(_("smazaný"), default=False)
    deleted_date = models.DateTimeField(_('datum smazání'), blank=True, null=True)

    class Meta:
        verbose_name = _('dotazník')
        verbose_name_plural = _('dotazníky')

    @property
    def short_name(self):
        for item_tuple in self.SURVEY_TYPES:
            if self.type in item_tuple:
                return f'{item_tuple[1]}'

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        return reverse("sportdiag:survey_detail", kwargs={"survey_id": self.id})

    def non_empty_categories(self):
        return [cat for cat in self.categories.order_by("id") if cat.questions.count() > 0]

    def non_empty_likert_scales(self):
        return [ls for ls in self.likert_scales.order_by("id") if ls.questions.count() > 0]

    def non_empty_question_groups(self):
        return [qg for qg in self.question_groups.order_by("id") if qg.questions.count() > 0]

    def no_category_questions(self):
        return self.questions.filter(category_id__isnull=True).order_by("order")

    def categorized_questions(self):
        return self.questions.filter(category_id__isnull=False).order_by("order")

    @property
    def max_score(self):
        max_score = 0
        if self.type == self.PCDEQ:
            max_category_score = 6
            return self.categories.count() * max_category_score
        for q in self.questions.all():
            max_score += max(q.get_clean_scores())
        if self.type == self.ACSI28_REFEREE:
            # for this type of survey question 3 is not included in score calculation
            q = self.questions.get(number=3)
            if q:
                max_score -= max(q.get_clean_scores())
        return max_score

    # todo override delete with setting delete date
