from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from .forms import ClientUserCreationForm, ClientProfileCreationForm, PsychologistUserCreationForm, \
    PsychologistProfileCreationForm
from .models import ClientProfile, PsychologistProfile
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
        context['user_form'] = self.user_form_class()
        context['profile_form'] = self.profile_form_class()
        return context

    def post(self, request, *args, **kwargs):
        user_form = self.user_form_class(request.POST)
        profile_form = self.profile_form_class(request.POST)
        # todo na ifu to spadne, protoze profile form nei valid
        # todo asi vadi, ze query set na psychologa je pres proxy
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile_form.save(user=user)
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
