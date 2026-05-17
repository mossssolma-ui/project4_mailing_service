from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm, ProfileUserUpdateForm
from .models import CustomUser


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Регистрация прошла успешно! На вашу почту отправлена ссылка для подтверждения.')
        return response


class EmailVerificationView(View):
    """Подтверждение email по токену"""

    def get(self, request, token):
        user = get_object_or_404(CustomUser, email_verification_token=token)
        user.is_active = True
        user.is_verified = True
        user.email_verification_token = None
        user.save()
        messages.success(request, 'Ваш email успешно подтвержден! Теперь вы можете войти в систему.')
        return redirect('users:login')


class ProfileUserUpdateView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = ProfileUserUpdateForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile_user")

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUserDetailView(LoginRequiredMixin, DetailView):
    model = CustomUser
    template_name = "users/profile_user.html"
    success_url = reverse_lazy("users:profile_user")

    def get_object(self, queryset=None):
        return self.request.user


class CustomPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'users/password_change_form.html'
    success_url = reverse_lazy('users:password_change_done')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        for field in form.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        return form
