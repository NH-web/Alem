from django.db import models
from django.utils import timezone
from datetime import timedelta
# Create your models here.
class TemporaryMemory(models.Model):
    email = models.EmailField()
    code = models.IntegerField()
    code_verified = models.BooleanField(default=False)
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    @property
    def code_expired(self):
        return timezone.now() > self.created_at + timedelta(hours=2)
    def __str__(self):
        return f"{self.email} (waiting: {'NO' if self.code_expired else 'YES'})"