# chat/models.py
from django.db import models
from django.contrib.auth.models import User
from mainapp.models import TravelInfo
from django.utils import timezone
from datetime import timedelta

class ChatRoom(models.Model):
    post = models.ForeignKey(TravelInfo, on_delete=models.CASCADE, related_name="chatrooms")
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_user1")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name="chat_user2")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post','user1','user2')
    
    def other(self, me):
        return self.user2 if self.user1 == me else self.user1
    def is_expired(self):
        """Automatically check if chat should be deleted."""
        return timezone.now().date() > (self.travel_post.departure_date + timedelta(days=20))
    def unread_count(self, user):
        return self.messages.filter(sender=self.other(user), is_read=False).count()
class Message(models.Model):
    chat = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["id"]
    def __str__(self):
        return f"{self.sender.username}: {self.text[:30]}"
class TypingPing(models.Model):
    chat = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, related_name="typing")
    user1_ping = models.DateTimeField(null=True, blank=True)
    user2_ping = models.DateTimeField(null=True, blank=True)

    @classmethod
    def is_typing(cls, chat, watcher):
        try:
            t = chat.typing
        except TypingPing.DoesNotExist:
            return False
        now = timezone.now()
        delta = timezone.timedelta(seconds=5)
        
        if watcher == chat.user1:
            return t.user2_ping and (now - t.user2_ping) < delta
        else:
            return t.user1_ping and (now - t.user1_ping) < delta