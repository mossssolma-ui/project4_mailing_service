from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Телефон")
    country = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.ImageField(upload_to="users/avatars/", blank=True, null=True, verbose_name="Аватар")

    is_verified = models.BooleanField(default=False, verbose_name="Email подтвержден")
    email_verification_token = models.CharField(max_length=100, blank=True, null=True,
                                                verbose_name="Токен подтверждения")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-email']

    def __str__(self):
        return self.email
