import os

from django.contrib.auth import get_user_model


from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создание суперпользователя"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        email = "admin@mail.ru"

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f"Пользователь {email} уже существует")
            )
            return

        user = User.objects.create(email=email)
        user.set_password(os.getenv("CSU_PASSWORD"))
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
