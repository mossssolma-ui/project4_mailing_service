from django import forms
from django.utils import timezone

from .models import Recipient, Message, Distribution


class StyleFormMixin(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fild_name, fild in self.fields.items():
            fild.widget.attrs["class"] = "form-control"


class RecipientForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']


class MessageForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Message
        fields = ['title', 'content']


class DistributionForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = Distribution
        fields = ['start_time', 'end_time', 'message', 'recipients']

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if not start_time or not end_time:
            return cleaned_data

        now = timezone.now()
        if start_time < now:
            self.add_error('start_time', 'Дата начала не может быть в прошлом')

        if start_time > end_time:
            self.add_error('end_time', 'Дата начала не может быть позже даты окончания')

        return cleaned_data
