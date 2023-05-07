import csv
import json
import logging
import mimetypes
import os
import shutil
from datetime import datetime, timezone
from dateutil import tz
from http import HTTPStatus

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core import serializers
from django.core.mail import EmailMessage
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.views.generic import ListView, FormView
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test

import bp.settings.development as settings
from accounts.models import ClientProfile, PsychologistProfile, User
from accounts.utils.user.functions import user_specific_upload_dir
from sportdiag.models import SurveyResponseRequest
from .forms import InviteClientForm, ResponseForm, ResponsesFilterForm, UploadFilesForm
from .models import Survey, Response
from bp.decorators import user_is_psychologist, user_is_researcher, user_is_staff_researcher, \
    user_is_psychologist_or_researcher
from bp.mixins import ClientRequiredMixin, PsychologistRequiredMixin, ResearcherRequiredMixin, \
    StaffResearcherRequiredMixin, PsychologistOrResearcherRequiredMixin

LOGGER = logging.getLogger(__name__)


class IndexView(TemplateView):
    template_name = 'sportdiag/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)


@login_required
def redirect_to_user_type_home(request):
    if request.method == "GET":
        user = request.user
        if user.is_client:
            return redirect('sportdiag:home_client')
        elif user.is_psychologist:
            return redirect('sportdiag:home_psychologist')
        elif user.is_researcher:  # is_staff se poresi v sablone
            return redirect('sportdiag:home_researcher')
        else:
            return HttpResponseNotFound()


@user_passes_test(user_is_psychologist)
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
                # todo nefunguje jak by melo - pro zobrazeni msg je nutne udelat new request... messages.error(request, "Něco se pokazilo. E-mail nebyl odeslán.")
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


class PsychologistHomeView(LoginRequiredMixin, PsychologistRequiredMixin, TemplateView):
    template_name = 'sportdiag/home/psychologist_home_vue.html'
    paginate_by = 5

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
        filtered_clients = User.objects.filter(id__in=client_user_ids).order_by(
            'last_name', 'first_name')
        context['surveys_json'] = serializers.serialize("json", surveys, fields=("name"))
        context['client_response_requests_json'] = json.dumps(client_response_requests)
        filtered_clients = list(filtered_clients.values("pk", "first_name", "last_name"))
        for i in range(filtered_clients.__len__()):
            filtered_clients[i]["detail_url"] = reverse('client_detail',
                                                        kwargs={'user_id': filtered_clients[i]["pk"], "page": 1})
        paginator = Paginator(filtered_clients, self.paginate_by)
        requested_page_number = kwargs.get("page", 1)
        page = paginator.page(requested_page_number)
        context['clients_paginated'] = json.dumps({
            "items": page.object_list,
            "items_total": paginator.count,
            "page_number": page.number,
            "pages_total": paginator.num_pages,
            "has_next_page": page.has_next(),
            "has_previous_page": page.has_previous(),
            # next page number
            # prev page number from page object
        })
        return context

    def get(self, request, *args, **kwargs):
        kwargs.update({"page": request.GET.get("page", 1)})
        context = self.get_context_data(**kwargs)
        return render(request, self.template_name, context)


