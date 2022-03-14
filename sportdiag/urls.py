from django.urls import path, include, re_path
from django.conf.urls import url
from .views import IndexView, BeneficiariesView, ContactView, PsychologistHomeView, InviteClient, \
    ApprovePsychologistsView, reject_psychologist, approve_psychologist, download_certificate, \
    redirect_to_user_type_home, ResearcherHomeView, ClientHomeView, ResearchersOverviewView, \
    deactivate_researcher_account, reactivate_researcher_account, SurveyDetail, SurveyConfirmView, \
    request_survey_response, SurveysAndManualsView, upload_survey_attachments, download_survey_attachment, \
    delete_survey_attachment, export_survey_responses_to_csv
from django.contrib.auth.decorators import login_required

# todo views, co jsou nyni ve sportdiagu, ale tykaji se accounts models importovat z accounts.views a nemit je ve sportdiagu

app_name = 'sportdiag'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('beneficienti/', BeneficiariesView.as_view(), name='beneficiaries'),
    path('kontakt/', ContactView.as_view(), name='contact'),
    path('sportdiag/', redirect_to_user_type_home, name='home'),
    path('sportdiag/c/', login_required(ClientHomeView.as_view()), name='home_client'),
    path('sportdiag/p/', login_required(PsychologistHomeView.as_view()), name='home_psychologist'),
    path('sportdiag/r/', login_required(ResearcherHomeView.as_view()), name='home_researcher'),
    path('sportdiag/pozvat_klienta/', InviteClient.as_view(), name='invite_client'),
    re_path(r'sportdiag/schvalovani_psychologu/(?:\?page=(?P<page>\d+))?$', ApprovePsychologistsView.as_view(),
            name='approve_psychologists'),
    path('sportdiag/schvalovani_psychologu/zamitnout/<int:pk>/', reject_psychologist,
         name='reject_psychologist'),
    path('sportdiag/schvalovani_psychologu/schvalit/<int:pk>/', approve_psychologist, name='approve_psychologist'),
    path('sportdiag/schvalovani_psychologu/stahnout_certifikat/<int:pk>/', download_certificate,
         name='download_certificate'),
    re_path(r'sportdiag/prehled_vyzkumniku/(?:\?page=(?P<page>\d+))?$', ResearchersOverviewView.as_view(),
            name='researchers_overview'),
    path('sportdiag/prehled_vyzkumniku/deaktivovat_vyzkumnika/<int:pk>/', deactivate_researcher_account,
         name='deactivate_researcher_account'),
    path('sportdiag/prehled_vyzkumniku/reaktivovat_vyzkumnika/<int:pk>/', reactivate_researcher_account,
         name='reactivate_researcher_account'),
    path('sportdiag/dotaznik/<int:survey_id>/', SurveyDetail.as_view(), name='survey_detail'),
    path('sportdiag/dotaznik/potvrzeni/<uuid4>/', SurveyConfirmView.as_view(), name="survey_confirmation"),
    path('sportdiag/zadost_o_responzi/', request_survey_response, name='request_survey_response'),
    path('sportdiag/dotazniky_manualy/', SurveysAndManualsView.as_view(), name='surveys_manuals'),
    path('sportdiag/dotazniky_manualy/nahrat_prilohy/<int:survey_id>/', upload_survey_attachments,
         name="upload_survey_attachments"),
    path('sportdiag/dotazniky_manualy/stahnout_prilohu/<int:survey_id>/<str:filename>/', download_survey_attachment,
         name='download_survey_attachment'),
    path('sportdiag/dotazniky_manualy/smazat_prilohu/<int:survey_id>/<str:filename>/', delete_survey_attachment,
         name='delete_survey_attachment'),
    path('sportdiag/export_do_csv/<int:survey_id>/', export_survey_responses_to_csv,
         name="export_survey_responses_to_csv"),
]
