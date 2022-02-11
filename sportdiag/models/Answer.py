"""
    These type-specific answer models use a text field to allow for flexible
    field sizes depending on the actual question this answer corresponds to any
    "required" attribute will be enforced by the form.
"""

import logging

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from sportdiag.models import Question, Response

LOGGER = logging.getLogger(__name__)


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name=_("otázka"), related_name="answers")
    response = models.ForeignKey(Response, on_delete=models.CASCADE, verbose_name=_("responze"), related_name="answers")
    created = models.DateTimeField(_("datum vytvoření"), auto_now_add=True)
    # updated = models.DateTimeField(_("Update date"), auto_now=True)
    body = models.TextField(_("odpověď"), blank=True, null=True)

    def __init__(self, *args, **kwargs):
        try:
            question = Question.objects.get(id=kwargs["question_id"])
        except KeyError:
            question = kwargs.get("question")
        body = kwargs.get("body")
        if question and body:
            self.check_answer_body(question, body)
        super().__init__(*args, **kwargs)

    # todo projit jak bude treba, kod resi zobrazeni odpovedi??
    @property
    def values(self):
        if self.body is None:
            return [None]
        if len(self.body) < 3 or self.body[0:3] != "[u'":
            return [self.body]
        # We do not use eval for security reason but it could work with :
        # eval(self.body)
        # It would permit to inject code into answer though.
        values = []
        raw_values = self.body.split("', u'")
        nb_values = len(raw_values)
        for i, value in enumerate(raw_values):
            if i == 0:
                value = value[3:]
            if i + 1 == nb_values:
                value = value[:-2]
            values.append(value)
        return values

    def check_answer_body(self, question, body):
        if question.type in [Question.RADIO, Question.SELECT, Question.LIKERT_SCALE]:
            choices = question.get_clean_choices()
            if body:
                if body[0] == "[":
                    answers = []
                    for i, part in enumerate(body.split("'")):
                        if i % 2 == 1:
                            answers.append(part)
                else:
                    answers = [body]
            for answer in answers:
                if answer not in choices:
                    msg = f"Impossible answer '{body}'"
                    msg += f" should be in {choices} "
                    raise ValidationError(msg)

    def __str__(self):
        return f"{self.__class__.__name__} to '{self.question}' : '{self.body}'"