class ResearcherHomeView(LoginRequiredMixin, ResearcherRequiredMixin, TemplateView):
    template_name = 'sportdiag/home/researcher_home_vue.html'
    filter_form = ResponsesFilterForm
    paginate_by = 30

    # todo filter form no longer used - remove from forms.py?

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        survey_id = kwargs.get('survey_id')
        survey = Survey.objects.get(id=survey_id)
        responses = Response.objects.filter(survey_id=survey_id).order_by("-created").select_related()
        table_data = []
        counter = 1
        # todo questions are ordered by order number, answers are ordered by 'created'
        # todo will always answer body/score match right Q column in table? It seems so
        for response in responses:
            client = ClientProfile.objects.get(user_id=response.user_id)
            answers = response.answers.order_by("created").select_related('question').values('question_id',
                                                                                             'question__number', 'body',
                                                                                             'score')
            table_data.append({
                "row_number": counter,
                "created": response.created.astimezone(tz=tz.tzlocal()).strftime("%Y-%m-%d %H:%M"),
                "response_id": response.id,
                "interview_uuid": str(response.interview_uuid),
                "response_detail_url": response.get_absolute_url(),
                "client_uuid": client.user_id,  # todo uuid?
                "nationality": client.nationality,
                "sex": client.sex,
                "age": client.age,
                "answers": list(answers),
                "score": response.total_score,
                "max_score": response.max_score,
            })
            counter += 1
        context["export_survey_responses_csv_request_path"] = reverse('sportdiag:export_survey_responses_to_csv',
                                                                      kwargs={"survey_id": survey_id})
        context['questions'] = list(
            survey.questions.order_by("order").values("number", "text", "pk", "required"))
        context['surveys'] = list(Survey.objects.filter(is_deleted=False).values('pk', 'name'))
        paginator = Paginator(table_data, self.paginate_by)
        requested_page_number = kwargs.get("page", 1)
        page = paginator.page(requested_page_number)
        context['responses'] = {
            "items": page.object_list,
            "items_total": paginator.count,
            "pages_total": paginator.num_pages,
            "has_next_page": page.has_next(),
            "has_previous_page": page.has_previous(),
        }
        return context

    def post(self, request, *args, **kwargs):
        filter_form = self.filter_form(request.POST)
        if filter_form.is_valid():
            selected_survey = filter_form.cleaned_data['survey']
            # todo improve code below?
            if selected_survey is None:
                context = self.get_context_data(survey_id=selected_survey)
            else:
                context = self.get_context_data(survey_id=selected_survey.id)
            return render(request, self.template_name, context)
        return redirect("sportdiag:home")

    def is_ajax(self, request):
        return request.headers.get("X-Requested-With") == "XMLHttpRequest"

    def get(self, request, *args, **kwargs):
        survey_id = request.GET.get("survey_id", None)
        if survey_id is None:
            survey = Survey.objects.order_by("id").first()
            if survey:
                survey_id = survey.id
            else:
                context = {"no_data": True}
                return render(request, self.template_name, context)
        kwargs.update({"survey_id": survey_id})
        kwargs.update({"page": request.GET.get("page", 1)})
        context = self.get_context_data(**kwargs)
        if self.is_ajax(request):
            # return only necessary data for table change
            data = {
                "export_survey_responses_csv_request_path": context.get("export_survey_responses_csv_request_path",
                                                                        None),
                "questions": context.get("questions", None),
                "responses": context.get("responses", None),
                "surveys": context.get("surveys", None)
            }
            return JsonResponse(data)
        context["questions"] = json.dumps(context.get("questions", None))
        context["responses"] = json.dumps(context.get("responses", None))
        context["surveys"] = json.dumps(context.get("surveys", None))
        return render(request, self.template_name, context)


class ClientHomeView(LoginRequiredMixin, ClientRequiredMixin, TemplateView):
    template_name = 'sportdiag/home/client_home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        survey_response_requests_ids = SurveyResponseRequest.objects.filter(client_id=user.id,
                                                                            is_pending=True).order_by(
            "requested_on_date").values_list("survey_id", flat=True)
        # todo should be only 1 active request for client per survey
        surveys = Survey.objects.filter(id__in=survey_response_requests_ids)
        context['surveys'] = surveys
        return context


class SurveyConfirmView(LoginRequiredMixin, ClientRequiredMixin, TemplateView):
    template_name = "sportdiag/new_response_saved_confirm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["uuid4"] = str(kwargs.get("uuid4"))
        context["response"] = Response.objects.get(interview_uuid=context["uuid4"])
        return context


