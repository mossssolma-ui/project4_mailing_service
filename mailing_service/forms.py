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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = kwargs.get('initial', {}).get('request')
        if request and request.user.is_authenticated:
            user = request.user

            if user.has_perm('mailing_service.can_view_all_recipients'):
                self.fields['recipients'].queryset = Recipient.objects.all()
            else:
                self.fields['recipients'].queryset = Recipient.objects.filter(owner=user)

            if user.has_perm('mailing_service.can_view_all_messages'):
                self.fields['message'].queryset = Message.objects.all()
            else:
                self.fields['message'].queryset = Message.objects.filter(owner=user)
