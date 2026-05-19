from django.db import models
from django.utils import timezone

from users.models import CustomUser


class Recipient(models.Model):
    """ Получатель рассылки """
    email = models.EmailField(max_length=300, unique=True, verbose_name="Электронная почта")
    full_name = models.CharField(max_length=200, verbose_name="ФИО")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owners_rec', verbose_name="Владелец")

    def __str__(self):
        return f"{self.email} - {self.full_name}"

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["email"]
        permissions = [
            ("can_view_all_recipients", "Может просматривать всех получателей")
        ]


class Message(models.Model):
    """ Управление сообщениями """
    title = models.CharField(max_length=300, verbose_name="Тема письма")
    content = models.TextField(verbose_name="Тело письма")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата изменения")
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owners_mes', verbose_name="Владелец")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ["title"]
        permissions = [
            ("can_view_all_messages", "Может просматривать все сообщения")
        ]


class Distribution(models.Model):
    """ Управление рассылками """

    class Status(models.TextChoices):
        CREATED = 'created', 'Создана'
        STARTED = 'started', 'Запущена'
        COMPLETED = 'completed', 'Завершена'

    start_time = models.DateTimeField(verbose_name="Дата и время начала отправки")
    end_time = models.DateTimeField(verbose_name="Дата и время окончания отправки")
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.CREATED,
        verbose_name='Статус рассылки'
    )
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="distributions",
                                verbose_name="Сообщение")
    recipients = models.ManyToManyField(Recipient, related_name="distributions", verbose_name="Получатели")
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owners_dist', verbose_name="Владелец")

    def __str__(self):
        return f"{self.message} - {self.get_status_display()}"

    def update_status(self):
        """Динамическое обновление статуса рассылки"""
        now = timezone.now()

        if now < self.start_time:
            new_status = self.Status.CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.Status.STARTED
        else:
            new_status = self.Status.COMPLETED

        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=['status'])

        return self.status

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-end_time"]
        permissions = [
            ("can_view_all_distributions", "Может просматривать все рассылки"),
            ("can_disable_distributions", "Может отключать рассылки"),
        ]


class Attempt(models.Model):
    """Попытка рассылки"""

    class Status(models.TextChoices):
        SUCCESS = 'success', 'Успешно'
        FAILED = 'failed', 'Не успешно'

    dt = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время попытки")
    status = models.CharField(max_length=15, choices=Status.choices, verbose_name="Статус")
    response = models.TextField(verbose_name="Ответ почтового сервера")
    distribution = models.ForeignKey(Distribution, on_delete=models.CASCADE, related_name="attempts",
                                     verbose_name="Рассылка")
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='owners_attempt',
                              verbose_name="Владелец")

    def __str__(self):
        return f"{self.dt} - {self.status}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
        ordering = ["-dt"]
        permissions = [
            ("can_view_all_attempt", "Может просматривать все попытки")
        ]
