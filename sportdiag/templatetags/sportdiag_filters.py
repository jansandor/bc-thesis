from django import template

register = template.Library()


@register.filter('bool_cz')
def bool_cz(value):
    if value:
        return 'Ano'
    if not value:
        return 'Ne'
    return '-'


@register.filter('answer')
def answer(answer):
    if answer.question.number == 0:
        return answer.body
    return answer.score


@register.filter('question')
def question(question):
    if question.number == 0:
        return question.text
    return question.short_name
