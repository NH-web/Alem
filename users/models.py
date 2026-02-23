from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, datetime
# Create your models here.
class TemporaryMemory(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    code = models.IntegerField()
    code_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    attempts = models.IntegerField(default=0)
    @property
    def code_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)
    def __str__(self):
        return f"{self.phone} (waiting: {'NO' if self.code_expired else 'YES'})"
