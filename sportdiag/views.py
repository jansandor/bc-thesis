from django.shortcuts import render, redirect, reverse
from django.views.generic.base import TemplateView, RedirectView, View
from django.views.generic import ListView, FormView, DeleteView
from django.contrib.auth.views import PasswordChangeView
from accounts.models import ClientProfile, PsychologistProfile, User
from .forms import InviteClientForm, ResponseForm
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse_lazy
import mimetypes
from django.http import HttpResponse, HttpResponseRedirect
from http import HTTPStatus
import os
from django.http import HttpResponseNotFound
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from sportdiag.models import SurveyResponseRequest
import logging

from .models import Survey, Response

LOGGER = logging.getLogger(__name__)


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


def request_survey_response(request):
    request_survey_response_email_html_template = "sportdiag/emails/request_survey_response_email.html"
    client_id = request.POST.get("client_id")
    survey_id = request.POST.get("survey_id")
    if client_id and survey_id:
        client = User.objects.get(id=client_id)  # todo try except
        client_email = client.email
        psychologist = request.user
        mail_subject = f'Sportdiag | {psychologist.__str__()} Vás žádá o vyplnění dotazníku'
        message = render_to_string(request_survey_response_email_html_template,
                                   {
                                       'psychologist_fullname': psychologist.__str__(),
                                       'survey_id': survey_id,
                                       'domain': get_current_site(request).domain,
                                   })
        email = EmailMessage(mail_subject, message, to=[client_email])
        email.content_subtype = 'html'
        try:
            email.send()
        except Exception:
            # todo logging, DRY
            messages.error(request, "Něco se pokazilo. E-mail nebyl odeslán.")
            return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)
        else:
            SurveyResponseRequest.objects.create(client_id=client_id, survey_id=survey_id)
            messages.success(request, "Responze vyžádána.")
            return HttpResponse()
        # ulozit do DB nove tabulky, ze je response requested na CID, SID
        # todo zaznam smaze az odeslani responze nebo zruseni pozadavku psychologem
        # todo misto response vyzadana disabled buttonu dat button zrusit pozadavek
        # -> smaze zaznam s tabulky survey response requests (klient dotaznik nebude moci vyplnit
        # pokud zaznam v tabulce pozadavku neexistuje

    messages.error(request, "Něco se pokazilo. E-mail nebyl odeslán.")
    return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)


class PsychologistHomeView(TemplateView):
    # todo paginace?
    template_name = 'sportdiag/home/psychologist_home.html'

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        surveys = Survey.objects.all()
        clients = ClientProfile.objects.filter(psychologist_id=user.id)
        client_user_ids = list(clients.values_list("user_id", flat=True))
        # todo solve situation, when psychologist changes survey in select!!
        # client has different pending survey response request value for different surveys...
        # but for now we have only one survey, so...
        client_ids_where_pending_survey_response_request = list(SurveyResponseRequest.objects
                                                                .filter(is_pending=True, client_id__in=client_user_ids)
                                                                .values_list("client_id", flat=True))
        context['surveys'] = surveys
        context['clients'] = clients
        context['client_ids_no_pending_request'] = [item for item in client_user_ids if
                                                    item not in client_ids_where_pending_survey_response_request]
        context['client_ids_where_pending_survey_response_request'] = client_ids_where_pending_survey_response_request
        return context


class ResearcherHomeView(TemplateView):
    # todo tabulkas daty, prokliky na answer/response detail?
    # klientovi pridat uuid?
    # v tabulce krome ostatniho interviewuuid a client uuid jako anonymni ident.?
    # export
    template_name = 'sportdiag/home/researcher_home.html'


class ClientHomeView(TemplateView):
    template_name = 'sportdiag/home/client_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['surveys'] = Survey.objects.all()
        return context


class SurveyConfirmView(TemplateView):
    template_name = "sportdiag/survey_confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uuid4"] = str(kwargs["uuid4"])
        context["response"] = Response.objects.get(interview_uuid=context["uuid4"])
        return context


class SurveyDetail(View):
    template_name = "sportdiag/survey_detail.html"

    def get(self, request, *args, **kwargs):
        # todo check jestli je zaznam v tabulce survey response requests pro client id & survey id
        # pokud ano, klient ma na home tlacitko "vyplnit"
        # pokud ne, klient je presmerovan na home a prida se message pozadavek je neplatny/byl zrusen?
        survey_id = kwargs.pop('id')
        survey = Survey.objects.get(id=survey_id)
        form = ResponseForm(survey=survey, user=request.user)
        context = {'response_form': form}
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        survey_id = kwargs.get("id")
        survey = Survey.objects.get(id=survey_id)
        form = ResponseForm(request.POST, survey=survey, user=request.user)
        context = {"response_form": form}  # , "categories": categories
        if form.is_valid():
            response = form.save()
            if response is None:
                # todo message? stane se mi to vubec nekdy?
                return redirect(reverse("sportdiag:home"))
            return redirect("sportdiag:survey_confirmation", uuid4=response.interview_uuid)
        LOGGER.info("Non valid form: <%s>", form)
        return render(request, self.template_name, context)


# todo proxy na psychologa?
# todo staff researcher required decorator/mixin
class ApprovePsychologistsView(LoginRequiredMixin, ListView):
    model = User
    paginate_by = 10
    template_name = 'sportdiag/approve_psychologists.html'
    # query jen is_active false a is_psychologist true?
    queryset = User.objects.filter(is_psychologist=True, email_verified=True, confirmed_by_staff=False, is_active=False)
    ordering = ['-date_joined']


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
