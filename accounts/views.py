from django.shortcuts import render
from django.views.generic import ListView, TemplateView, CreateView, FormView
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from .forms import ClientUserCreationForm, PsychologistUserCreationForm, ResearcherUserCreationForm, ClientChangeForm, \
    PsychologistChangeForm, ResearcherChangeForm
from .models import ClientProfile, PsychologistProfile, User
from sportdiag.models import Response
from django.shortcuts import redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from .tokens import account_activation_token_generator
from django.contrib.auth.views import PasswordResetView as DjangoPasswordResetView, \
    PasswordResetDoneView as DjangoPasswordResetDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from bp.mixins import PsychologistRequiredMixin, StaffResearcherRequiredMixin
from django.contrib import messages


class SignUpView(TemplateView):
    template_name = 'accounts/registration/signup.html'


class ClientSignUpView(CreateView):
    model = get_user_model()
    form_class = ClientUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/registration/client_signup.html'
    account_activation_token_generator = default_token_generator
    account_activation_email_html = 'accounts/registration/emails/account_activation_email.html'

    def get(self, request, *args, **kwargs):
        if 'uuid4' in kwargs:
            self.initial = {'psychologist_key': kwargs.pop('uuid4')}
        return super().get(request)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            # client registration confirm mail
            # todo dat nejak rozumne do funkce? treba send_account_confirm_email
            mail_subject = 'Sportdiag | Dokončete registraci'
            message = render_to_string(self.account_activation_email_html,
                                       {
                                           'user_fullname': user.__str__(),
                                           'domain': get_current_site(request).domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                           'token': self.account_activation_token_generator.make_token(user)
                                       })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.content_subtype = 'html'
            email.send()
            # todo add message succes/info
            return redirect(self.success_url)
        else:
            # context = self.get_context_data(**kwargs)
            return render(request, self.template_name, {'form': form})


class PsychologistSignUpView(CreateView):
    model = get_user_model()
    form_class = PsychologistUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'accounts/registration/psychologist_signup.html'
    account_activation_token_generator = default_token_generator
    account_activation_email_html = 'accounts/registration/emails/account_activation_email.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # psychologist registration confirm mail
            # in activate function is sent next mail to the staff,
            # when psych. has email confirmed
            psychologist = PsychologistProfile.objects.get(user=user)
            mail_subject = 'Sportdiag | Dokončete registraci'
            message = render_to_string(self.account_activation_email_html,
                                       {
                                           'user_fullname': psychologist.__str__(),
                                           'domain': get_current_site(request).domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                           'token': self.account_activation_token_generator.make_token(user)
                                       })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.content_subtype = 'html'
            email.send()
            # todo add message succes/info
            return redirect(self.success_url)
        else:
            return render(request, self.template_name, {'form': form})


def activate(request, uidb64, token):
    # todo mozna casem rozdelit na activate-client a activate-psych atd
    activation_confirm_template_name = 'accounts/registration/account_activation_confirm.html'
    activation_link_used_template_name = 'accounts/registration/account_activation_invalid_link.html'
    new_psychologist_registration_email_html_template = 'accounts/registration/emails/new_psychologist_registration_email.html'
    new_client_email_html_template = 'accounts/registration/emails/new_client_email.html'

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token_generator.check_token(user, token) and not user.email_verified:
        if user.is_client:
            user.email_verified = True
            user.is_active = True
            user.save()
            # mail to psychologist - new client
            mail_subject = 'Sportdiag | Nový klient'
            try:
                client = ClientProfile.objects.get(user=user)
                psychologist = User.objects.get(pk=client.psychologist_id)
            except:
                pass  # todo ?
            message = render_to_string(new_client_email_html_template,
                                       {
                                           'user_id': user.id,
                                           'user_fullname': user.__str__(),
                                           'domain': get_current_site(request).domain,
                                       })
            email = EmailMessage(mail_subject, message, to=[psychologist.email])
            email.content_subtype = 'html'
            email.send()
            # todo add message succes/info
            # user = authenticate(email=user.email, password=user.password)
            # if user is not None:
            #    login(request, user)  # login po prekliknuti stranky nedrzi
        elif user.is_psychologist:
            user.email_verified = True
            user.save()
            psychologist = PsychologistProfile.objects.get(user=user)
            mail_subject = 'Sportdiag | Registroval se nový psycholog'
            message = render_to_string(new_psychologist_registration_email_html_template,
                                       {'psychologist_fullname': psychologist.__str__(),
                                        'domain': get_current_site(request).domain,
                                        })
            admins = User.objects.filter(is_staff=True, is_researcher=True)
            for admin in admins:
                # mail to staff researchers - new psychologist to approval
                email = EmailMessage(mail_subject, message, to=[admin.email])
                email.content_subtype = 'html'
                email.send()
        elif user.is_researcher:
            user.email_verified = True
            user.is_active = True
            user.save()
        return render(request, activation_confirm_template_name, {'user': user})
    else:
        return render(request, activation_link_used_template_name)


