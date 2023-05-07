import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.urls import reverse

from sportdiag.models import Survey


class Response(models.Model):
    created = models.DateTimeField(_('datum vytvoření'), auto_now_add=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('dotazník'), related_name='responses')
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_('uživatel'),
                             related_name='responses')

    interview_uuid = models.UUIDField(_("unikátní ID responze"), default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = _('Set of answers to survey')
        verbose_name_plural = _('Sets of answers to surveys')

    def compute_category_score(self, category):
        self.survey.categories.get(id=category.id)
        cat_score = 0
        if self.survey.type == Survey.ACSI28_ATHLETE:
            questions_ids = category.questions.order_by("number").values_list("id", flat=True)
            cat_score = self.answers.filter(question_id__in=questions_ids).aggregate(
                Sum("score"))
            return cat_score.get("score__sum") / 4
        elif self.survey.type == Survey.ACSI28_REFEREE:
            questions_ids = category.questions.order_by("number").values_list("id", flat=True)
            cat_score = self.answers.filter(question_id__in=questions_ids).aggregate(
                Sum("score"))
            if category.name.lower() == "Schopnost akceptovat konstruktivní kritiku (Coachability)".lower():
                return cat_score.get("score__sum") / 3
            return cat_score.get("score__sum") / 4
        elif self.survey.type == Survey.PCDEQ:
            questions_count = category.questions.count()
            cat_score = self.answers.filter(question__in=category.questions.order_by("number")).aggregate(Sum("score"))
            return cat_score.get("score__sum") / questions_count
        elif self.survey.type == Survey.VMIQ2:
            questions_ids = category.questions.order_by("number").values_list("id", flat=True)
            cat_score = self.answers.filter(question_id__in=questions_ids).aggregate(
                Sum("score"))
            return cat_score.get("score__sum")
        return cat_score

    @property
    def total_score(self):
        total_score = 0
        if self.survey.type == Survey.ACSI28_ATHLETE or self.survey.type == Survey.VMIQ2:
            total_score = self.answers.filter(question_id__in=self.survey.categorized_questions()).aggregate(
                Sum("score"))
            return total_score.get("score__sum")
        elif self.survey.type == Survey.ACSI28_REFEREE:
            # question number 3 is not included in the total survey score calculation
            total_score = self.answers.filter(
                question_id__in=self.survey.categorized_questions().exclude(number=3)).aggregate(Sum("score"))
            return total_score.get("score__sum")
        elif self.survey.type == Survey.PCDEQ:
            for cat in self.survey.non_empty_categories():
                total_score += self.compute_category_score(cat)
        return total_score

    @property
    def max_score(self):
        return self.survey.max_score

    def get_absolute_url(self):
        return reverse('sportdiag:response_detail', kwargs={'response_id': self.id})

    def __str__(self):
        return f"Response to {self.survey} by {self.user} on {self.created}"
