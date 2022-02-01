from django.contrib import admin

# Register your models here.
from .models import Survey, Category, Question, LikertScale

admin.site.register(Survey)
admin.site.register(Category)
admin.site.register(Question)
admin.site.register(LikertScale)
