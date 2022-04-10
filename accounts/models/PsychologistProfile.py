from django.db import models
from django.utils.translation import gettext_lazy as _

import uuid

from accounts.models import BaseUserProfile
from accounts.utils.user import academic_degrees
from accounts.utils.user.functions import user_specific_upload_file_path


class PsychologistProfile(BaseUserProfile):
    academic_degree_before_name = models.CharField(_('titul před jménem'), max_length=10, blank=True,
                                                   choices=academic_degrees.ACADEMIC_DEGREES_BEFORE_NAME,
                                                   default=academic_degrees.NO_DEGREE)
    academic_degree_after_name = models.CharField(_('titul za jménem'), max_length=10, blank=True,
                                                  choices=academic_degrees.ACADEMIC_DEGREES_AFTER_NAME,
                                                  default=academic_degrees.NO_DEGREE)
    # TODO multiplefiles input
    # https://stackoverflow.com/questions/38257231/how-can-i-upload-multiple-files-to-a-model-field
    certificate = models.FileField(upload_to=user_specific_upload_file_path, verbose_name=_('certifikát'))
    # todo uuid by mel byt sam o sobe s vysokou pravdepodobnosti unikatni, je dobry napad setovat ho defaultne unique?
    # aby se pak nekdy nestalo, ciste velkou nahodou, ze spadne tvorba profilu v DB, protoze se nevygeneroval nahodny...
    personal_key = models.UUIDField(_('osobní klíč'), default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        verbose_name = _('psycholog')
        verbose_name_plural = _('psychologové')  # TODO tady to bude chtit gettext pro plural

    def __str__(self):
        # todo v mailu adminovi kdyz nejsou tituly nebo jeden z nich udela navic mezeru/y kolem jmena
        return f'{self.academic_degree_before_name} {self.user.__str__()} {self.academic_degree_after_name}'
