from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, UpdateView, ListView
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm, ProfileUserUpdateForm
from .models import CustomUser


class ManagerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name='Менеджеры').exists()

    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для просмотра этой страницы')
        return redirect('mailing_service:home')


class UsersView(ManagerRequiredMixin, LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = "users/all_users.html"
    context_object_name = "users"

    def get_queryset(self):
        return CustomUser.objects.filter(
            is_superuser=False,
            is_staff=False
        ).exclude(
            groups__name='Менеджеры'
        ).order_by('-date_joined')


class UserBlockView(ManagerRequiredMixin, LoginRequiredMixin, View):
    """Блокировка/разблокировка пользователя"""

    def get(self, request, pk):
        user = get_object_or_404(CustomUser, pk=pk)

        if user == request.user:
            messages.error(request, 'Вы не можете заблокировать самого себя!')
            return redirect('users:users_list')

        if user.groups.filter(name='Менеджеры').exists():
            messages.error(request, 'Вы не можете блокировать менеджера!')
            return redirect('users:users_list')

        user.is_active = not user.is_active
        user.save()

        status = "заблокирован" if not user.is_active else "разблокирован"
        messages.success(request, f'Пользователь {user.email} успешно {status}.')
        return redirect('users:users_list')


class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        response = super().form_valid(form)

        user_group = Group.objects.get(name="Пользователи")
        self.object.groups.add(user_group)

        messages.success(self.request, 'Регистрация прошла успешно! На вашу почту отправлена ссылка для подтверждения.')
        return response


class EmailVerificationView(View):

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
