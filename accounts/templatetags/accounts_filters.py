from django import template
from accounts.utils.user.sex_choices import SEX_CHOICES, MAN, WOMAN

register = template.Library()


@register.filter('sex_value')
def bool_cz(value):
    if value == MAN:
        return SEX_CHOICES[1][1]
    elif value == WOMAN:
        return SEX_CHOICES[2][1]
    return 'pohlaví neuvedeno'
