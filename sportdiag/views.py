from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import ListView, FormView, DeleteView
from accounts.models import ClientProfile, PsychologistProfile, User
from .forms import InviteClientForm
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse_lazy
import mimetypes
from django.http import HttpResponse
import os


class IndexView(TemplateView):
    template_name = 'sportdiag/index.html'


class ContactView(TemplateView):
    template_name = 'sportdiag/contact.html'


class BeneficiariesView(TemplateView):
    template_name = 'sportdiag/beneficiaries.html'


# psychologist home view
class HomePageView(ListView):
    model = ClientProfile  # spis user?
    # paginate_by = 10
    template_name = 'sportdiag/home.html'
    ordering = ['-last_name']

    # todo home view je jen rozcestnik/redirect na psychologist/client/researcher home
    def get_queryset(self):
        return ClientProfile.objects.filter(psychologist=self.request.user)


# todo proxy na psychologa?
# todo staff researcher required decorator/mixin
class ApprovePsychologistsView(ListView):
    model = User
    # paginate_by = 10
    template_name = 'sportdiag/approve_psychologists.html'
    # query jen is_active false a is_psychologist true?
    queryset = User.objects.filter(is_psychologist=True, email_verified=True, confirmed_by_staff=False, is_active=False)
    ordering = ['-date_joined']


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
            return redirect('sportdiag:home')
        else:
            return render(request, self.template_name, {'form': form})


class RejectPsychologist(DeleteView):
    model = User
    # todo message uspesne smazano/zamitnuto
    # todo send mail
    template_name = 'sportdiag/reject_psychologist_confirm.html'
    success_url = reverse_lazy('sportdiag:approve_psychologists')


def approve_psychologist(request, pk):
    # uzivatel urcite existuje, proklik je z listu useru, co existuji..
    # a neni verejna url, ktera by sla zmenit
    # i presto, pokud o url patternu vim, muzu pk zmenit
    # ochrana checkem, jestli user existuje?
    user = User.objects.get(id=pk)
    user.confirmed_by_staff = True
    user.is_active = True
    user.save()
    # todo message uspesne schvaleno
    # todo send mail
    return redirect('sportdiag:approve_psychologists')


def download_certificate(request, pk):
    user = PsychologistProfile.objects.get(user_id=pk)
    filepath = user.certificate.path
    filename = os.path.basename(user.certificate.name)
    file = open(filepath, 'rb')
    mime_type, _ = mimetypes.guess_type(filepath)
    response = HttpResponse(file, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response
