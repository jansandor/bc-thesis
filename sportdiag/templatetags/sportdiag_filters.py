from django import template

register = template.Library()


@register.filter('bool_cz')
def bool_cz(value):
    if value:
        return 'Ano'
    if not value:
        return 'Ne'
    return '-'
