from django.urls import path, include
from .views import IndexView, BeneficiariesView, ContactView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('beneficiaries/', BeneficiariesView.as_view(), name='beneficiaries'),
    path('contact/', ContactView.as_view(), name='contact'),
]
