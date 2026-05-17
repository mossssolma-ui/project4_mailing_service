from django import forms

from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.crypto import get_random_string

from django.conf import settings
from .models import CustomUser


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})


class CustomPasswordChangeForm(StyleFormMixin, PasswordChangeForm):
    """Форма смены пароля с Bootstrap стилями"""
    pass


class CustomUserCreationForm(StyleFormMixin, UserCreationForm):
    phone_number = forms.CharField(max_length=15, required=False, help_text='Номер телефона (необязательно)')

    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError('Номер должен состоять из цифр')
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = False
        user.email_verification_token = get_random_string(50)

        if commit:
            user.save()

        self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        verification_url = reverse('users:verify_email', kwargs={'token': user.email_verification_token})
        full_url = f"http://127.0.0.1:8000{verification_url}"
        subject = "Подтверждение регистрации на сайте Сервис рассылок"
        message = f"""
                    Здравствуйте!
                    
                    Для подтверждения регистрации на сайте Сервис рассылок перейдите по ссылке:
                    {full_url}
                    
                    Если вы не регистрировались на нашем сайте, проигнорируйте это письмо.
                    
                    С уважением,
                    Команда сервиса рассылок
                """
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])


class CustomUserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2')


class ProfileUserUpdateForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'phone_number', 'country', 'avatar')
