from django.urls import path, include, re_path
from django.conf.urls import url
from .views import SignUpView, ClientSignUpView, PsychologistSignUpView, activate, PasswordResetView, \
    PasswordResetDoneView, ResearcherCreateView, ClientDetailView, AccountSettingsView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('registrace/', SignUpView.as_view(), name='signup'),
    path('registrace/klient/', ClientSignUpView.as_view(), name='signup_client'),
    path('registrace/klient/<uuid4>/', ClientSignUpView.as_view(), name='signup_client'),
    path('registrace/psycholog/', PsychologistSignUpView.as_view(), name='signup_psychologist'),
    path('prihlaseni/', auth_views.LoginView.as_view(template_name='accounts/registration/login.html'), name='login'),
    path('odhlasit/', auth_views.LogoutView.as_view(), name='logout'),
    path('obnoveni_hesla/', PasswordResetView.as_view(), name='password_reset'),
    path('obnoveni_hesla_vyzadano/', PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('obnoveni_hesla_dokonceni/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('obnoveni_hesla/dokonceno/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/registration/password_reset_complete.html'), name='password_reset_complete'),
    path('aktivovat_ucet/<uidb64>/<token>/', activate, name='activate'),
    path('registrace/vyzkumnik/', ResearcherCreateView.as_view(), name='create_researcher_account'),
    re_path(r'detail_klienta/(?P<user_id>\d+)/$', ClientDetailView.as_view(), name='client_detail'),
    re_path(r'detail_klienta/(?P<user_id>\d+)/\?(?:page=(?P<page>\d+))?$', ClientDetailView.as_view(),
            name='client_detail'),
    path('nastaveni_uctu/<int:pk>', AccountSettingsView.as_view(), name='account_settings')
    # url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$', activate,
    #    name='activate'),
]

# urlpatterns = [
#    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
#    path('password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
# ]
