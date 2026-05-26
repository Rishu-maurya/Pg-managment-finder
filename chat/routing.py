"""
Routing configuration for Django Channels WebSocket consumers
Maps WebSocket URLs to consumers
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Chat endpoints
    re_path(
        r'ws/chat/conversation/(?P<conversation_id>\w+)/$',
        consumers.ChatConsumer.as_asgi(),
        name='websocket-chat'
    ),
    # Notification endpoint
    re_path(
        r'ws/notifications/$',
        consumers.NotificationConsumer.as_asgi(),
        name='websocket-notifications'
    ),
]
