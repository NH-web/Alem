from django.db import models
from django.contrib.auth.models import User
from mainapp.models import TravelInfo
from django.utils import timezone
from datetime import timedelta
# Create your models here.
class ChatRoom(models.Model):
    travel = models.ForeignKey(TravelInfo, on_delete=models.CASCADE, related_name="chats", blank=True, null=True)
    participants = models.ManyToManyField(
        User,
        related_name="chatrooms"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        if not self.travel:
            return False
        
        return self.travel.departure_date + timedelta(days=30)
    def __str__(self):
        return f"ChatRoom {self.id}"

class Message(models.Model):
    chatroom = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_messages"   
    )
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="chat_images/", blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.sender} -> Room {self.chatroom.id}"

class UserStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_seen = models.DateTimeField(default=timezone.now)

    @property
    def is_online(self):
        return timezone.now() - self.last_seen < timedelta(seconds=30)

class Block(models.Model):
    blocker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blocked_users"
    )
    blocked = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blocked_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("blocker", "blocked")

def get_or_create_chatroom(user1, user2):
    chatrooms = ChatRoom.objects.filter(participants=user1).filter(participants=user2)
    
    if chatrooms.exists():
        return chatrooms.first()
    chatroom = ChatRoom.objects.create()
    chatroom.participants.add(user1,user2)
    return chatroom
