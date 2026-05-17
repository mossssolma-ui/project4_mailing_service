# users/management/commands/create_group.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from mailing_service.models import Distribution, Recipient, Message, Attempt


class Command(BaseCommand):
    help = "Создание групп и назначение прав"

    def handle(self, *args, **kwargs):
        manager_group, created = Group.objects.get_or_create(name='Менеджеры')

        user_group, created = Group.objects.get_or_create(name='Пользователи')

        distribution_ct = ContentType.objects.get_for_model(Distribution)
        recipient_ct = ContentType.objects.get_for_model(Recipient)
        message_ct = ContentType.objects.get_for_model(Message)
        attempt_ct = ContentType.objects.get_for_model(Attempt)

        user_perms = [
            Permission.objects.get(codename='view_distribution', content_type=distribution_ct),
            Permission.objects.get(codename='view_recipient', content_type=recipient_ct),
            Permission.objects.get(codename='view_message', content_type=message_ct),
            Permission.objects.get(codename='view_attempt', content_type=attempt_ct),
            Permission.objects.get(codename='add_distribution', content_type=distribution_ct),
            Permission.objects.get(codename='add_recipient', content_type=recipient_ct),
            Permission.objects.get(codename='add_message', content_type=message_ct),
            Permission.objects.get(codename='change_distribution', content_type=distribution_ct),
            Permission.objects.get(codename='change_recipient', content_type=recipient_ct),
            Permission.objects.get(codename='change_message', content_type=message_ct),
            Permission.objects.get(codename='delete_distribution', content_type=distribution_ct),
            Permission.objects.get(codename='delete_recipient', content_type=recipient_ct),
            Permission.objects.get(codename='delete_message', content_type=message_ct),
        ]

        user_group.permissions.add(*user_perms)

        manager_perms = list(user_perms)

        custom_perms = Permission.objects.filter(codename__in=[
            'can_view_all_distributions',
            'can_view_all_recipients',
            'can_view_all_messages',
            'can_view_all_attempt',
            'can_disable_distributions'
        ])
        manager_perms.extend(custom_perms)

        manager_group.permissions.add(*manager_perms)

        self.stdout.write(self.style.SUCCESS('Группы "Менеджеры" и "Пользователи" созданы'))
