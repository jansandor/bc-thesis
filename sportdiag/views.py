from django.shortcuts import render
from django.views.generic.base import TemplateView


class IndexView(TemplateView):
    template_name = 'sportdiag/index.html'


class ContactView(TemplateView):
    template_name = 'sportdiag/contact.html'


class BeneficiariesView(TemplateView):
    template_name = 'sportdiag/beneficiaries.html'


class HomePageView(TemplateView):
    template_name = 'sportdiag/home.html'
