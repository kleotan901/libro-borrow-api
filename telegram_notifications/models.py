from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    connect_token = models.CharField(max_length=64, null=True)
    chat_id = models.CharField(max_length=255, null=True)
