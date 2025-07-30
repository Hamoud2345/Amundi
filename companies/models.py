from django.db import models
from django.utils import timezone

# Create your models here.
# companies/models.py
class Company(models.Model):
    name        = models.CharField(max_length=120, unique=True)
    description = models.TextField()
    sector      = models.CharField(max_length=80)
    financials  = models.JSONField(blank=True, default=dict)

    def __str__(self):
        return self.name

class ChatHistory(models.Model):
    user_message = models.TextField()
    bot_response = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = "Chat Histories"
    
    def __str__(self):
        return f"Chat at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
