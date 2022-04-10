import csv
import json
import logging
import mimetypes
import os
import shutil
from datetime import datetime, timezone
from http import HTTPStatus
from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core import serializers
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.views.generic import ListView, FormView
from django.views.generic.base import TemplateView, View

import bp.settings as settings
from accounts.models import ClientProfile, PsychologistProfile, User
from accounts.utils.user.functions import user_specific_upload_dir
from sportdiag.models import SurveyResponseRequest, Answer, Question, Category
from .forms import InviteClientForm, ResponseForm, ResponsesFilterForm, UploadFilesForm
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
    if request.method == "GET":
        user = request.user
        if user.is_anonymous:
            return redirect('login')
        elif user.is_client:
            return redirect('sportdiag:home_client')
        elif user.is_psychologist:
            return redirect('sportdiag:home_psychologist')
        elif user.is_researcher:  # is_staff se poresi v sablone
            initial_survey = Survey.objects.order_by('id').first()  # todo WHAT IF NO SURVEY
            base_url = reverse('sportdiag:home_researcher')
            # query_string = urlencode({'survey_id': initial_survey.id, 'page': 1})
            query_string = urlencode({'page': 1})
            url = f'{base_url}?{query_string}'
            print("url", url)
            return redirect(url)
        else:
            return HttpResponseNotFound()


def request_survey_response(request):
    if request.method == "POST":
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
                                           # todo delete nejspis 'survey_id': survey_id,
                                           'domain': get_current_site(request).domain,
                                       })
            email = EmailMessage(mail_subject, message, to=[client_email])
            email.content_subtype = 'html'
            try:
                email.send()
            except Exception:
                # todo logging, DRY
                # messages.error(request, "Něco se pokazilo. E-mail nebyl odeslán.")
                return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)
            else:
                SurveyResponseRequest.objects.create(client_id=client_id, survey_id=survey_id)
                # todo return refreshed client_response_requests ? currently updated in JS
                # messages.success(request, "Responze vyžádána.")
                return HttpResponse(status=HTTPStatus.OK)
            # todo misto response vyzadana disabled buttonu dat button zrusit pozadavek
            # -> smaze zaznam z tabulky survey response requests (klient dotaznik nebude moci vyplnit
            # pokud zaznam v tabulce pozadavku neexistuje

    # messages.error(request, "Něco se pokazilo. E-mail nebyl odeslán.")
    return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)


class PsychologistHomeView(TemplateView):
    # todo paginace?
    template_name = 'sportdiag/home/psychologist_home_vue.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        surveys = Survey.objects.filter(is_published=True, is_deleted=False).order_by("id")
        clients = ClientProfile.objects.filter(psychologist_id=user.id)
        client_user_ids = list(clients.values_list("user_id", flat=True))
        client_response_requests = {}
        for client in clients:
            client_response_requests[client.user.id] = list(
                SurveyResponseRequest.objects
                    .filter(client_id=client.user.id, is_pending=True)
                    .values_list("survey_id", flat=True))
        context['surveys_json'] = serializers.serialize("json", surveys, fields=("name"))
        context['clients_json'] = serializers.serialize("json", User.objects.filter(id__in=client_user_ids),
                                                        fields=("first_name", "last_name"))

        context['client_response_requests_json'] = json.dumps(client_response_requests)
        return context


class ApprovePsychologistsView(LoginRequiredMixin, ListView):
    model = User
    paginate_by = 10
    template_name = 'sportdiag/approve_psychologists.html'
    # query jen is_active false a is_psychologist true?
    queryset = User.objects.filter(is_psychologist=True, email_verified=True, confirmed_by_staff=False, is_active=False)
    ordering = ['-date_joined']


