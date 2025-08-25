# chat/management/commands/cleanup_chats.py
from django.core.management.base import BaseCommand
from alemchat.models import ChatRoom

class Command(BaseCommand):
    help = "Deletes chats 20 days after departure date"

    def handle(self, *args, **kwargs):
        for chat in ChatRoom.objects.all():
            if chat.is_expired():
                chat.delete()
        self.stdout.write(self.style.SUCCESS("Old chats deleted successfully"))