class PasswordResetView(DjangoPasswordResetView):
    html_email_template_name = 'accounts/registration/emails/password_reset_email.html'
    email_template_name = 'accounts/registration/emails/password_reset_email.html'
    # TODO sablona, vyresit jak nastavit site_name.. pak bych nemusel sablonu menit
    # https://github.com/django/django/blob/8d9827c06ce1592cca111e7eafb9ebe0153104ef/django/contrib/auth/templates/registration/password_reset_subject.txt
    subject_template_name = 'accounts/registration/emails/password_reset_subject.txt'
    template_name = 'accounts/registration/password_reset.html'


class PasswordResetDoneView(DjangoPasswordResetDoneView):
    template_name = 'accounts/registration/password_reset_done.html'


class ResearcherCreateView(LoginRequiredMixin, StaffResearcherRequiredMixin, CreateView):
    model = get_user_model()
    form_class = ResearcherUserCreationForm
    success_url = reverse_lazy('sportdiag:researchers_overview')
    template_name = 'accounts/registration/create_researcher_account.html'
    account_activation_token_generator = default_token_generator
    account_activation_email_html = 'accounts/registration/emails/researcher_account_activation_email.html'

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            (user, password) = form.save()
            # researcher account creation confirm mail
            # todo dat nejak rozumne do funkce? treba send_account_confirm_email
            staff_researcher_user = request.user
            mail_subject = 'Sportdiag | Správce aplikace Vám vytvořil účet'
            message = render_to_string(self.account_activation_email_html,
                                       {
                                           'staff_researcher_fullname': staff_researcher_user.__str__(),
                                           'user_email': user.email,
                                           'password': password,
                                           'domain': get_current_site(request).domain,
                                           'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                           'token': self.account_activation_token_generator.make_token(user)
                                       })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.content_subtype = 'html'
            email.send()
            # todo add message succes/info
            return redirect(self.success_url)
        else:
            return render(request, self.template_name, {'form': form})


# todo prepsat login view.. pridat checkbox remember me
# todo pro psychologa hazet warning/info/alert message, pokud jeho ucet jeste nebyl schvalen adminem
# todo pro kazdeho usera hazet message, pokud nema aktivovany ucet

class ClientDetailView(LoginRequiredMixin, PsychologistRequiredMixin, ListView):
    template_name = "accounts/client_detail.html"
    model = Response
    ordering = ['-created']
    paginate_by = 2

    def get_queryset(self, user_id):
        queryset = super().get_queryset()
        queryset = queryset.filter(user_id=user_id)
        return queryset

    def get_context_data(self, **kwargs):
        user_id = kwargs.get('user_id')
        responses_qs = self.get_queryset(user_id=user_id)
        context = super().get_context_data(object_list=responses_qs, **kwargs)
        client = ClientProfile.objects.get(user_id=user_id)
        context['client'] = client
        # todo show survey response requests to psychologist
        return context

    def get(self, request, *args, **kwargs):
        kwargs.update({"page": request.GET.get("page", 1)})
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


class AccountSettingsView(LoginRequiredMixin, FormView):
    template_name = 'accounts/user_settings.html'
    success_url = 'account_settings'

    def get_initial(self):
        initial = super().get_initial()
        user = self.request.user
        initial.update({
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
        })
        if user.is_client:
            user_profile = ClientProfile.objects.get(user_id=user.id)
            initial.update({
                "birthdate": user_profile.birthdate.__str__(),
                "sex": user_profile.sex,
                "nationality": user_profile.nationality,
            })
        elif user.is_psychologist:
            user_profile = PsychologistProfile.objects.get(user_id=user.id)
            initial.update({
                "academic_degree_before_name": user_profile.academic_degree_before_name,
                "academic_degree_after_name": user_profile.academic_degree_after_name,
            })
        elif user.is_researcher:
            pass
        return initial

    def get_form_class(self):
        user = self.request.user
        if user.is_client:
            self.form_class = ClientChangeForm
        elif user.is_psychologist:
            self.form_class = PsychologistChangeForm
        elif user.is_researcher:
            self.form_class = ResearcherChangeForm
        return self.form_class

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        kwargs.update({"user": user})
        return kwargs

    def form_valid(self, form):
        form.save(user=self.request.user)
        messages.success(self.request, f"Uloženo.")
        return super().form_valid(form)

    def get_success_url(self):
        url = super().get_success_url()
        kwargs = {"pk": self.request.user.pk}
        return reverse_lazy(url, kwargs=kwargs)
