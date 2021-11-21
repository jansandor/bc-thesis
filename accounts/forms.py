from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.db import transaction
from django.forms import ModelForm
from django import forms
from accounts.models import ClientProfile, PsychologistProfile
from django.utils.translation import gettext_lazy as _
import datetime
from datetime import datetime as dt
from accounts.utils.user import user_types
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import InlineRadios
from crispy_forms.layout import Layout, Submit, Field, Div
from django.core.exceptions import ObjectDoesNotExist
from accounts.utils.forms import DateInput
from accounts.utils.user import sex_choices
from accounts.utils.user import academic_degrees


class UserCreationForm(DjangoUserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'autofocus': 'true'}),
        }


class ClientUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2',
                  'birthdate', 'sex', 'psychologist_key']

    birthdate = forms.DateField(widget=DateInput(attrs={'min': datetime.date(dt.today().year - 100, 1, 1).__str__(),
                                                        'max': dt.today().date().__str__()}),
                                label=_('Datum narození'))
    sex = forms.ChoiceField(widget=forms.RadioSelect(), choices=sex_choices.SEX_CHOICES, initial=sex_choices.NOTSET,
                            label=_('Pohlaví'))
    psychologist_key = forms.UUIDField(label=_('Klíč psychologa'),
                                       error_messages={'invalid': 'Zadejte validní klíč.',
                                                       'required': '!'})  # TODO prepsat

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.label_class = 'fw-light'
        self.helper.layout = Layout(
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'birthdate',
            InlineRadios('sex'),  # not working for |crispy, use tag
            'psychologist_key',
            Div(Submit('submit', 'Registrovat se'),
                css_class='d-flex flex-column justify-content-center')
        )

    def clean_psychologist_key(self):
        psychologist_key = self.cleaned_data['psychologist_key']
        try:
            PsychologistProfile.objects.get(personal_key__exact=psychologist_key)
        except ObjectDoesNotExist:
            raise forms.ValidationError(
                _('Zadaný klíč nepatří žádnému psychologovi. \
                Pokud jste klíč od vašeho psychologa neobdržel(a), prosím, kontaktujte jej.'),
                code='invalid psychologist key',
                params={'value': psychologist_key})
        return psychologist_key

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_client = True
        user.is_active = False
        user.save()
        data = self.cleaned_data
        psychologist = PsychologistProfile.objects.get(personal_key__exact=data.get('psychologist_key'))
        ClientProfile.objects.create(user=user, user_type=user_types.CLIENT, birthdate=data.get('birthdate'),
                                     sex=data.get('sex'), psychologist=psychologist.user)
        return user


class PsychologistUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2',
                  'academic_degree_before_name', 'academic_degree_after_name',
                  'certificate']

    academic_degree_before_name = forms.ChoiceField(choices=academic_degrees.ACADEMIC_DEGREES_BEFORE_NAME,
                                                    initial=academic_degrees.NO_DEGREE,
                                                    label=_('Titul před jménem'),
                                                    required=False)
    academic_degree_after_name = forms.ChoiceField(choices=academic_degrees.ACADEMIC_DEGREES_AFTER_NAME,
                                                   initial=academic_degrees.NO_DEGREE,
                                                   label=_('Titul za jménem'),
                                                   required=False)

    certificate = forms.FileField(label=_('Certifikát'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = 'fw-light'
        self.helper.layout = Layout(
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
            'academic_degree_before_name',
            'academic_degree_after_name',
            'certificate',
            Div(Submit('submit', 'Registrovat se'),
                css_class='d-flex flex-column justify-content-center')
        )

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_psychologist = True
        user.is_active = False
        user.confirmed_by_staff = False
        user.save()
        data = self.cleaned_data
        PsychologistProfile.objects.create(user=user, user_type=user_types.PSYCHOLOGIST,
                                           academic_degree_before_name=data.get('academic_degree_before_name'),
                                           academic_degree_after_name=data.get('academic_degree_after_name'),
                                           certificate=data.get('certificate'))
        return user


class ResearcherUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
        required=False,
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.initial = {'password1': '', 'password2': ''}
        self.helper = FormHelper()
        self.helper.disable_csrf = True
        self.helper.form_tag = False
        self.helper.label_class = 'fw-light'
        self.helper.layout = Layout('first_name', 'last_name', 'email')

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_researcher = True
        user.is_active = False
        raw_password = self.Meta.model.objects.make_random_password()
        user.set_password(raw_password)
        user.save()
        # profile tabulka je v DB, ale zatim neni duvod ji vyuzit
        return user
