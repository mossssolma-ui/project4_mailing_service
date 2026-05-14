from django import forms
from django.utils import timezone

from .models import Recipient, Message, Distribution


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите E-mail'})
        self.fields['full_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Укажите ФИО'})
        self.fields['comment'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите комментарий'})


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['title', 'content']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите тему письма'})
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите текст письма'})


class DistributionForm(forms.ModelForm):
    class Meta:
        model = Distribution
        fields = ['start_time', 'end_time', 'message', 'recipients']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['start_time'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Дата и время начала отправки'})
        self.fields['end_time'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Дата и время окончания отправки'})
        self.fields['message'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите сообщение'})
        self.fields['recipients'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Выберите получателей'})

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