class NewResponseFormView(LoginRequiredMixin, ClientRequiredMixin, TemplateView):
    template_name = "sportdiag/new_response.html"
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
            survey = Survey.objects.get(id=survey_id)  # todo select related
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


class ApprovePsychologistsView(LoginRequiredMixin, StaffResearcherRequiredMixin, ListView):
    model = User
    paginate_by = 10
    template_name = 'sportdiag/approve_psychologists.html'
    # query jen is_active false a is_psychologist true?
    queryset = User.objects.filter(is_psychologist=True, email_verified=True, confirmed_by_staff=False, is_active=False)
    ordering = ['-date_joined']


class InviteClient(LoginRequiredMixin, PsychologistRequiredMixin, FormView):
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


@user_passes_test(user_is_staff_researcher)
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


@user_passes_test(user_is_staff_researcher)
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


@user_passes_test(user_is_staff_researcher)
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


class ResearchersOverviewView(LoginRequiredMixin, StaffResearcherRequiredMixin, ListView):
    model = User
    paginate_by = 10
    template_name = 'sportdiag/researchers_overview.html'

    def get_queryset(self):
        """ returns all researchers excluding logged in (staff) researcher """
        queryset = super().get_queryset()
        current_user = self.request.user  # current user is staff researcher
        queryset = queryset.filter(is_researcher=True).difference(User.objects.filter(id=current_user.id)).order_by(
            '-date_joined')
        return queryset


@user_passes_test(user_is_staff_researcher)
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


@user_passes_test(user_is_staff_researcher)
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


class SurveysAndManualsView(LoginRequiredMixin, PsychologistOrResearcherRequiredMixin, ListView):
    template_name = "sportdiag/surveys_and_manuals.html"
    upload_survey_attachments_form = UploadFilesForm
    paginate_by = 5
    model = Survey
    ordering = ['id']

    def get_queryset(self, user):
        queryset = super().get_queryset()
        queryset = queryset.filter(is_deleted=False)
        if user and user.is_psychologist:
            queryset = queryset.filter(is_published=True)
        return queryset

    def get_context_data(self, **kwargs):
        user = kwargs.get("user")
        queryset = self.get_queryset(user=user)
        context = super().get_context_data(object_list=queryset, **kwargs)
        context['upload_attachments_form'] = self.upload_survey_attachments_form()
        surveys_attachments = {}
        surveys = context['object_list']
        for survey in surveys:
            attachments_dir_path = get_survey_attachments_upload_dir_path(survey)
            attachments_names = os.listdir(attachments_dir_path)
            surveys_attachments[survey.id] = attachments_names
        context['surveys_attachments'] = surveys_attachments
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(user=request.user)
        return render(request, self.template_name, context)


def get_survey_media_dir_path(survey):
    return settings.MEDIA_ROOT / 'sportdiag/surveys' / f'survey_{survey.id}'


def get_survey_attachments_upload_dir_path(survey):
    survey_media_dir_path = get_survey_media_dir_path(survey)
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


@user_passes_test(user_is_staff_researcher)
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
        messages.error(request, "Příloha nebyla nahrána.")
        return redirect('sportdiag:surveys_manuals')


@user_passes_test(user_is_psychologist_or_researcher)
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


@user_passes_test(user_is_staff_researcher)
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


