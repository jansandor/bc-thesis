from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic import ListView, FormView, DeleteView
from django.contrib.auth.views import PasswordChangeView
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
from django.http import HttpResponseNotFound
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required


class IndexView(TemplateView):
    template_name = 'sportdiag/index.html'


class ContactView(TemplateView):
    template_name = 'sportdiag/contact.html'


class BeneficiariesView(TemplateView):
    template_name = 'sportdiag/beneficiaries.html'


# login required mixin/decorator
def redirect_to_user_type_home(request):
    user = request.user
    if user.is_anonymous:
        return redirect('login')
    elif user.is_client:
        return redirect('sportdiag:home_client')
    elif user.is_psychologist:
        return redirect('sportdiag:home_psychologist')
    elif user.is_researcher:  # is_staff se poresi v sablone
        return redirect('sportdiag:home_researcher')
    else:
        return HttpResponseNotFound()


# todo template view...
class PsychologistHomeView(ListView):
    model = ClientProfile  # spis user?
    # paginate_by = 10
    template_name = 'sportdiag/home/psychologist_home.html'
    ordering = ['last_name']

    def get_queryset(self):
        return ClientProfile.objects.filter(psychologist=self.request.user)


class ResearcherHomeView(TemplateView):
    template_name = 'sportdiag/home/researcher_home.html'


class ClientHomeView(TemplateView):
    template_name = 'sportdiag/home/client_home.html'


# todo proxy na psychologa?
# todo staff researcher required decorator/mixin
class ApprovePsychologistsView(LoginRequiredMixin, ListView):
    model = User
    paginate_by = 10
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
    # todo send mail psychologovi - registrace zamitnuta -- prepsat kvuli tomu delete view/napsat vlastni?
    template_name = 'sportdiag/reject_psychologist_confirm.html'
    success_url = reverse_lazy('sportdiag:approve_psychologists')
    # todo bylo by pekne, kdyby success vracel na stranku+page, z ktere byla akce provedena
    # def get(self, request, *args, **kwargs):
    #    self.object = self.get_object()
    #    context = self.get_context_data(object=self.object, success_url=self.request.META.get('HTTP_REFERER'))
    #    return self.render_to_response(context)

    # def get_success_url(self):
    #     c = self.get_context_data()
    #     return c


def approve_psychologist(request, pk):
    # uzivatel urcite existuje, proklik je z listu useru, co existuji
    # a neni verejna url, ktera by sla zmenit
    # presto, pokud o url patternu vim, muzu pk zmenit
    # todo ochrana checkem, jestli user existuje?
    registration_approved_email_html_template = 'sportdiag/emails/psychologist_registration_approved_email.html'

    user = User.objects.get(id=pk)
    user.confirmed_by_staff = True
    user.is_active = True
    user.save()
    # todo message uspesne schvaleno
    mail_subject = f'Sportdiag | Vaše registrace byla schválena správcem'
    message = render_to_string(registration_approved_email_html_template,
                               {
                                   'domain': get_current_site(request).domain,
                               })
    email = EmailMessage(mail_subject, message, to=[user.email])
    email.content_subtype = 'html'
    email.send()
    return redirect(request.META.get('HTTP_REFERER'))  # redirect('sportdiag:approve_psychologists')


def download_certificate(request, pk):
    user = PsychologistProfile.objects.get(user_id=pk)
    filepath = user.certificate.path
    filename = os.path.basename(user.certificate.name)
    file = open(filepath, 'rb')
    mime_type, _ = mimetypes.guess_type(filepath)
    response = HttpResponse(file, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


class ResearchersOverviewView(ListView):
    model = User
    paginate_by = 10
    template_name = 'sportdiag/researchers_overview.html'

    def get_queryset(self):
        """ returns all researchers excluding logged in (staff) researcher """
        queryset = super().get_queryset()
        current_user = self.request.user
        queryset = queryset.filter(is_researcher=True).difference(User.objects.filter(id=current_user.id)).order_by(
            '-date_joined')
        return queryset


def deactivate_researcher_account(request, pk):
    # todo mail vyzkumnikovi, ze ucet byl deaktivovan
    # todo na FE confirm popup
    researcher = User.objects.get(id=pk)
    researcher.is_active = False
    researcher.save()
    return redirect(request.META.get('HTTP_REFERER'))


def reactivate_researcher_account(request, pk):
    # todo mail vyzkumnikovi, ze ucet byl reaktivovan
    # todo na FE confirm popup
    researcher = User.objects.get(id=pk)
    researcher.is_active = True
    researcher.save()
    return redirect(request.META.get('HTTP_REFERER'))
