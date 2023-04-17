from django import forms
from crispy_forms.helper import FormHelper
from django.utils.translation import gettext_lazy as _
from crispy_forms.layout import Submit, Layout, Div
from django.core.exceptions import ObjectDoesNotExist
from django.forms import models
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import InlineRadios, FormActions
from crispy_forms.layout import Layout, Submit, Field, Div, HTML, Button

from accounts.models import User
# dat layout object do neceho jako sportdiag.crispy_extension.layout
from sportdiag.models import Response, Survey, Question, LikertScaleQuestionLayoutObject, Answer
import logging
import uuid

LOGGER = logging.getLogger(__name__)


class InviteClientForm(forms.Form):
    class Meta:
        fields = ['client_email']

    client_email = forms.EmailField(label=_('E-mail klienta'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True

    def clean_client_email(self):
        client_email = self.cleaned_data['client_email']
        try:
            client = User.objects.get(email=client_email)
        except ObjectDoesNotExist:
            # todo spolihat v logice kodu na vyjimku je dost na prase.. vymyslet lip
            return client_email
        raise forms.ValidationError(
            _('Uživatel s tímto e-mailem je již registrován.'),
            code='invalid client_email',
            params={'value': client_email})


from django.forms.widgets import ChoiceWidget


# todo custom radio?
class LikertRadio(ChoiceWidget):
    input_type = 'radio'
    template_name = 'sportdiag/widgets/likert_radio/likert_radio.html'
    # template_name = 'django/forms/widgets/radio.html'
    option_template_name = 'sportdiag/widgets/likert_radio/liker_radio_option.html'
    # option_template_name = 'django/forms/widgets/radio_option.html'


class ResponseForm(models.ModelForm):
    FIELDS = {
        Question.SHORT_TEXT: forms.CharField,
        Question.INTEGER: forms.IntegerField,
    }

    WIDGETS = {
        Question.SHORT_TEXT: forms.TextInput,
        Question.RADIO: forms.RadioSelect,
        Question.SELECT: forms.Select,
        Question.INTEGER: forms.IntegerField,
        Question.LIKERT_SCALE: LikertRadio
    }

    class Meta:
        model = Response
        fields = ()

    def get_likert_scale_table_header(self, likert_scale):
        html = '<div class="table-responsive">\
                        <table class="table table-bordered bg-white">\
                            <thead>\
                            <tr> \
                                <th scope="col"></th>'
        for choice in likert_scale.get_choices():
            html += f'<th scope="col" class="text-center">{choice}</th>'
        html += '</tr></thead><tbody>'
        return html

    # expects survey and user in kwargs
    def __init__(self, *args, **kwargs):
        self.survey = kwargs.pop('survey')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.label_class = 'fw-light'
        self.helper.layout = Layout()

        self.groups = self.survey.non_empty_question_groups()
        self.likert_scales = self.survey.non_empty_likert_scales()
        # todo to list()?
        # self.other_questions = self.survey.questions.filter(category__isnull=True, likert_scale__isnull=True).order_by(
        #    "order", "id")
        self.processed_likert_scales = {}
        for ls in self.likert_scales:
            ls_questions = list(self.survey.questions.filter(likert_scale__id=ls.id))
            self.processed_likert_scales[ls.id] = {
                "table_header_added": False,
                "questions": [q.id for q in ls_questions]
            }
        print(self.processed_likert_scales)
        # todo nejaka logika by mela jit do modelu survey
        self.processed_question_groups = {}
        for group in self.groups:
            group_questions = group.questions.all()
            self.processed_question_groups[group.id] = {
                "group_start_added": False,
                "questions": [q.id for q in group_questions]
            }
        self.add_questions()

    @staticmethod
    def get_group_start_html(group):  # todo group
        html = f'<div class="accordion" id="accordion{group.id}">\
                            <div class="accordion-item">\
                                <h3 class="accordion-header" id="heading{group.id}">\
                                    <button class="accordion-button" type="button" data-bs-toggle="collapse"\
                                    data-bs-target="#collapse{group.id}" aria-expanded="true"\
                                    aria-controls="collapse{group.id}">\
                                    {group.name}\
                                    </button>\
                                </h3>\
                            <div id="collapse{group.id}" class="accordion-collapse collapse show"\
                            aria-labelledby="heading{group.id}"\
                            data-bs-parent="#accordion{group.id}">\
                        <div class="accordion-body">'
        if group.description != "":
            html += f'<p class="fw-bolder">Popis:</p><p class="fst-italic">{group.description}</p>'
        if group.instructions != "":
            html += f'<p class="fw-bolder">Instrukce:</p><p class="fst-italic">{group.instructions}</p>'
        return html

    def add_likert_scale_question(self, question):
        ls_id = question.likert_scale.id
        if not self.processed_likert_scales[ls_id]["table_header_added"]:
            self.helper.layout.append(HTML(self.get_likert_scale_table_header(question.likert_scale)))
            self.processed_likert_scales[ls_id]["table_header_added"] = True
        self.helper.layout.append(HTML('<tr>'))
        required = '<span class="asteriskField">*</span>' if question.required else ""
        self.helper.layout.append(
            HTML(
                f'<td style="width: 500px" class="align-middle fw-light">{question.order}) {question.text}{required}</td>'))
        self.add_question(question)
        self.helper.layout.append(HTML('</tr>'))
        self.processed_likert_scales[ls_id]["questions"].remove(question.id)
        if self.processed_likert_scales[ls_id]["questions"].__len__() == 0:
            self.helper.layout.append(HTML('</tbody></table></div>'))

    def add_questions(self):
        for question in self.survey.questions.order_by('order'):  # enumerate(self.survey.questions.all())
            if question.group is not None:
                group_id = question.group_id
                group = self.survey.question_groups.get(id=group_id)
                if not self.processed_question_groups[group_id]["group_start_added"]:
                    self.helper.layout.append(HTML(self.get_group_start_html(group)))
                    self.processed_question_groups[group_id]["group_start_added"] = True
                if question.likert_scale is not None:
                    self.add_likert_scale_question(question)
                else:
                    self.add_question(question)
                self.processed_question_groups[group_id]["questions"].remove(question.id)
                if self.processed_question_groups[group_id]["questions"].__len__() == 0:
                    self.helper.layout.append(HTML('</div></div></div></div><br/>'))  # group end
            elif question.likert_scale is not None:
                self.add_likert_scale_question(question)
            else:
                self.add_question(question)
        # todo handle questions without category
        self.helper.layout.append(
            Div(Div(Submit("submit", _("Odeslat")), css_class="mb-1"),
                HTML("""<button data-bs-toggle="modal" data-bs-target="#cancelSurveyModal"
                type="button" class="btn btn-secondary ms-1 mb-1">Ukončit a zapomenout odpovědi</button>"""),
                css_class="d-flex flex-wrap justify-content-end"))
        # todo css_class="d-flex justify-content-end" ??? tlacitka vpravo dole misto vlevo

    def add_question(self, question):
        kwargs = {
            "label": f'{question.order}) {question.text}',
            "required": question.required}
        choices = self.get_question_choices(question)
        if choices:
            kwargs["choices"] = choices
        widget = self.get_question_widget(question)
        if widget:
            kwargs["widget"] = widget
        field = self.get_question_field(question, **kwargs)
        # field = forms.ChoiceField(widget=forms.RadioSelect(), choices=choices,
        #                          label=_(question.text),
        #                          required=question.required)
        field.widget.attrs["question_group"] = question.group.name if question.group else ""
        field.widget.attrs["likert_scale"] = question.likert_scale.name if question.likert_scale else ""
        # logging.debug("Field for %s : %s", question, field.__dict__)
        field_key = f"question_{question.id}"
        # add question to crispy form Layout manually to customize rendering
        # if question.type == Question.LIKERT_SCALE
        # self.helper.layout.append(Field(field_key))
        self.helper.layout.append(
            LikertScaleQuestionLayoutObject(field_key) if question.type == Question.LIKERT_SCALE else Field(field_key))
        self.fields[field_key] = field

    @staticmethod
    def get_question_choices(question):
        """Return the choices we should use for a question.
        :param Question question: The question
        :rtype: List of String or None"""
        question_choices = None
        if question.type not in [Question.SHORT_TEXT, Question.INTEGER]:
            question_choices = question.get_choices()
            # add an empty option at the top so that the user has to explicitly
            # select one of the options
            # if question.type in [Question.SELECT]: todo solve validation for "nevybrano"
            #    question_choices = tuple([("-", _("Nevybráno"))]) + question_choices
        return question_choices

    def get_question_widget(self, question):
        """Return the widget we should use for a question.
        :param Question question: The question
        :rtype: django.forms.widget or None"""
        try:
            return self.WIDGETS[question.type]
        except KeyError:
            return None

    def get_question_field(self, question, **kwargs):
        """Return the field we should use in our form.
        :param Question question: The question
        :param **kwargs: A dict of parameter properly initialized in
            add_question.
        :rtype: django.forms.fields"""
        # logging.debug("Args passed to field %s", kwargs)
        try:
            return self.FIELDS[question.type](**kwargs)
        except KeyError:
            return forms.ChoiceField(**kwargs)

    def get_answer_body(self, question, field_value):
        choices = [choice.replace("(", "").replace(")", "") for choice in question.get_clean_choices()]
        if field_value in choices:
            index = choices.index(field_value)
            return question.get_clean_choices()[index]

    def save(self, commit=True):
        """Save the response object"""
        # Recover an existing response from the database if any
        #  There is only one response by logged user.
        response = super().save(commit=False)
        response.survey = self.survey
        response.interview_uuid = uuid.uuid4()
        if self.user.is_authenticated:
            response.user = self.user
        response.save()
        # response "raw" data as dict (for signal)
        data = {"survey_id": response.survey.id, "interview_uuid": response.interview_uuid, "responses": []}
        # create an answer object for each question and associate it with this
        # response.
        for field_name, field_value in list(self.cleaned_data.items()):
            if field_name.startswith("question_"):
                # warning: this way of extracting the id is very fragile and
                # entirely dependent on the way the question_id is encoded in
                # the field name in the __init__ method of this form class.
                q_id = int(field_name.split("_")[1])
                question = Question.objects.get(id=q_id)
                answer = Answer(question=question)
                # todo get_answer_body to Question class or get_answer_score to ResponseForm class?
                answer.body = self.get_answer_body(question, field_value.replace("-", " ")) if question.type in [
                    Question.SELECT, Question.RADIO, Question.LIKERT_SCALE] else field_value.replace("-", " ")
                answer.score = question.get_answer_score(answer)
                data["responses"].append((answer.question.id, answer.body))
                LOGGER.debug("Creating answer for question %d of type %s : %s", q_id, answer.question.type, field_value)
                answer.response = response
                answer.save()
        # todo k cemu je ten signal completed??
        # survey_completed.send(sender=Response, instance=response, data=data)
        return response


class ResponsesFilterForm(forms.Form):
    survey = forms.ModelChoiceField(queryset=Survey.objects.filter(is_deleted=False).order_by('id'),
                                    label=_("Dotazník"), required=False, empty_label=None)

    # todo dalsi fieldy - filtry pro tabulku vysledku + vizual filter formu
    # todo helper property instead of using init?
    class Meta:
        fields = ['survey']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        # self.helper.form_class = 'row'
        self.helper.label_class = 'fw-light'
        self.helper.field_class = 'col-sm-8 col-md-6 col-lg-4'
        self.helper.layout = Layout('survey', Submit('submit', 'Filtrovat'))


class UploadFilesForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))

    # todo crispy
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_show_labels = False
        self.helper.form_tag = False
        self.helper.disable_csrf = True