@user_passes_test(user_is_researcher)
def export_survey_responses_to_csv(request, survey_id):
    # todo POST? melo by byt chraneno, at na tu URL nevleze kdekdo a nemeni cisla
    survey = Survey.objects.get(id=survey_id)
    responses = Response.objects.filter(survey_id=survey.id).order_by("-created")
    if not responses:
        # todo NOW EXPORT BUTTON IS NOT RENDERED IF NO SURVEYS RESULTS IN TEMPLATE
        # messages doesnt work with redirect ...
        messages.error(request, "Žádné responze k exportování.")
        return redirect('sportdiag:home_researcher')
        # return render(request, self.template_name, context)
    filename = f"odpovedi_{datetime.now(timezone.utc).date()}_{survey.short_name}.csv".replace(" ", "_").replace("-",
                                                                                                                 "_")
    questions = []
    questions += [question.text for question in survey.no_category_questions()]
    questions += [question.short_name for question in survey.categorized_questions()]
    http_response = HttpResponse(content_type='text/csv',
                                 headers={'Content-Disposition': f'attachment; filename="{filename}"'},
                                 charset='utf-8-sig')
    writer = csv.writer(http_response)  # todo bad diacritics on win excel
    writer.writerow(
        ['#', 'Dotazník', 'Datum responze', 'ID Responze', 'ID Klienta', 'Státní příslušnost', 'Pohlaví',
         'Věk', *questions, 'Skóre', 'Max Skóre'])
    counter = 1
    for response in responses:
        client = ClientProfile.objects.get(user_id=response.user_id)
        no_cat_questions_answers = response.answers.filter(question_id__in=survey.no_category_questions()).order_by(
            "created").values_list("body", flat=True)
        answers = response.answers.filter(question_id__in=survey.categorized_questions()).order_by(
            "created").values_list("score", flat=True)
        response_created = response.created.astimezone(tz=tz.tzlocal()).strftime("%Y-%m-%d %H:%M")
        writer.writerow(
            [f'{counter}', f'{survey.short_name}', f'{response_created}',
             f'{response.interview_uuid}', f'{client.user_id}', f'{client.nationality}', f'{client.sex}',
             f'{client.age}',
             *no_cat_questions_answers, *answers, f'{response.total_score}', f'{response.max_score}'])
        counter += 1  # todo round total score..
    return http_response


@user_passes_test(user_is_staff_researcher)
def toggle_is_published(request, survey_id):
    survey = Survey.objects.get(id=survey_id)
    if survey:
        survey.is_published = not survey.is_published
        survey.save()
    else:
        messages.error(request, "Dotazník nenalezen.")
    return redirect("sportdiag:surveys_manuals")


@user_passes_test(user_is_staff_researcher)
def delete_survey(request, survey_id):
    """performs soft delete"""
    survey = Survey.objects.get(id=survey_id)
    if survey:
        survey.is_deleted = True
        survey.deleted_date = datetime.now(timezone.utc)
        survey.save()
        # todo remove attachments - TEST
        survey_media_dir_path = get_survey_media_dir_path(survey)
        if os.path.exists(survey_media_dir_path):
            shutil.rmtree(survey_media_dir_path)  # todo on error logging
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


class ResponseDetailView(LoginRequiredMixin, PsychologistOrResearcherRequiredMixin, TemplateView):
    template_name = "sportdiag/response_detail.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        response = Response.objects.get(id=kwargs.get("response_id"))
        client = ClientProfile.objects.get(user_id=response.user_id)
        survey = Survey.objects.get(id=response.survey_id)
        context["response"] = response
        context["client"] = client
        context["survey"] = survey
        categories_data = []
        for category in survey.non_empty_categories():
            questions_data = []
            for question in category.questions.order_by("number"):
                answer = question.answers.get(response_id=response.id)
                question_data = {
                    "question_tag": question.short_name,
                    "required": question.required,
                    "question_text": question.text,
                    "answer_text": answer.body,
                    "answer_score": answer.score
                }
                questions_data.append(question_data)
            categories_data.append({
                "id": category.id,
                "name": category.name,
                "questions_data": questions_data,
                "score": response.compute_category_score(category)
            })
        context["categories_data"] = categories_data
        no_cat_questions_data = []
        for question in survey.no_category_questions():
            answer = question.answers.get(response_id=response.id)
            no_cat_questions_data.append({
                "required": question.required,
                "question_text": question.text,
                "answer_text": answer.body,
            })
        context["no_cat_questions_data"] = no_cat_questions_data
        return context
