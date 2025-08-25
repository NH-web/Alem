from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from .models import TypingPing, ChatRoom, Message
from mainapp.models import TravelInfo, UserProfile

@login_required
def start_chat(request, post_id):
    post = get_object_or_404(TravelInfo, id=post_id)
    owner = post.user
    me = request.user
    if me == owner:
        return redirect('/')
    u1, u2 = sorted([me, owner], key=lambda x: x.id)
    chat, _ = ChatRoom.objects.get_or_create(post=post, user1=u1, user2=u2)
    TypingPing.objects.get_or_create(chat=chat)
    return redirect('chat_room', chat_id=chat.id)

@login_required
def chat_room(request, chat_id):
    if request.is_mobile:
        chat = get_object_or_404(ChatRoom, id=chat_id)
        if request.user not in (chat.user1, chat.user2):
            return HttpResponseForbidden("Not your Chat")
        other = chat.other(request.user)
        #load last 50 messages initially

        initial = list(chat.messages.select_related("sender").order_by("-id")[:50])
        initial.reverse()
        return render(request, "chat_room_mobile2.html", {"chat":chat, "other":other, "initial_messages":initial})
        
    chats = ChatRoom.objects.filter(Q(user1=request.user) | Q(user2=request.user)).select_related('post','user1','user2').prefetch_related('messages')
    chat = get_object_or_404(ChatRoom, id=chat_id)
    print (request.user.userprofile.profile_picture)
    chat_list = []
    for c in chats:
        last = c.messages.order_by('-id').first()
        unread = c.unread_count(request.user)
        other_user = c.user1 if c.user2 == request.user else c.user2

        chat_list.append({
            "chat":c,
            "last":last,
            "unread":unread,
            "other_user":other_user
        })
    if request.user not in (chat.user1, chat.user2):
        return HttpResponseForbidden("Not your Chat")
    other = chat.other(request.user)
    #load last 50 messages initially
    initial = list(chat.messages.select_related("sender").order_by("-id")[:50])
    initial.reverse()
    return render(request, "chat_room2.html", {"chat":chat, "other":other, "initial_messages":initial,"chat_list":chat_list})

@login_required
def inbox(request):
    
    chats = ChatRoom.objects.filter(Q(user1=request.user) | Q(user2=request.user)).select_related('post','user1','user2').prefetch_related('messages')
    if not request.is_mobile:
        if chats.exists():
            return redirect(f'/chat/chat/{chats[0].id}/')
        else:
            return render(request, 'nochat.html', {"message":"No Chat Yet"})
    chat_list = []
    for c in chats:
        last = c.messages.order_by('-id').first()
        unread = c.unread_count(request.user)
        other_user = c.user1 if c.user2 == request.user else c.user2

        chat_list.append({
            "chat":c,
            "last":last,
            "unread":unread,
            "other_user":other_user
        })
    return render(request, 'mobile_inbox.html', {"chat_list": chat_list})
@login_required
def api_send_message(request, chat_id):
    if request.method != "POST":
        return JsonResponse({"error":"POST only"}, status=405)
    chat = get_object_or_404(ChatRoom, id=chat_id)
    if request.user not in (chat.user1, chat.user2):
        return JsonResponse({"error": "Forbidden"}, status=403)
    
    text = (request.POST.get("text") or "").strip()
    if not text:
        return JsonResponse({"error": "Empty"}, status=400)
    msg = Message.objects.create(chat=chat, sender=request.user, text=text)
    return JsonResponse({
        "id": msg.id,
        "sender": msg.sender.username,
        "text":msg.text,
        "created_at":msg.created_at.isoformat(),
    }, status=201)

@login_required
def api_fetch_messages(request, chat_id):
    chat = get_object_or_404(ChatRoom, id=chat_id)
    if request.user not in (chat.user1, chat.user2):
        return JsonResponse({"error":"Forbidden"}, status=403)
    
    after_id = request.GET.get("after_id")
    qs = chat.messages.select_related("sender")
    if after_id and after_id.isdigit():
        qs = qs.filter(id__gt=int(after_id))
    msgs = list(qs.order_by("id")[:200])

    #mark as read for messages from the other side 
    chat.messages.filter(
        sender=chat.other(request.user),
        is_read=False
    ).update(is_read=True)
    return JsonResponse({
        "messages":[{
            "id":m.id,
            "sender":m.sender.username,
            "mine":(m.sender_id == request.user.id),
            "text":m.text,
            "created_at":m.created_at.isoformat(),
        } for m in msgs],
        "typing": TypingPing.is_typing(chat, request.user),
    })

@login_required
def api_typing_ping(request, chat_id):
    if request.method != "POST":
        return JsonResponse({"ok": False}, status=405)
    chat = get_object_or_404(ChatRoom, id=chat_id)
    if request.user not in (chat.user1, chat.user2):
        return JsonResponse({"ok":False}, status=403)
    tp, _ = TypingPing.objects.get_or_create(chat=chat)
    now = timezone.now()
    if request.user == chat.user1:
        tp.user1_ping = now
    else:
        tp.user2_ping = now
    tp.save(update_fields=["user1_ping","user2_ping"])
    return JsonResponse({"ok":True})

