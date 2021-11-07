from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from .forms import ClientUserCreationForm, ClientProfileCreationForm, PsychologistUserCreationForm, \
    PsychologistProfileCreationForm
from .models import ClientProfile, PsychologistProfile, User
from django.shortcuts import redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth import authenticate, login
from bp import settings
from django.http import HttpResponse


class SignUpView(TemplateView):
    template_name = 'accounts/registration/signup.html'


class ClientSignUpView(TemplateView):
    user_model = get_user_model()
    profile_model = ClientProfile
    user_form_class = ClientUserCreationForm
    profile_form_class = ClientProfileCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/registration/client_signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # if self.user_form_class.is_bound():
        #    context['user_form'] = self.user_form_class
        # else:
        context['user_form'] = self.user_form_class()
        # if self.profile_form_class.is_bound():
        #    context['profile_form'] = self.profile_form_class
        # else:
        context['profile_form'] = self.profile_form_class()
        return context

    def post(self, request, *args, **kwargs):
        user_form = self.user_form_class(request.POST)
        profile_form = self.profile_form_class(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile_form.save(user=user)
            # account confirmation mail
            # todo dat nejak rozumne do funkce? treba send_account_confirm_email
            current_site = get_current_site(request)
            mail_subject = 'Sportdiag | Dokončete registraci potvrzením emailu'
            message = render_to_string('accounts/registration/emails/account_activation_email.html',
                                       {
                                           'user': user,
                                           'domain': current_site.domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                           'token': account_activation_token.make_token(user)
                                       })
            receiver = user_form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[receiver], from_email=settings.DEFAULT_FROM_EMAIL)
            email.send()
            #
            return redirect(self.success_url)
        else:  # TODO raise some error or what? return form for corrections
            context = self.get_context_data(**kwargs)
            context['user_form'] = user_form
            context['profile_form'] = profile_form
            return self.render_to_response(context)


class PsychologistSignUpView(TemplateView):
    user_model = get_user_model()
    profile_model = PsychologistProfile
    user_form_class = PsychologistUserCreationForm
    profile_form_class = PsychologistProfileCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/registration/psychologist_signup.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_form'] = self.user_form_class()
        context['profile_form'] = self.profile_form_class()
        return context

    def post(self, request, *args, **kwargs):
        user_form = self.user_form_class(request.POST)
        profile_form = self.profile_form_class(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile_form.save(user=user)
            return redirect(self.success_url)
        else:
            context = self.get_context_data(**kwargs)
            context['user_form'] = user_form
            context['profile_form'] = profile_form
            return self.render_to_response(context)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'accounts/registration/account_activation_confirm.html')
    else:
        return render(request, 'accounts/registration/invalid_account_activation_link.html')
