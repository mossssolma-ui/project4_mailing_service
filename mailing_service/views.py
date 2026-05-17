from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from users.models import CustomUser
from .forms import DistributionForm, RecipientForm, MessageForm
from .models import Recipient, Message, Distribution, Attempt


# Recipient
class RecipientList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Recipient
    template_name = 'mailing_service/recipient_list.html'
    context_object_name = 'recipients'
    permission_required = 'mailing_service.view_recipient'

    def get_queryset(self):
        if self.request.user.has_perm('mailing_service.can_view_all_recipients'):
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=self.request.user)


class RecipientDetail(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = 'mailing_service/recipient_details.html'
    context_object_name = 'recipient'
    permission_required = 'mailing_service.view_recipient'

    def get_queryset(self):
        if self.request.user.has_perm('mailing_service.can_view_all_recipients'):
            return Recipient.objects.all()
        return Recipient.objects.filter(owner=self.request.user)


class RecipientCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing_service/recipient_form.html'
    success_url = reverse_lazy('mailing_service:recipient_list')
    permission_required = 'mailing_service.add_recipient'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing_service/recipient_form.html'
    success_url = reverse_lazy('mailing_service:recipient_list')
    permission_required = 'mailing_service.change_recipient'

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)


class RecipientDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Recipient
    template_name = 'mailing_service/recipient_delete.html'
    success_url = reverse_lazy('mailing_service:recipient_list')
    permission_required = 'mailing_service.delete_recipient'

    def get_queryset(self):
        return Recipient.objects.filter(owner=self.request.user)