class ResearcherHomeView(TemplateView):
    # todo tabulkas daty, prokliky na answer/response detail?
    # klientovi pridat uuid?
    # v tabulce krome ostatniho interviewuuid a client uuid jako anonymni ident.?
    template_name = 'sportdiag/home/researcher_home.html'
    filter_form = ResponsesFilterForm
    paginated_by = 2

    @staticmethod
    def compute_score(answers):  # todo extract method and reuse in client detail
        total_score = 0
        for i, answer in enumerate(answers):
            try:
                answer_score = int(answer)
            except ValueError:
                if answer != "":
                    answers[i] = answer.replace("-", " ")
                else:
                    answers[i] = "-"
                continue
            else:
                total_score += answer_score
        return total_score

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey_id = kwargs.get('survey_id')
        print("survey_id", survey_id)
        if not survey_id:
            survey = Survey.objects.filter(is_deleted=False).order_by('id').first()  # initial_survey
            survey_id = survey.id
        # todo error handling
        context['filter_form'] = self.filter_form(initial={'survey': survey_id})
        responses = Response.objects.filter(survey_id=survey_id).order_by("-created")
        clients = ClientProfile.objects \
            .filter(user_id__in=responses.values_list("user_id", flat=True)) \
            .order_by("user_id")
        questions_queryset = Question.objects.filter(survey_id=responses.first().survey_id).order_by("order")
        context['questions'] = [question.get_short_name() for question in questions_queryset]
        table_data = []
        counter = 1
        for response in responses:
            for client in clients:
                if client.user_id == response.user_id:
                    answers = list(Answer.objects
                                   .filter(response_id=response.id)
                                   .order_by("created")
                                   .values_list("body", flat=True))
                    score = self.compute_score(answers)
                    table_data.append({
                        "row_number": counter,
                        "created": response.created,
                        "interview_uuid": response.id,  # todo uuid?
                        "client_uuid": client.user_id,  # todo uuid?
                        "nationality": client.nationality,
                        "sex": client.sex,
                        "age": client.age,
                        "answers": answers,
                        "score": score,
                    })
                    counter += 1
        # print("table_data", table_data)
        paginator = Paginator(table_data, self.paginated_by)
        page_number = kwargs.get('page')
        print("page_number", page_number)
        page_obj = paginator.get_page(page_number)
        # context["table_data"] = Paginator
        context['page_obj'] = page_obj
        context["survey_id"] = survey_id
        return context

    def get(self, request, *args, **kwargs):
        print("request", request)
        print("kwargs", kwargs)
        page_number = request.GET.get('page')
        survey_id = request.GET.get('survey_id')
        if survey_id:
            kwargs.update({"survey_id": survey_id})
        print("kwargs after update", kwargs)
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        filter_form = self.filter_form(request.POST)
        if filter_form.is_valid():
            selected_survey = filter_form.cleaned_data['survey']
            print("selected_survey", selected_survey)
            context = self.get_context_data(survey_id=selected_survey.id)
            return render(request, self.template_name, context)
        else:
            pass
        return HttpResponse(status=HTTPStatus.INTERNAL_SERVER_ERROR)


class ClientHomeView(TemplateView):
    template_name = 'sportdiag/home/client_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        survey_response_requests_ids = SurveyResponseRequest.objects \
            .filter(client_id=user.id, is_pending=True) \
            .values_list("survey_id", flat=True)
        # todo should be only 1 active request for client per survey
        surveys = Survey.objects.filter(id__in=survey_response_requests_ids)
        context['surveys'] = surveys
        return context


class SurveyConfirmView(TemplateView):
    template_name = "sportdiag/survey_confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uuid4"] = str(kwargs.get("uuid4"))  # todo get?
        context["response"] = Response.objects.get(interview_uuid=context["uuid4"])
        return context


