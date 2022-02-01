import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from sportdiag.models import Survey
from accounts.models import User


class Response(models.Model):
    created = models.DateTimeField(_('datum vytvoření'), auto_now_add=True)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, verbose_name=_('dotazník'), related_name='responses')
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, verbose_name=_('uživatel'), null=True,
                             blank=True)
    interview_uuid = models.UUIDField(_("unikátní ID responze"), default=uuid.uuid4(), editable=False, unique=True)

    class Meta:
        verbose_name = _('Set of answers to survey')
        verbose_name_plural = _('Sets of answers to surveys')

    def __str__(self):
        return f"Response to {self.survey} by {self.user} on {self.created}"
