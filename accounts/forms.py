from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm as DjangoUserCreationForm
from django.db import transaction
from django.forms import ModelForm
from django import forms
from .models import ClientProfile, PsychologistProfile
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from .user_types import CLIENT, PSYCHOLOGIST


# TODO odstranit zbytecne naroky na tvorbu hesla
# TODO pokud klient nebude muset vybrat psychologa (coz by teoreticky mel povinne), tak nevim, jestli to je ok takto
# pokud psychologa bude must vybrat a treba to bude random user (teoreticky by nemel byt random, protoze by se o appce
# mel dovedet prave od psychologa), tak  by mohl vybrat treba spatneho, ne sveho, jen aby se zaregistroval
# melo by byt tedy implementovano neco jako ze klientova registrace bude dokoncena, az ji psycholog schvali

# TODO validace data narozeni, lepsi widget (bootstrap, datepicker)
# https://docs.djangoproject.com/en/3.2/ref/settings/#date-input-formats

class UserCreationForm(DjangoUserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'form-control'}),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password',
                                          'class': 'form-control'}),
    )

    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control',
                                                 'autofocus': 'true'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control',
                                             'autofocus': 'false'}),  # autofocus toto neprepise v html
        }


class ClientUserCreationForm(UserCreationForm):
    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_client = True
        user.save()
        return user


class ClientProfileCreationForm(ModelForm):
    """ Zajisti vytvoreni klientskeho profilu pri registraci uzivatele"""
    psychologist = forms.ModelChoiceField(queryset=PsychologistProfile.objects.all(),
                                          label=_('Váš psycholog'), required=False)

    class Meta:
        model = ClientProfile
        fields = ['birthdate', 'sex', 'psychologist']
        widgets = {
            'birthdate': forms.SelectDateWidget(
                years=range(datetime.utcnow().year - 100, datetime.utcnow().year + 1))
        }

        def save(self, commit=True, user=None):
            # if user is None:
            #    raise some error
            data = self.cleaned_data
            profile = ClientProfile.objects.create(user=user, user_type=CLIENT, birthdate=data['birthdate'],
                                                   sex=data['sex'],
                                                   psychologist=data['psychologist'])
            return profile


class PsychologistSignUpForm(ModelForm):
    # pridat tituly a certifikat
    # nebo udelat custom form kde zpracuju custom usera i profil
    # certificate = forms.FileField(label='Certifikát', allow_empty_file=True) # empty file ppotom na false

    # Psycholog musi uvest jmeno povinne (zobrazuje se totiz klientovi, kdyz ma vybraneho psychologa)
    # first_name = forms.CharField(label=_('Jméno'), max_length=60, required=True) # musi zustat 60 kvuli DB modelu
    # last_name = forms.CharField(label=_('Příjmení'), max_length=60, required=True)
    # zjistil jsem, ze i uzivatel by mel jmeno vyplnit.. zobrazuje se psychologum...

    # class Meta:
    #     model = CustomUser
    #     fields = ('first_name', 'last_name', 'email')

    """ Zajisti vytvoreni profilu psychologa pri registraci uzivatele"""

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_psychologist = True
        user.save()
        # Profile.objects.create(user=user, user_type=PSYCHOLOGIST)
        return user
