from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.db import transaction
from django.forms import ModelForm
from django import forms
from accounts.models import ClientProfile, PsychologistProfile
from django.utils.translation import gettext_lazy as _
import datetime
from datetime import datetime as dt
from django.core.exceptions import ObjectDoesNotExist

from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import InlineRadios, FormActions
from crispy_forms.layout import Layout, Submit, Field, Div, HTML

from accounts.utils.forms import DateInput
from accounts.utils.user import user_types, sex_choices, academic_degrees, nationality


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
                  'birthdate', 'sex', 'psychologist_key', 'terms_accepted']

    birthdate = forms.DateField(widget=DateInput(attrs={'min': datetime.date(dt.today().year - 100, 1, 1).__str__(),
                                                        'max': dt.today().date().__str__()}),
                                label=_('Datum narození'))
    sex = forms.ChoiceField(widget=forms.RadioSelect(), choices=sex_choices.SEX_CHOICES, initial=sex_choices.NOTSET,
                            label=_('Pohlaví'))
    nationality = forms.ChoiceField(choices=nationality.CHOICES, initial=nationality.CZE, label=_('Státní příslušnost'))
    psychologist_key = forms.UUIDField(label=_('Klíč psychologa'),
                                       error_messages={'invalid': 'Zadejte validní klíč.',
                                                       'required': '!'})  # TODO prepsat error podle docs
    terms_accepted = forms.BooleanField(label=_('Souhlasím s účastí ve výzkumu a se zpracováním osobních údajů'),
                                        required=True)

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
            'nationality',
            'psychologist_key',
            'terms_accepted',
            HTML("""<button type="button" class="btn btn-sm btn-secondary mb-3" data-bs-toggle="modal" 
                data-bs-target="#termsOfUseDetailModal">Zobrazit souhlas</button>"""),
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
                                     sex=data.get('sex'), psychologist=psychologist.user,
                                     terms_accepted=data.get('terms_accepted'), nationality=data.get('nationality'))
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
        return user, raw_password


class UserChangeBaseForm(forms.Form):
    first_name = forms.CharField(label="Jméno", max_length=150)
    last_name = forms.CharField(label="Příjmení", max_length=150)
    email = forms.EmailField(label="E-mail")
    fields = ['first_name', 'last_name', 'email']

    def get_layout_fields(self):
        return self.fields

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.label_class = 'fw-light'
        layout_fields = self.get_layout_fields()
        self.helper.layout = Layout(
            *layout_fields,
            FormActions(Submit('submit', 'Uložit'),
                        css_class='d-flex flex-column justify-content-center')
        )

    def save(self, user):
        data = self.cleaned_data
        user.first_name = data.get("first_name")
        user.last_name = data.get("last_name")
        user.email = data.get("email")
        user.save()
        return user


class ClientChangeForm(UserChangeBaseForm):
    # TODO share somehow ClientUserCreationForm
    birthdate = forms.DateField(widget=DateInput(attrs={'min': datetime.date(dt.today().year - 100, 1, 1).__str__(),
                                                        'max': dt.today().date().__str__()}),
                                label=_('Datum narození'))
    sex = forms.ChoiceField(widget=forms.RadioSelect(), choices=sex_choices.SEX_CHOICES, initial=sex_choices.NOTSET,
                            label=_('Pohlaví'))
    nationality = forms.ChoiceField(choices=nationality.CHOICES, initial=nationality.CZE, label=_('Státní příslušnost'))
    fields = ['birthdate', 'sex', 'nationality']

    @transaction.atomic
    def save(self, user):
        super().save(user=user)
        data = self.cleaned_data
        profile = ClientProfile.objects.get(user_id=user.id)
        profile.birthdate = data.get("birthdate")
        profile.sex = data.get("sex")
        profile.nationality = data.get("nationality")
        profile.save()


class PsychologistChangeForm(UserChangeBaseForm):
    # TODO share somehow PsychologistUserCreationForm
    academic_degree_before_name = forms.ChoiceField(choices=academic_degrees.ACADEMIC_DEGREES_BEFORE_NAME,
                                                    initial=academic_degrees.NO_DEGREE,
                                                    label=_('Titul před jménem'),
                                                    required=False)
    academic_degree_after_name = forms.ChoiceField(choices=academic_degrees.ACADEMIC_DEGREES_AFTER_NAME,
                                                   initial=academic_degrees.NO_DEGREE,
                                                   label=_('Titul za jménem'),
                                                   required=False)
    fields = ['academic_degree_before_name', 'academic_degree_after_name']

    @transaction.atomic
    def save(self, user):
        super().save(user=user)
        data = self.cleaned_data
        profile = PsychologistProfile.objects.get(user_id=user.id)
        profile.academic_degree_before_name = data.get("academic_degree_before_name")
        profile.academic_degree_after_name = data.get("academic_degree_after_name")
        profile.save()


class ResearcherChangeForm(UserChangeBaseForm):
    pass
