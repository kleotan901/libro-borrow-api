from rest_framework import serializers

from telegram_notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "user", "connect_token", "chat_id"]
