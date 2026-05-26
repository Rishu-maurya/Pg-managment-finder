from django.db import models
from users.models import MyUser as User
from pgs.models import PgListing


class ChatConversation(models.Model):
    """
    Chat Conversation Model for one-on-one messaging
    between PG Seeker and PG Owner
    """
    # Participants
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="initiated_conversations")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_conversations")

    # Related to a specific PG listing
    pg = models.ForeignKey(PgListing, on_delete=models.CASCADE, related_name="conversations", blank=True, null=True)

    # Conversation metadata
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["-last_message_at", "-created_at"]
        unique_together = ("initiator", "recipient", "pg")

    def __str__(self):
        return f"Chat: {self.initiator.email} ↔ {self.recipient.email}"

    def get_unread_count(self, user):
        """Get count of unread messages for a specific user"""
        return self.messages.filter(receiver=user, is_read=False).count()


class ChatMessage(models.Model):
    """
    ChatMessage Model for individual messages
    Supports text messages with optional file attachments
    """
    MESSAGE_TYPE_CHOICES = [
        ("text", "Text"),
        ("image", "Image"),
        ("file", "File"),
        ("document", "Document"),
    ]

    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")

    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPE_CHOICES, default="text")
    content = models.TextField()

    # File attachment (optional)
    attachment = models.FileField(upload_to="chat_attachments/", blank=True, null=True)

    # Message status
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message from {self.sender.email} to {self.receiver.email}"

    def mark_as_read(self):
        """Mark message as read"""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class ChatBlock(models.Model):
    """
    Chat Block Model to allow users to block other users
    Prevents unwanted messages and interactions
    """
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_users")
    blocked_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked_user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.blocker.email} blocked {self.blocked_user.email}"

