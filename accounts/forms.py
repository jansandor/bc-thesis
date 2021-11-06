from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.db import transaction
from django.forms import ModelForm
from django import forms
from .models import ClientProfile, PsychologistProfile, User, PsychologistProxy
from django.utils.translation import gettext_lazy as _
import datetime
from datetime import datetime as dt
from .utils.user import user_types, sex_choices
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import InlineRadios, Field, Div, InlineField
from crispy_forms.layout import Layout, Fieldset, Row, Column


# TODO odstranit zbytecne naroky na tvorbu hesla
# TODO implementovano neco jako ze klientova registrace bude dokoncena, az ji psycholog schvali

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


class ClientProfileCreationForm(ModelForm):
    """ Zajisti vytvoreni klientskeho profilu pri registraci uzivatele"""

    class Meta:
        model = ClientProfile
        fields = ['birthdate', 'sex', 'psychologist']
        widgets = {
            'birthdate': DateInput(attrs={'min': datetime.date(dt.today().year - 100, 1, 1).__str__(),
                                          'max': dt.today().date().__str__()}),
            'sex': forms.RadioSelect
        }

    # TODO nejak poresit, at muzu queryset nastavit na PsychProxy a pritom pracovat s user attributem
    psychologist = forms.ModelChoiceField(queryset=User.objects.filter(is_psychologist=True),
                                          label=_('Váš psycholog'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = 'fw-light'  # 'fw-bolder'
        self.helper.layout = Layout(
            'birthdate',
            InlineRadios('sex'),
            'psychologist'
        )

    def save(self, commit=True, user=None):
        # TODO if user is None: raise some error or throw except
        data = self.cleaned_data
        # psychologist_proxy = data['psychologist']
        profile = ClientProfile.objects.create(user=user, user_type=user_types.CLIENT, birthdate=data['birthdate'],
                                               sex=data['sex'],
                                               psychologist=data['psychologist'])
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
