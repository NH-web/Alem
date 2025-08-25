# alemchat/tasks.py
from celery import shared_task
from alemchat.models import Chat
from datetime import date, timedelta

@shared_task
def delete_expired_chats_task():
    cutoff = date.today() - timedelta(days=20)
    Chat.objects.filter(travel__departure_date__lt=cutoff).delete()

# alemchat/tasks.py
@shared_task
def save_message_task(chat_id, sender_id, content):
    from django.utils import timezone
    from django.contrib.auth import get_user_model
    from .models import Chat, Message
    try:
        chat = Chat.objects.get(id=chat_id)
    except Chat.DoesNotExist:
        return
    if chat.is_expired:
        return
    Message.objects.create(chat_id=chat_id, sender_id=sender_id, content=content)
