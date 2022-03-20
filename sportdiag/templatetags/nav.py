from django import template
from django.urls import resolve

register = template.Library()


@register.simple_tag
def active_nav_link(request, view_name):
    view = resolve(request.path).view_name
    if view == view_name:
        return "active"
    return ""