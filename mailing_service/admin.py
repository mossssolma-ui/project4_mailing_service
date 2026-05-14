from django.contrib import admin

from .models import Recipient, Message, Distribution, Attempt


@admin.register(Recipient)
class RecipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'full_name', 'created_at', 'updated_at')
    search_fields = ('email', 'full_name')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at', 'updated_at')
    search_fields = ('title', 'content')
    list_filter = ('created_at', 'updated_at')


@admin.register(Distribution)
class DistributionAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', 'status', 'start_time', 'end_time')
    search_fields = ('status',)


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('id', 'dt', 'status', 'distribution')
    list_filter = ('status',)
