from django import forms


class DateInput(forms.DateInput):
    """
    Changes Django default input_type of DateInput which is 'text' to HTML5 'date' input type.
    It ensures that the HTML5 "DatePicker" is displayed to the user instead of the text input.
    It also allows only correct date to be selected, ie. it is not possible to select 30.2.yyyy etc.
    """
    input_type = 'date'
