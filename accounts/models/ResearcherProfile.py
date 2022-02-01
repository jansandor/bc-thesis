from accounts.models import BaseUserProfile
from django.utils.translation import gettext_lazy as _


# TODO vyzkumnici asi nebudou potrebovat profil, spis permissions atd.
class ResearcherProfile(BaseUserProfile):
    class Meta:
        verbose_name = _('výzkumník')
        verbose_name_plural = _('výzkumníci')
