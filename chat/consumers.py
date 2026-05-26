"""
WebSocket Consumers for Real-time Chat

This module handles WebSocket connections and manages real-time messaging
between PG seekers and owners.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import ChatMessage, ChatConversation, ChatBlock


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat messaging
    Handles connection, message sending/receiving, and disconnect
    """

    async def connect(self):
        """
        Handle WebSocket connection
        """
        self.user = self.scope['user']
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Check if user is blocked
        is_blocked = await self.check_if_blocked()
        if is_blocked:
            await self.close()
            return

        # Accept connection
        await self.accept()

        # Notify that user is online
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_join',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        )

    async def disconnect(self, close_code):
        """
        Handle WebSocket disconnect
        """
        # Notify that user is offline
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_leave',
                'user_id': self.user.id,
                'username': self.user.username,
            }
        )

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Receive message from WebSocket
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'mark_as_read':
                await self.handle_mark_as_read(data)
            elif message_type == 'typing':
                await self.handle_typing(data)

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))

    async def handle_chat_message(self, data):
        """
        Handle incoming chat message
        """
        content = data.get('message', '').strip()

        if not content:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message cannot be empty'
            }))
            return

        # Save message to database
        message = await self.save_message(content)

        if message:
            # Broadcast to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message_id': message.id,
                    'sender_id': self.user.id,
                    'sender_username': self.user.username,
                    'sender_name': f"{self.user.first_name} {self.user.last_name}",
                    'content': message.content,
                    'timestamp': message.created_at.isoformat(),
                    'is_read': message.is_read,
                }
            )

    async def handle_mark_as_read(self, data):
        """
        Handle message read status update
        """
        message_id = data.get('message_id')
        await self.mark_message_as_read(message_id, self.user.id)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'message_read',
                'message_id': message_id,
                'user_id': self.user.id,
            }
        )

    async def handle_typing(self, data):
        """
        Handle typing indicator
        """
        is_typing = data.get('is_typing', False)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user.id,
                'username': self.user.username,
                'is_typing': is_typing,
            }
        )

    # Handlers for messages from channel layer

    async def chat_message(self, event):
        """
        Send chat message to WebSocket
        """
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message_id': event['message_id'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'sender_name': event['sender_name'],
            'content': event['content'],
            'timestamp': event['timestamp'],
            'is_read': event['is_read'],
        }))

    async def user_join(self, event):
        """
        Notify when user joins the chat
        """
        # Don't notify self of their join
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'user_join',
                'user_id': event['user_id'],
                'username': event['username'],
            }))

    async def user_leave(self, event):
        """
        Notify when user leaves the chat
        """
        await self.send(text_data=json.dumps({
            'type': 'user_leave',
            'user_id': event['user_id'],
            'username': event['username'],
        }))

    async def message_read(self, event):
        """
        Notify when message is read
        """
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id'],
            'user_id': event['user_id'],
        }))

    async def typing_indicator(self, event):
        """
        Send typing indicator
        """
        await self.send(text_data=json.dumps({
            'type': 'typing_indicator',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing'],
        }))

    # Database operations (wrapped with database_sync_to_async)

    @database_sync_to_async
    def check_if_blocked(self):
        """
        Check if the user is blocked from this conversation
        """
        try:
            conversation = ChatConversation.objects.get(id=self.conversation_id)

            # Get other user in conversation
            if conversation.initiator == self.user:
                other_user = conversation.recipient
            else:
                other_user = conversation.initiator

            # Check if blocked by other user
            is_blocked = ChatBlock.objects.filter(
                blocker=other_user,
                blocked_user=self.user
            ).exists()

            return is_blocked
        except ChatConversation.DoesNotExist:
            return True

    @database_sync_to_async
    def save_message(self, content):
        """
        Save message to database
        """
        try:
            conversation = ChatConversation.objects.get(id=self.conversation_id)

            # Get receiver
            if conversation.initiator == self.user:
                receiver = conversation.recipient
            else:
                receiver = conversation.initiator

            # Create message
            message = ChatMessage.objects.create(
                conversation=conversation,
                sender=self.user,
                receiver=receiver,
                content=content,
                message_type='text',
            )

            # Update conversation timestamp
            conversation.last_message_at = timezone.now()
            conversation.save()

            return message

        except Exception as e:
            return None

    @database_sync_to_async
    def mark_message_as_read(self, message_id, user_id):
        """
        Mark message as read
        """
        try:
            message = ChatMessage.objects.get(id=message_id, receiver_id=user_id)
            message.mark_as_read()
            return True
        except ChatMessage.DoesNotExist:
            return False


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    """

    async def connect(self):
        """
        Handle notification connection
        """
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close()
            return

        self.user_group_name = f'user_{self.user.id}_notifications'

        # Join notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Handle notification disconnect
        """
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    async def notification_message(self, event):
        """
        Send notification to user
        """
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification_id': event.get('notification_id'),
            'title': event.get('title'),
            'message': event.get('message'),
            'notification_type': event.get('notification_type'),
            'timestamp': event.get('timestamp'),
        }))