class SurveyDetailView(TemplateView):
    template_name = "sportdiag/survey_detail.html"
    new_response_email_html_template = "sportdiag/emails/new_response_email_html_template.html"

    def get(self, request, *args, **kwargs):
        # todo check jestli je zaznam v tabulce survey response requests pro client id & survey id
        # pokud ano, klient ma na home tlacitko "vyplnit"
        # pokud ne, klient je presmerovan na home a prida se message pozadavek je neplatny/byl zrusen?
        user = request.user
        survey_id = kwargs.get('survey_id')
        context = self.get_context_data(**kwargs)
        if user and survey_id:
            try:
                response_request = SurveyResponseRequest.objects.get(client_id=user.id, survey_id=survey_id,
                                                                     is_pending=True)
            except SurveyResponseRequest.DoesNotExist:
                # todo handle - responze uz byla vytvorena nebo byl pozadavek zrusen psychologem
                # todo pokud nastane, vratit na home a message?
                print("SurveyResponseRequest.DoesNotExist")
                pass
            except SurveyResponseRequest.MultipleObjectsReturned:
                # todo handle, nemelo by nikdy nastat!
                pass
            survey = Survey.objects.get(id=survey_id)
            form = ResponseForm(survey=survey, user=request.user)
            context = {'response_form': form, 'survey_id': survey_id}
        else:
            # todo handle, nejaky error
            pass
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        survey_id = kwargs.get("survey_id")
        survey = Survey.objects.get(id=survey_id)
        client = ClientProfile.objects.get(user_id=request.user.id)
        form = ResponseForm(request.POST, survey=survey, user=request.user)
        context = {"response_form": form}  # , "categories": categories
        if form.is_valid():
            response = form.save()
            # todo melo by vzdy vratit 1 request, handle try except
            survey_response_request = SurveyResponseRequest.objects.get(client_id=client.user_id, survey_id=survey.id,
                                                                        is_pending=True)
            survey_response_request.responded_on_date = datetime.now(timezone.utc)
            survey_response_request.is_pending = False
            survey_response_request.save()
            if response is None:
                # todo message? stane se mi to vubec nekdy?
                return redirect(reverse("sportdiag:home"))
            psychologist = User.objects.get(id=client.psychologist_id)
            mail_subject = f'Sportdiag | Nová responze'
            message = render_to_string(self.new_response_email_html_template,
                                       {
                                           'client_fullname': client.user.get_full_name(),
                                           'client_id': client.user_id,
                                           'domain': get_current_site(request).domain,
                                       })
            email = EmailMessage(mail_subject, message, to=[psychologist.email])
            email.content_subtype = 'html'
            email.send()
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

    def get(self, request, *args, **kwargs):
        psychologist = PsychologistProfile.objects.get(pk=request.user.id)
        context = self.get_context_data()
        context['psychologist'] = psychologist
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        user = request.user
        profile = PsychologistProfile.objects.get(user_id=user.id)
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
            return render(request, self.template_name, {'form': form, 'psychologist': profile})


def reject_psychologist(request, pk):
    if request.method == "POST":
        registration_rejected_email_html_template = "sportdiag/emails/psychologist_registration_rejected_email.html"
        # success_url = reverse_lazy('sportdiag:approve_psychologists')
        # todo bylo by pekne, kdyby success vracel na stranku+page, z ktere byla akce provedena
        user = User.objects.get(id=pk)
        if user:
            mail_subject = f'Sportdiag | Vaše registrace byla zamítnuta správcem'
            message = render_to_string(registration_rejected_email_html_template,
                                       {
                                           'domain': get_current_site(request).domain,
                                       })
            email = EmailMessage(mail_subject, message, to=[user.email])
            email.content_subtype = 'html'
            email.send()
            user_uploaded_files_dir_path = settings.MEDIA_ROOT / user_specific_upload_dir(user=user)
            if os.path.exists(user_uploaded_files_dir_path):
                shutil.rmtree(user_uploaded_files_dir_path)  # todo onerror logging
            user.delete()
            return redirect(request.META.get('HTTP_REFERER'))  # redirect('sportdiag:approve_psychologists')


def approve_psychologist(request, pk):
    if request.method == "POST":
        # uzivatel urcite existuje, proklik je z listu useru, co existuji
        # a neni verejna url, ktera by sla zmenit
        # presto, pokud o url patternu vim, muzu pk zmenit
        # todo ochrana checkem, jestli user existuje? 5/3/22 neni nutna? jinak by P nebyl v tabulce
        # todo --> url/view ma pristupnou pouze staff researcher
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
    if request.method == "GET":
        user = PsychologistProfile.objects.get(user_id=pk)
        filepath = user.certificate.path
        filename = os.path.basename(user.certificate.name)
        file = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(file, content_type=mime_type)
        response['Content-Disposition'] = f"attachment; filename={filename}"
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
    if request.method == "POST":
        researcher_account_deactivated_email_html_template = "sportdiag/emails/researcher_account_deactivated_email.html"
        researcher = User.objects.get(id=pk)
        researcher.is_active = False
        researcher.save()
        mail_subject = f'Sportdiag | Váš účet byl deaktivován správcem'
        message = render_to_string(researcher_account_deactivated_email_html_template)
        email = EmailMessage(mail_subject, message, to=[researcher.email])
        email.content_subtype = 'html'
        email.send()
        return redirect(request.META.get('HTTP_REFERER'))


def reactivate_researcher_account(request, pk):
    if request.method == "POST":
        researcher_account_reactivated_email_html_template = "sportdiag/emails/researcher_account_reactivated_email.html"
        researcher = User.objects.get(id=pk)
        researcher.is_active = True
        researcher.save()
        mail_subject = f'Sportdiag | Váš účet byl znovu aktivován správcem'
        message = render_to_string(researcher_account_reactivated_email_html_template,
                                   {
                                       'domain': get_current_site(request).domain,
                                   })
        email = EmailMessage(mail_subject, message, to=[researcher.email])
        email.content_subtype = 'html'
        email.send()
        return redirect(request.META.get('HTTP_REFERER'))


