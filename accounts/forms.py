from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.db import transaction
from django.forms import ModelForm
from django import forms
from .models import ClientProfile, PsychologistProfile, User
from django.utils.translation import gettext_lazy as _
import datetime
from datetime import datetime as dt
from .utils.user import user_types, sex_choices
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import InlineRadios, Field, Div, InlineField
from crispy_forms.layout import Layout, Fieldset, Row, Column
from django.core.exceptions import ObjectDoesNotExist


# TODO odstranit zbytecne naroky na tvorbu hesla

class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'autofocus': 'true'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = 'fw-light'


class ClientUserCreationForm(UserCreationForm):
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_client = True
        user.is_active = False
        user.save()
        return user


class PsychologistUserCreationForm(UserCreationForm):
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_psychologist = True
        user.save()
        return user


class ResearcherUserCreationForm(UserCreationForm):
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_researcher = True
        user.save()
        return user


class DateInput(forms.DateInput):
    """
    Changes Django default input_type of DateInput which is 'text' to HTML5 'date' input type.
    It ensures that the HTML5 "DatePicker" is displayed to the user insted of text input.
    It also allows only correct date to be selected, ie. it is not possible to select 30.2.yyyy etc.
    """
    input_type = 'date'


class UserNotSpecifiedException(Exception):
    def __str__(self):
        return 'user keyword argument must be assigned to an instance of User'


class ClientProfileCreationForm(ModelForm):
    """ Zajisti vytvoreni klientskeho profilu pri registraci uzivatele"""

    class Meta:
        model = ClientProfile
        fields = ['birthdate', 'sex', 'psychologist_key']
        widgets = {
            'birthdate': DateInput(attrs={'min': datetime.date(dt.today().year - 100, 1, 1).__str__(),
                                          'max': dt.today().date().__str__()}),
            'sex': forms.RadioSelect()
        }

    psychologist_key = forms.UUIDField(label=_('Klíč vašeho psychologa'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = 'fw-light'
        self.helper.layout = Layout(
            'birthdate',
            InlineRadios('sex'),
            'psychologist_key'
        )

    def clean_psychologist_key(self):
        psychologist_key = self.cleaned_data['psychologist_key']
        try:
            PsychologistProfile.objects.get(personal_key__exact=psychologist_key)
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                _('Zadaný klíč nepatří žádnému psychologovi. Pokud jste klíč od vašeho psychologa neobdrželi, prosím, kontaktujte jej.'),
                code='invalid psychologist key',
                params={'value': psychologist_key})
        return psychologist_key

    def save(self, commit=True, user=None):
        if user is None:
            raise UserNotSpecifiedException
        else:
            data = self.cleaned_data
            psychologist_profile = PsychologistProfile.objects.get(personal_key__exact=data['psychologist_key'])
            profile = ClientProfile.objects.create(user=user, user_type=user_types.CLIENT, birthdate=data['birthdate'],
                                                   sex=data['sex'], psychologist=psychologist_profile.user)
            return profile


class PsychologistProfileCreationForm(ModelForm):
    """ Zajisti vytvoreni profilu psychologa pri registraci uzivatele"""

    class Meta:
        model = PsychologistProfile
        fields = ['academic_degree_before_name', 'academic_degree_after_name', 'certificate']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = 'fw-light'

    def save(self, commit=True, user=None):
        # TODO if user is None: raise some error or throw except
        data = self.cleaned_data
        profile = PsychologistProfile.objects.create(user=user, user_type=user_types.PSYCHOLOGIST,
                                                     academic_degree_before_name=data['academic_degree_before_name'],
                                                     academic_degree_after_name=data['academic_degree_after_name'],
                                                     certificate=data['certificate'])
        return profile
