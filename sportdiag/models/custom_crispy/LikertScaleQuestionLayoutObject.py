from crispy_forms.layout import Field
from crispy_forms.utils import TEMPLATE_PACK


class LikertScaleQuestionLayoutObject(Field):
    template = "%s/layout/likert_scale_question.html"

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        return super().render(
            form, form_style, context, template_pack=template_pack)