# Message
class MessageList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Message
    template_name = 'mailing_service/message_list.html'
    context_object_name = 'message'
    permission_required = 'mailing_service.view_message'

    def get_queryset(self):
        if self.request.user.has_perm('mailing_service.can_view_all_messages'):
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageDetail(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    model = Message
    template_name = 'mailing_service/message_details.html'
    context_object_name = 'message'
    permission_required = 'mailing_service.view_message'

    def get_queryset(self):
        if self.request.user.has_perm('mailing_service.can_view_all_messages'):
            return Message.objects.all()
        return Message.objects.filter(owner=self.request.user)


class MessageCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing_service/message_form.html'
    success_url = reverse_lazy('mailing_service:message_list')
    permission_required = 'mailing_service.add_message'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing_service/message_form.html'
    success_url = reverse_lazy('mailing_service:message_list')
    permission_required = 'mailing_service.change_message'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


class MessageDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Message
    template_name = 'mailing_service/message_delete.html'
    success_url = reverse_lazy('mailing_service:message_list')
    permission_required = 'mailing_service.delete_message'

    def get_queryset(self):
        return Message.objects.filter(owner=self.request.user)


# Distribution
class DistributionList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Distribution
    template_name = 'mailing_service/distribution_list.html'
    context_object_name = 'distribution'
    permission_required = 'mailing_service.view_distribution'

    def get_queryset(self):
        if self.request.user.has_perm('mailing_service.can_view_all_distributions'):
            queryset = Distribution.objects.all()
        else:
            queryset = Distribution.objects.filter(owner=self.request.user)

        for obj in queryset:
            obj.update_status()
        return queryset


class DistributionDetail(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    model = Distribution
    template_name = 'mailing_service/distribution_details.html'
    context_object_name = 'distribution'
    permission_required = 'mailing_service.view_distribution'

    def get_queryset(self):
        if self.request.user.has_perm('mailing_service.can_view_all_distributions'):
            return Distribution.objects.all()
        return Distribution.objects.filter(owner=self.request.user)

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        distribution = self.object
        now = timezone.now()

        if not (distribution.start_time <= now <= distribution.end_time):
            messages.error(request, 'Время запуска рассылки еще не настало или истекло')
            return redirect('mailing_service:distribution_details', pk=distribution.pk)

        attempts_for_create = []
        for recipient in distribution.recipients.all():
            try:
                send_mail(
                    subject=distribution.message.title,
                    message=distribution.message.content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                attempts_for_create.append(
                    Attempt(
                        status=Attempt.Status.SUCCESS,
                        response="Письмо успешно отправлено",
                        distribution=distribution,
                        owner=self.request.user
                    )
                )
            except Exception as e:
                attempts_for_create.append(
                    Attempt(
                        status=Attempt.Status.FAILED,
                        response=str(e)[:500],
                        distribution=distribution,
                        owner=self.request.user
                    )
                )
        if attempts_for_create:
            Attempt.objects.bulk_create(attempts_for_create, batch_size=10)

        return redirect('mailing_service:distribution_details', pk=distribution.pk)


class DistributionCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    permission_required = 'mailing_service.add_distribution'
    model = Distribution
    form_class = DistributionForm
    template_name = 'mailing_service/distribution_form.html'
    success_url = reverse_lazy('mailing_service:distribution_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = kwargs.get('initial', {})
        kwargs['initial']['request'] = self.request
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class DistributionUpdate(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    permission_required = 'mailing_service.change_distribution'
    model = Distribution
    form_class = DistributionForm
    template_name = 'mailing_service/distribution_form.html'
    success_url = reverse_lazy('mailing_service:distribution_list')

    def get_queryset(self):
        return Distribution.objects.filter(owner=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = kwargs.get('initial', {})
        kwargs['initial']['request'] = self.request
        return kwargs


class DistributionDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Distribution
    template_name = 'mailing_service/distribution_delete.html'
    success_url = reverse_lazy('mailing_service:distribution_list')
    permission_required = 'mailing_service.delete_distribution'

    def get_queryset(self):
        return Distribution.objects.filter(owner=self.request.user)


# Attempt
class AttemptList(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    model = Attempt
    template_name = 'mailing_service/attempt_list.html'
    context_object_name = 'attempts'
    permission_required = 'mailing_service.view_attempt'

    def get_queryset(self):
        if self.request.user.has_perm('mailing_service.can_view_all_attempt'):
            queryset = Attempt.objects.all()
        else:
            queryset = Attempt.objects.filter(owner=self.request.user)

        distribution_id = self.request.GET.get('distribution')
        if distribution_id:
            queryset = queryset.filter(distribution_id=distribution_id)
        return queryset.select_related('distribution', 'distribution__message').order_by('-dt')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_now = timezone.now()

        if self.request.user.has_perm('mailing_service.can_view_all_attempt'):
            distributions = Distribution.objects.all()
            user_attempts = Attempt.objects.all()
        else:
            distributions = Distribution.objects.filter(owner=self.request.user)
            user_attempts = Attempt.objects.filter(owner=self.request.user)

        context['active_distributions'] = distributions.filter(
            start_time__lte=time_now,
            end_time__gte=time_now,
            status=Distribution.Status.STARTED
        ).count()

        context['active_mailings'] = distributions.filter(
            start_time__lte=time_now,
            end_time__gte=time_now,
            status=Distribution.Status.STARTED
        )

        context['total_attempts'] = user_attempts.count()
        context['success_attempts'] = user_attempts.filter(status=Attempt.Status.SUCCESS).count()
        context['failed_attempts'] = user_attempts.filter(status=Attempt.Status.FAILED).count()
        context['total_messages_sent'] = user_attempts.filter(status=Attempt.Status.SUCCESS).count()

        return context


# home
@method_decorator(cache_page(300), name='dispatch')  # кеш на 5 минут
class HomeView(TemplateView):
    template_name = 'mailing_service/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_now = timezone.now()

        is_manager = self.request.user.is_authenticated and self.request.user.has_perm(
            'mailing_service.can_view_all_distributions')
        is_authenticated = self.request.user.is_authenticated

        cache_key = f'home_stats_{"manager" if is_manager else "user" if is_authenticated else "guest"}'

        stats = cache.get(cache_key)

        if stats is None:
            if is_manager:
                distributions = Distribution.objects.all()
                messages_count = Message.objects.all()
                recipients = Recipient.objects.all()
                attempts = Attempt.objects.all()
            elif is_authenticated:
                distributions = Distribution.objects.filter(owner=self.request.user)
                messages_count = Message.objects.filter(owner=self.request.user)
                recipients = Recipient.objects.filter(owner=self.request.user)
                attempts = Attempt.objects.filter(owner=self.request.user)
            else:
                distributions = Distribution.objects.all()
                messages_count = Message.objects.all()
                recipients = Recipient.objects.all()
                attempts = Attempt.objects.all()

            stats = {
                'count_distributions': distributions.count(),
                'count_messages': messages_count.count(),
                'active_distributions': distributions.filter(
                    start_time__lte=time_now,
                    end_time__gte=time_now,
                    status=Distribution.Status.STARTED
                ).count(),
                'unique_recipients': recipients.count(),
            }

            cache.set(cache_key, stats, 300)

        context.update(stats)
        context['is_manager'] = is_manager
        context['is_authenticated'] = is_authenticated

        if is_manager:
            context['total_users'] = CustomUser.objects.exclude(
                groups__name='Менеджеры'
            ).filter(is_superuser=False).count()
            context['success_attempts'] = attempts.filter(status=Attempt.Status.SUCCESS).count()
            context['failed_attempts'] = attempts.filter(status=Attempt.Status.FAILED).count()

        return context
