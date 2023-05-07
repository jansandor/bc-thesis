from django.contrib import admin

# Register your models here.
from .models import Survey, Category, Question, LikertScale, QuestionGroup, Answer, Response, SurveyResponseRequest


class QuestionAdmin(admin.ModelAdmin):
    list_display = (
        'survey', 'text', 'number', 'order', 'required', 'type', 'choices', 'scores', 'category', 'group',
        'likert_scale')


admin.site.register(Survey)
admin.site.register(Category)
admin.site.register(Question, QuestionAdmin)
admin.site.register(LikertScale)
admin.site.register(QuestionGroup)
admin.site.register(Answer)
admin.site.register(Response)
admin.site.register(SurveyResponseRequest)