class SurveysAndManualsView(TemplateView):
    template_name = "sportdiag/surveys_and_manuals.html"
    upload_survey_attachments_form = UploadFilesForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upload_attachments_form'] = self.upload_survey_attachments_form()
        surveys = Survey.objects.filter(is_deleted=False).order_by('id')
        user = kwargs.get("user")
        if user and user.is_psychologist:
            surveys = surveys.filter(is_published=True)
        context['surveys'] = surveys
        surveys_attachments = {}
        for survey in surveys:
            attachments_dir_path = get_survey_attachments_upload_dir_path(survey)
            attachments_names = os.listdir(attachments_dir_path)
            surveys_attachments[survey.id] = attachments_names
        context['surveys_attachments'] = surveys_attachments
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(user=request.user)
        return render(request, self.template_name, context)


def get_survey_attachments_upload_dir_path(survey):
    survey_media_dir_path = settings.MEDIA_ROOT / 'sportdiag/surveys' / f'survey_{survey.id}'
    if not os.path.exists(survey_media_dir_path):
        os.mkdir(survey_media_dir_path)
    survey_attachments_dir_path = survey_media_dir_path / 'attachments'
    if not os.path.exists(survey_attachments_dir_path):
        os.mkdir(survey_attachments_dir_path)
    return survey_attachments_dir_path


def handle_uploaded_file(file, attachments_dir_path):
    file_dest_path = attachments_dir_path / file.name  # todo ? .replace(" ", "_")
    # todo handle filename collisions, now file is overwritten
    with open(file_dest_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)


def upload_survey_attachments(request, **kwargs):
    if request.method == 'POST':
        form = UploadFilesForm(request.POST, request.FILES)
        files = request.FILES.getlist('file_field')
        survey_id = kwargs.get('survey_id')
        survey = Survey.objects.get(id=survey_id)
        attachments_dir_path = get_survey_attachments_upload_dir_path(survey)
        if form.is_valid():
            for f in files:
                handle_uploaded_file(f, attachments_dir_path)
            messages.success(request, f"Přílohy nahrány.")
            return redirect('sportdiag:surveys_manuals')
        # todo message error?
        messages.error(request, "Příloha nebyla nahrána.")
        return redirect('sportdiag:surveys_manuals')


def download_survey_attachment(request, survey_id, filename):
    if request.method == "GET":
        survey = Survey.objects.get(id=survey_id)
        attachments_dir_path = get_survey_attachments_upload_dir_path(survey)
        file_path = attachments_dir_path / filename
        if not os.path.exists(file_path):
            messages.error(request, "Příloha nenalezena.")
            return redirect('sportdiag:surveys_manuals')
        else:
            file = open(file_path, 'rb')
            mime_type, _ = mimetypes.guess_type(file_path)
            response = HttpResponse(file, content_type=mime_type)
            response['Content-Disposition'] = f"attachment; filename={filename}"
        return response


def delete_survey_attachment(request, survey_id, filename):
    if request.method == "POST":
        survey = Survey.objects.get(id=survey_id)
        attachments_dir_path = get_survey_attachments_upload_dir_path(survey)
        file_path = f"{attachments_dir_path}/{filename}"
        if os.path.exists(file_path):
            os.remove(file_path)
            messages.success(request, f"Příloha smazána.")
        else:
            messages.error(request, "Příloha nenalezena.")
        return redirect('sportdiag:surveys_manuals')


# todo 3rd time used same code block
def compute_score(answers):  # todo extract method and reuse in client detail
    total_score = 0
    for i, answer in enumerate(answers):
        try:
            answer_score = int(answer)
        except ValueError:
            if answer != "":
                answers[i] = answer.replace("-", " ")
            else:
                answers[i] = ""
            continue
        else:
            total_score += answer_score
    return total_score


