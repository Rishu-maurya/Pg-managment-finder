from django.contrib import admin
from .models import ChatConversation, ChatMessage, ChatBlock


@admin.register(ChatConversation)
class ChatConversationAdmin(admin.ModelAdmin):
    list_display = ('initiator', 'recipient', 'pg', 'is_active', 'created_at', 'last_message_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('initiator__email', 'recipient__email', 'pg__title')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'message_type', 'is_read', 'created_at')
    list_filter = ('message_type', 'is_read', 'created_at')
    search_fields = ('sender__email', 'receiver__email', 'content')
    readonly_fields = ('created_at', 'updated_at', 'read_at')


@admin.register(ChatBlock)
class ChatBlockAdmin(admin.ModelAdmin):
    list_display = ('blocker', 'blocked_user', 'created_at')
    search_fields = ('blocker__email', 'blocked_user__email')
    readonly_fields = ('created_at',)

