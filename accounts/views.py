from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from .forms import ClientUserCreationForm, ClientProfileCreationForm, PsychologistSignUpForm
from .models import ClientProfile
from django.shortcuts import redirect


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
        context['user_form'] = self.user_form_class
        context['profile_form'] = self.profile_form_class
        return context

    def post(self, request, *args, **kwargs):
        user_form = self.user_form_class(request.POST)
        profile_form = self.profile_form_class(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile_form.save(user=user)
            return redirect(self.success_url)
        else:
            return redirect('signup')


class PsychologistSignUpView(CreateView):
    model = get_user_model()
    form_class = PsychologistSignUpForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/registration/psychologist_signup.html'
