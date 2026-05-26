"""
Views for chat functionality
Handles HTTP endpoints for chat management
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from .models import ChatConversation, ChatMessage, ChatBlock
from pgs.models import PgListing


@login_required(login_url='user_login')
def chat_list(request):
    """
    Display list of all conversations for the user
    Shows recent conversations with preview
    """
    # Get all conversations where user is participant
    conversations = ChatConversation.objects.filter(
        Q(initiator=request.user) | Q(recipient=request.user),
        is_active=True
    ).select_related('initiator', 'recipient', 'pg').prefetch_related('messages').order_by('-last_message_at')

    # Get unread message count for each conversation
    conversations_data = []
    for conv in conversations:
        unread_count = conv.get_unread_count(request.user)
        last_message = conv.messages.first()

        conversations_data.append({
            'conversation': conv,
            'unread_count': unread_count,
            'last_message': last_message,
            'other_user': conv.recipient if conv.initiator == request.user else conv.initiator,
        })

    context = {
        'conversations': conversations_data,
        'page': 'chat',
    }

    return render(request, 'chat/chat_list.html', context)


@login_required(login_url='user_login')
def chat_detail(request, conversation_id):
    """
    Display chat conversation detail page
    Shows messages and provides WebSocket connection
    """
    conversation = get_object_or_404(
        ChatConversation,
        id=conversation_id
    )

    # Check if user is part of this conversation
    if request.user not in [conversation.initiator, conversation.recipient]:
        return redirect('chat_list')

    # Check if user is blocked
    other_user = conversation.recipient if conversation.initiator == request.user else conversation.initiator
    is_blocked = ChatBlock.objects.filter(
        blocker=other_user,
        blocked_user=request.user
    ).exists()

    if is_blocked:
        context = {'error_message': 'You have been blocked by this user.'}
        return render(request, 'chat/blocked.html', context)

    # Get chat messages (last 50)
    messages = conversation.messages.select_related('sender', 'receiver').order_by('-created_at')[:50]
    messages = list(reversed(messages))  # Reverse to show chronological order

    # Mark all received messages as read
    ChatMessage.objects.filter(
        conversation=conversation,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    context = {
        'conversation': conversation,
        'other_user': other_user,
        'messages': messages,
        'page': 'chat',
    }

    return render(request, 'chat/chat_detail.html', context)


@login_required(login_url='user_login')
@require_http_methods(['GET', 'POST'])
def start_chat(request, user_id=None, pg_slug=None):
    """
    Start a new chat conversation with a user
    Accepts either user_id or pg_slug as parameter
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # Determine recipient
    recipient = None
    pg = None

    if user_id:
        recipient = get_object_or_404(User, id=user_id)
    elif pg_slug:
        pg = get_object_or_404(PgListing, slug=pg_slug)
        recipient = pg.owner

    if not recipient:
        return redirect('chat_list')

    # Can't chat with yourself
    if request.user == recipient:
        return redirect('chat_list')

    # Check if conversation already exists
    conversation, created = ChatConversation.objects.get_or_create(
        initiator=request.user,
        recipient=recipient,
        pg=pg
    )

    # Also check reverse (initiator and recipient might be swapped)
    if not created:
        existing = ChatConversation.objects.filter(
            initiator=recipient,
            recipient=request.user,
            pg=pg
        ).first()

        if existing:
            conversation = existing

    return redirect('chat_detail', conversation_id=conversation.id)


@login_required(login_url='user_login')
@require_http_methods(['POST'])
def block_user(request, conversation_id):
    """
    Block a user from chatting
    """
    conversation = get_object_or_404(
        ChatConversation,
        id=conversation_id
    )

    # Check if user is part of this conversation
    if request.user not in [conversation.initiator, conversation.recipient]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Get the other user
    other_user = conversation.recipient if conversation.initiator == request.user else conversation.initiator

    # Create or update block
    block, created = ChatBlock.objects.get_or_create(
        blocker=request.user,
        blocked_user=other_user
    )

    # Deactivate conversation
    conversation.is_active = False
    conversation.save()

    return JsonResponse({'status': 'success', 'message': 'User blocked'})


@login_required(login_url='user_login')
@require_http_methods(['POST'])
def unblock_user(request, user_id):
    """
    Unblock a user
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    user = get_object_or_404(User, id=user_id)

    # Delete block
    ChatBlock.objects.filter(
        blocker=request.user,
        blocked_user=user
    ).delete()

    return JsonResponse({'status': 'success', 'message': 'User unblocked'})


@login_required(login_url='user_login')
def chat_api_messages(request, conversation_id):
    """
    API endpoint to get messages for a conversation
    Used for pagination and initial load
    """
    conversation = get_object_or_404(
        ChatConversation,
        id=conversation_id
    )

    # Check if user is part of this conversation
    if request.user not in [conversation.initiator, conversation.recipient]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Get limit and offset from query params
    limit = int(request.GET.get('limit', 50))
    offset = int(request.GET.get('offset', 0))

    # Get messages
    messages = conversation.messages.select_related(
        'sender', 'receiver'
    ).order_by('-created_at')[offset:offset + limit]

    messages_data = [{
        'id': msg.id,
        'sender': {
            'id': msg.sender.id,
            'username': msg.sender.username,
            'name': f"{msg.sender.first_name} {msg.sender.last_name}",
        },
        'receiver': {
            'id': msg.receiver.id,
            'username': msg.receiver.username,
        },
        'content': msg.content,
        'timestamp': msg.created_at.isoformat(),
        'is_read': msg.is_read,
        'message_type': msg.message_type,
    } for msg in reversed(messages)]

    return JsonResponse({
        'messages': messages_data,
        'total_count': conversation.messages.count(),
    })


@login_required(login_url='user_login')
def blocked_users(request):
    """
    Display list of blocked users
    """
    blocked = ChatBlock.objects.filter(blocker=request.user).select_related('blocked_user')

    context = {
        'blocked_users': blocked,
        'page': 'chat',
    }

    return render(request, 'chat/blocked_users.html', context)

