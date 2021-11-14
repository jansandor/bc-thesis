from django.urls import path, include
from .views import IndexView, BeneficiariesView, ContactView, HomePageView, InviteClient
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('beneficiaries/', BeneficiariesView.as_view(), name='beneficiaries'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('sportdiag/', login_required(HomePageView.as_view()), name='home'),
    path('sportdiag/invite-client', InviteClient.as_view(), name='invite_client')
]
