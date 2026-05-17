from django.contrib import admin

from .models import Recipient, Message, Distribution, Attempt

from django.contrib import admin
from .models import Recipient, Message, Distribution, Attempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('email', 'full_name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('title',)


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'status', 'owner', 'start_time', 'end_time')
    list_filter = ('status', 'owner')
    search_fields = ('message__title',)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'dt', 'status', 'distribution', 'owner')
    list_filter = ('status', 'owner')
