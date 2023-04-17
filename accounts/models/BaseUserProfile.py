from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from accounts.utils.user import user_types


# TODO kdyz se smaze v adminu profil, uzivatelsky ucet prezije, ale rozbije se napr. "upravit profil"
# asi by to chtelo podobne jak u uctu, at s profilem zmizi i ucet?
class BaseUserProfile(models.Model):
    USER_TYPES = (
        (user_types.CLIENT, _('Klient')),
        (user_types.PSYCHOLOGIST, _('Psycholog')),
        (user_types.RESEARCHER, _('Výzkumník')),
    )

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, primary_key=True,
                                verbose_name=_('uživatel'))
    user_type = models.CharField(_('typ uživatele'), max_length=12, choices=USER_TYPES, default=user_types.CLIENT)

    def __str__(self):
        """zajisti vypsani jmena uzivatele v tabulce profily, pri vyberu psychologa"""
        return self.user.__str__()

    class Meta:
        abstract = True
