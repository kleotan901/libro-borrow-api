from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from telegram_notifications.models import Notification
from telegram_notifications.serializers import NotificationSerializer
from telegram_notifications.tasks import webhook


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user)

    @action(methods=["post"], url_path="start", detail=False)
    def start(self, request):
        telegram_url = settings.TELEGRAM_URL
        bot_name = settings.BOT_NAME
        connect_token = Notification.objects.get(user=request.user.id).connect_token
        url = f"{telegram_url}/{bot_name}?start={connect_token}"

        user_id = request.user.id
        webhook.delay(user_id)
        return Response({"telegram bot start": url})
