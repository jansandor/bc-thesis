from django import forms
from crispy_forms.helper import FormHelper
from django.utils.translation import gettext_lazy as _
from crispy_forms.layout import Submit, Layout, Div
from accounts.models import User
from django.core.exceptions import ObjectDoesNotExist


class InviteClientForm(forms.Form):
    class Meta:
        fields = ['client_email']

    client_email = forms.EmailField(label=_('E-mail klienta'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def clean_client_email(self):
        client_email = self.cleaned_data['client_email']
        try:
            client = User.objects.get(email=client_email)
        except ObjectDoesNotExist:
            # todo spolihat v logice kodu na vyjimku je dost na prase.. vymyslet lip
            return client_email
        raise forms.ValidationError(
            _('Uživatel s tímto e-mailem je již registrován.'),
            code='invalid client_email',
            params={'value': client_email})
