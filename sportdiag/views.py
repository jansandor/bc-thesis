from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import ListView, FormView
from accounts.models import ClientProfile, PsychologistProfile, User
from .forms import InviteClientForm
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site


class IndexView(TemplateView):
    template_name = 'sportdiag/index.html'


class ContactView(TemplateView):
    template_name = 'sportdiag/contact.html'


class BeneficiariesView(TemplateView):
    template_name = 'sportdiag/beneficiaries.html'


# psychologist home view
class HomePageView(ListView):
    model = ClientProfile
    paginate_by = 10
    template_name = 'sportdiag/home.html'
    # todo je jen rozcestnik/redirect na psychologist/client/researcher home


# todo client home view
# todo psychologist home view
# todo researcher home view

class InviteClient(FormView):
    form_class = InviteClientForm
    success_url = 'home'
    template_name = 'sportdiag/invite_client.html'
    invite_email_html_template = 'sportdiag/emails/invite_client_email.html'

    # def get_context_data(self, **kwargs):
    #    context = super().get_context_data(**kwargs)

    def get(self, request, *args, **kwargs):
        psychologist = PsychologistProfile.objects.get(pk=request.user.id)
        context = self.get_context_data()
        context['psychologist'] = psychologist
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user = request.user
        profile = PsychologistProfile.objects.get(user=user)
        if form.is_valid():
            client_email = form.cleaned_data.get('client_email')
            mail_subject = f'Sportdiag | {profile.__str__()} Vás zve k registraci do aplikace Sportdiag'
            message = render_to_string(self.invite_email_html_template,
                                       {
                                           'psychologist_fullname': profile.__str__(),
                                           'psychologist_key': profile.personal_key,
                                           'domain': get_current_site(request).domain,
                                       })
            email = EmailMessage(mail_subject, message, to=[client_email])
            email.content_subtype = 'html'
            email.send()
            # todo message, ze email byl odeslan
            return redirect('home')
        else:
            return render(request, self.template_name, {'form': form})
