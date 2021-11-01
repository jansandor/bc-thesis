from django.urls import path, include
from .views import SignUpView, ClientSignUpView, PsychologistSignUpView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signup/client/', ClientSignUpView.as_view(), name='signup_client'),
    path('signup/psychologist/', PsychologistSignUpView.as_view(), name='signup_psychologist'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/registration/login.html'), name='login'),
    path('password_reset/',
         auth_views.PasswordResetView.as_view(template_name='accounts/registration/password_reset.html'),
         name='password_reset'),
    path('password_reset_done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/registration/password_reset_complete.html'), name='password_reset_complete'),
]

# from django.contrib.auth import views
# from django.urls import path
# path('', include('django.contrib.auth.urls')),
# urlpatterns = [
#    path('login/', views.LoginView.as_view(), name='login'),
#    path('logout/', views.LogoutView.as_view(), name='logout'),
#
#    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
#    path('password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
## ]
