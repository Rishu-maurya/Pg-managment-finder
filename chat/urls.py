"""
URL configuration for chat app
Maps HTTP URLs to views
"""

from django.urls import path
from . import views

urlpatterns = [
    # Chat list and detail
    path('', views.chat_list, name='chat_list'),
    path('conversation/<int:conversation_id>/', views.chat_detail, name='chat_detail'),

    # Start new chat
    path('start/<int:user_id>/', views.start_chat, name='start_chat_user'),
    path('start/pg/<slug:pg_slug>/', views.start_chat, name='start_chat_pg'),

    # Blocking
    path('block/<int:conversation_id>/', views.block_user, name='block_user'),
    path('unblock/<int:user_id>/', views.unblock_user, name='unblock_user'),
    path('blocked/', views.blocked_users, name='blocked_users'),

    # API endpoints
    path('api/messages/<int:conversation_id>/', views.chat_api_messages, name='chat_api_messages'),
]
