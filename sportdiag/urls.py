from django.urls import path, include, re_path
from .views import IndexView, BeneficiariesView, ContactView, PsychologistHomeView, InviteClient, \
    ApprovePsychologistsView, RejectPsychologist, approve_psychologist, download_certificate, \
    redirect_to_user_type_home, ResearcherHomeView, ClientHomeView, ResearchersOverviewView, \
    deactivate_researcher_account, reactivate_researcher_account, SurveyDetail, SurveyConfirmView
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
    path('sportdiag/schvalovani_psychologu/zamitnout/<int:pk>/', RejectPsychologist.as_view(),
         name='reject_psychologist'),
    path('sportdiag/schvalovani_psychologu/schvalit/<int:pk>/', approve_psychologist, name='approve_psychologist'),
    path('sportdiag/schvalovani_psychologu/stahnout_certifikat/<int:pk>/', download_certificate,
         name='download_certificate'),
    re_path(r'sportdiag/prehled-vyzkumniku/(?:\?page=(?P<page>\d+))?$', ResearchersOverviewView.as_view(),
            name='researchers_overview'),
    path('sportdiag/prehled-vyzkumniku/deaktivovat_vyzkumnika/<int:pk>/', deactivate_researcher_account,
         name='deactivate_researcher_account'),
    path('sportdiag/prehled-vyzkumniku/reaktivovat_vyzkumnika/<int:pk>/', reactivate_researcher_account,
         name='reactivate_researcher_account'),
    path('sportdiag/dotaznik/<int:id>/', SurveyDetail.as_view(), name='survey_detail'),
    path('sportdiag/dotaznik/potvrzeni/<uuid4>/', SurveyConfirmView.as_view(), name="survey_confirmation"),
]