def export_survey_responses_to_csv(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    filename = f"odpovedi_{datetime.now(timezone.utc).date()}_{survey.short_name}.csv".replace(" ", "_").replace("-",
                                                                                                                 "_")
    # todo survey short name
    responses = Response.objects.filter(survey_id=survey.id).order_by("-created")
    clients = ClientProfile.objects \
        .filter(user_id__in=responses.values_list("user_id", flat=True)) \
        .order_by("user_id")
    questions_queryset = Question.objects.filter(survey_id=responses.first().survey_id).order_by("order")
    questions = [question.get_short_name() for question in questions_queryset]

    http_response = HttpResponse(content_type='text/csv',
                                 headers={'Content-Disposition': f'attachment; filename="{filename}"'})
    writer = csv.writer(http_response)
    writer.writerow(
        ['#', 'Dotazník', 'Datum responze', 'ID Responze', 'ID Klienta', 'Státní příslušnost', 'Pohlaví',
         'Věk', *questions, 'Skóre'])
    counter = 1
    for response in responses:
        for client in clients:
            if client.user_id == response.user_id:
                print("response.created.__str__()", datetime.fromisoformat(response.created.__str__()))
                answers = list(Answer.objects
                               .filter(response_id=response.id)
                               .order_by("created")
                               .values_list("body", flat=True))
                score = compute_score(answers)
                # todo uuid? user, response
                response_created = datetime.fromisoformat(response.created.__str__())
                writer.writerow(
                    [f'{counter}', f'{survey.short_name}', f'{response_created.strftime("%Y-%m-%d %H:%M:%S")}',
                     f'{response.id}', f'{client.user_id}', f'{client.nationality}', f'{client.sex}', f'{client.age}',
                     *answers, f'{score}'])
                counter += 1
    return http_response


def toggle_is_published(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    if survey:
        survey.is_published = not survey.is_published
        survey.save()
    else:
        messages.error(request, "Dotazník nenalezen.")
    return redirect("sportdiag:surveys_manuals")


# performs soft delete
def delete_survey(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    if survey:
        survey.is_deleted = True
        survey.deleted_date = datetime.now(timezone.utc)
        survey.save()
    else:
        messages.error(request, "Dotazník nenalezen.")
    return redirect("sportdiag:surveys_manuals")


likert_scale_values_text = [
    "",
    "rozhodně nesouhlasím",
    "nesouhlasím",
    "spíše nesouhlasím",
    "ani nesouhlasím/ani souhlasím",
    "spíše souhlasím ",
    "souhlasím",
    "rozhodně souhlasím",
]


class ResponseDetailView(TemplateView):
    template_name = "sportdiag/response_detail.html"

    @staticmethod
    def get_answer_body(answer):
        try:
            int(answer)
        except ValueError:
            if answer != "":
                answer = answer.replace("-", " ")
            else:
                answer = "-"
        return answer

    @staticmethod
    def get_answer_int(answer_body):
        try:
            answer_value = int(answer_body)
        except ValueError:
            return 0
        return answer_value

    @staticmethod
    def compute_score(answers):  # todo extract method and reuse in researchers home
        total_score = 0
        for i, answer in enumerate(answers):
            try:
                answer_score = int(answer)
            except ValueError:
                if answer != "":
                    answers[i] = answer.replace("-", " ")
                else:
                    answers[i] = "-"
                continue
            else:
                total_score += answer_score
        return total_score

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response = Response.objects.get(id=kwargs.get("response_id"))
        client = ClientProfile.objects.get(user_id=response.user_id)
        survey = Survey.objects.get(id=response.survey_id)
        context["response"] = response
        context["client"] = client
        context["survey"] = survey
        categories = survey.non_empty_categories()
        print("categories", categories)
        categories_data = []
        response_total_score = 0
        for category in categories:
            cat_score = 0
            questions_data = []
            cat_questions = Question.objects.filter(category_id=category.id).order_by("number")
            for question in cat_questions:
                answer = Answer.objects.get(response_id=response.id, question_id=question.id)
                cat_score += self.get_answer_int(answer.body)
                answer_text = ""
                if question.type == Question.LIKERT_SCALE:
                    answer_text = likert_scale_values_text[self.get_answer_int(answer.body)]
                if answer_text == "":
                    answer_text = self.get_answer_body(answer)
                question_data = {
                    "question_tag": question.get_short_name(),
                    "required": question.required,
                    "question_text": question.text,
                    "answer_text": answer_text,
                    "answer_score": self.get_answer_int(answer.body)
                }
                questions_data.append(question_data)
            categories_data.append({
                "category_name": category.name,
                "questions_data": questions_data,
                "category_score": cat_score,
            })
            response_total_score += cat_score
        context["categories"] = categories_data
        context["response_total_score"] = response_total_score
        print("categories", categories_data)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)
