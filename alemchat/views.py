from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import get_or_create_chatroom,ChatRoom, Message, Block
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
# Create your views here.


@login_required
@require_POST
def send_message(request):
    if request.method == "POST":
        chatroom_id = request.POST.get("chatroom_id")
        message_text = request.POST.get("message", "")
        image = request.FILES.get("image")

        chat = ChatRoom.objects.get(id=chatroom_id)

        msg = Message.objects.create(
            chatroom=chat,
            sender=request.user,
            content=message_text,
            image=image
        ) 
        if Block.objects.filter(blocker=msg.sender.username, blocked=request.user).exists():
            return JsonResponse({"error":"You are blocked"}, status=403)

        return JsonResponse({
            "id": msg.id,
            "content": msg.content,
            "image": msg.image.url if msg.image else None,
            "sender": msg.sender.username
        })


@login_required
@login_required
def fetch_messages(request, chatroom_id):
    chatroom = ChatRoom.objects.get(id=chatroom_id)

    messages = Message.objects.filter(chatroom=chatroom).select_related("sender")

    data = []
    for msg in messages:
        data.append({
            "sender": msg.sender.username,
            "content": msg.content,
            "image":msg.image.url if msg.image else None,
            "id": msg.id,
            "is_read":msg.is_read
        }
        )

    return JsonResponse({"messages": data})


@login_required
def chats_view(request, username=None):
    # All chats (left panel)
    chats_qs = (
        ChatRoom.objects
        .filter(participants=request.user)
        .annotate(
            unread_count=Count(
                "messages",
                filter=Q(messages__is_read=False)
                & ~Q(messages__sender=request.user)
            )
        )
        .prefetch_related("participants")
    )
    blocked_ids = Block.objects.filter(blocker=request.user).values_list("blocked_id", flat=True)
    chats_qs = chats_qs.exclude(participants__id__in=blocked_ids)

    chats = [chat for chat in chats_qs if not chat.is_expired()]

    active_chat = None
    messages = None
    other_user = None

    # If a chat is selected
    if username:
        other_user = get_object_or_404(User, username=username)
        active_chat = get_or_create_chatroom(request.user, other_user)
    
        if active_chat.is_expired():
            return redirect("chat_list")

        # Mark messages as read
        active_chat.messages.filter(
            is_read=False
        ).exclude(sender=request.user).update(is_read=True)

        messages = active_chat.messages.order_by("timestamp")

    return render(request, "chatapp.html", {
        "chats": chats,
        "active_chat": active_chat,
        "messages": messages,
        "other_user": other_user,
        "myself":request.user,
    })
@login_required
@require_POST
def delete_chat(request, chat_id):
    chat = get_object_or_404(ChatRoom, id=chat_id)

    # Only participants can delete
    if request.user not in chat.participants.all():
        return JsonResponse({"error": "Unauthorized"}, status=403)

    chat.delete()
    return JsonResponse({"success": True})

@login_required
@require_POST
def block_user(request, user_id):
    blocked_user = get_object_or_404(User, id=user_id)

    if blocked_user == request.user:
        return JsonResponse({"error": "Cannot block yourself"}, status=400)

    Block.objects.get_or_create(
        blocker=request.user,
        blocked=blocked_user
    )

    # Optional: delete chat between them
    ChatRoom.objects.filter(
        participants=request.user
    ).filter(
        participants=blocked_user
    ).delete()

    return JsonResponse({"success": True})
def cleanup_expired_chats():
    expired_chats = ChatRoom.objects.all()
    for chat in expired_chats:
        if chat.is_expired():
            chat.delete()