from django.urls import path, include
from .views import IndexView, BeneficiariesView, ContactView, HomePageView, InviteClient, \
    ApprovePsychologistsView, RejectPsychologist, approve_psychologist, download_certificate
from django.contrib.auth.decorators import login_required

app_name = 'sportdiag'

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('beneficiaries/', BeneficiariesView.as_view(), name='beneficiaries'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('sportdiag/', login_required(HomePageView.as_view()), name='home'),
    path('sportdiag/invite_client', InviteClient.as_view(), name='invite_client'),
    path('sportdiag/approve_psychologists/', ApprovePsychologistsView.as_view(),
         name='approve_psychologists'),
    path('sportdiag/approve_psychologists/reject/<int:pk>/', RejectPsychologist.as_view(),
         name='reject_psychologist'),
    path('sportdiag/approve_psychologists/approve/<int:pk>/', approve_psychologist, name='approve_psychologist'),
    path('sportdiag/approve_psychologists/download_certificate/<int:pk>/', download_certificate,
         name='download_certificate')
]
