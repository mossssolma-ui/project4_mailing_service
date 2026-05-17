from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from .forms import DistributionForm, RecipientForm, MessageForm
from .models import Recipient, Message, Distribution, Attempt


# Recipient
class RecipientList(ListView):
    """Список получателей рассылок"""
    model = Recipient
    template_name = 'mailing_service/recipient_list.html'
    context_object_name = 'recipients'


class RecipientDetail(DetailView):
    """Конкретный получатель рассылки"""
    model = Recipient
    template_name = 'mailing_service/recipient_details.html'
    context_object_name = 'recipient'


class RecipientCreate(CreateView):
    """Создать получателя рассылки"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing_service/recipient_form.html'
    success_url = reverse_lazy('mailing_service:recipient_list')
    context_object_name = 'recipient'


class RecipientUpdate(UpdateView):
    """Изменить данные получателя рассылки"""
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailing_service/recipient_form.html'
    success_url = reverse_lazy('mailing_service:recipient_list')
    context_object_name = 'recipient'


class RecipientDelete(DeleteView):
    """Удалить получателя рассылки"""
    model = Recipient
    template_name = 'mailing_service/recipient_delete.html'
    success_url = reverse_lazy('mailing_service:recipient_list')


# Message
class MessageList(ListView):
    """Список сообщений"""
    model = Message
    template_name = 'mailing_service/message_list.html'
    context_object_name = 'message'


class MessageDetail(DetailView):
    """Конкретное сообщение"""
    model = Message
    template_name = 'mailing_service/message_details.html'
    context_object_name = 'message'


class MessageCreate(CreateView):
    """Создать сообщение"""
    model = Message
    form_class = MessageForm
    template_name = 'mailing_service/message_form.html'
    success_url = reverse_lazy('mailing_service:message_list')
    context_object_name = 'message'


class MessageUpdate(UpdateView):
    """Изменить сообщение"""
    model = Message
    form_class = MessageForm
    template_name = 'mailing_service/message_form.html'
    success_url = reverse_lazy('mailing_service:message_list')
    context_object_name = 'message'


class MessageDelete(DeleteView):
    """Удалить сообщение"""
    model = Message
    template_name = 'mailing_service/message_delete.html'
    success_url = reverse_lazy('mailing_service:message_list')


# Distribution
class DistributionList(ListView):
    """Список рассылок"""
    model = Distribution
    template_name = 'mailing_service/distribution_list.html'
    context_object_name = 'distribution'

    def get_queryset(self):
        """Обновление статуса в списке"""
        queryset = super().get_queryset()
        for obj in queryset:
            obj.update_status()
        return queryset


class DistributionDetail(DetailView):
    """Конкретная рассылка"""
    model = Distribution
    template_name = 'mailing_service/distribution_details.html'
    context_object_name = 'distribution'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.update_status()
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    def post(self, request, *args, **kwargs):
        """Ручной запуск рассылки"""

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
                        distribution=distribution
                    )
                )
            except Exception as e:
                attempts_for_create.append(
                    Attempt(
                        status=Attempt.Status.FAILED,
                        response=str(e)[:500],
                        distribution=distribution
                    )
                )
        if attempts_for_create:
            Attempt.objects.bulk_create(attempts_for_create)

        return redirect('mailing_service:distribution_details', pk=distribution.pk)


class DistributionCreate(CreateView):
    """Создать рассылку"""
    model = Distribution
    form_class = DistributionForm
    template_name = 'mailing_service/distribution_form.html'
    success_url = reverse_lazy('mailing_service:distribution_list')


class DistributionUpdate(UpdateView):
    """Изменить рассылку"""
    model = Distribution
    form_class = DistributionForm
    template_name = 'mailing_service/distribution_form.html'
    success_url = reverse_lazy('mailing_service:distribution_list')


class DistributionDelete(DeleteView):
    """Удалить рассылку"""
    model = Distribution
    template_name = 'mailing_service/distribution_delete.html'
    success_url = reverse_lazy('mailing_service:distribution_list')


# Attempt
class AttemptList(ListView):
    model = Attempt
    template_name = 'mailing_service/attempt_list.html'
    context_object_name = 'attempts'

    def get_queryset(self):
        queryset = super().get_queryset()
        distribution_id = self.request.GET.get('distribution')
        if distribution_id:
            queryset = queryset.filter(distribution_id=distribution_id)
        return queryset.select_related('distribution').order_by('-dt')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_now = timezone.now()

        context['active_distributions'] = Distribution.objects.filter(
            start_time__lte=time_now,
            end_time__gte=time_now,
            status=Distribution.Status.STARTED
        ).count()

        context['active_mailings'] = Distribution.objects.filter(
            start_time__lte=time_now,
            end_time__gte=time_now,
            status=Distribution.Status.STARTED
        )

        return context


# home
class HomeView(TemplateView):
    template_name = 'mailing_service/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        time_now = timezone.now()
        count_distributions = Distribution.objects.count()
        count_messages = Message.objects.count()
        active_distributions = Distribution.objects.filter(start_time__lte=time_now, end_time__gte=time_now,
                                                           status=Distribution.Status.STARTED).count()
        unique_recipients = Recipient.objects.count()

        context.update({
            'count_distributions': count_distributions,
            'count_messages': count_messages,
            'active_distributions': active_distributions,
            'unique_recipients': unique_recipients,
        })
        return context
