from django.conf import settings
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from telegram_notifications.models import Notification
from telegram_notifications.serializers import NotificationSerializer


class NotificationViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = (IsAdminUser,)

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user)

    @action(
        methods=["get"],
        url_path="start",
        detail=False,
        permission_classes=(IsAuthenticated,),
    )
    def start(self, request):
        """Endpoint send link to Telegram Bot"""
        user_notification = Notification.objects.get(user=request.user.id)
        connect_token = user_notification.connect_token
        if not connect_token:
            return Response(
                {"error": "Connect token not found for this user"},
                status=status.HTTP_404_NOT_FOUND,
            )
        telegram_url = settings.TELEGRAM_URL
        bot_name = settings.BOT_NAME
        url = f"{telegram_url}/{bot_name}?start={connect_token}"
        return Response({"telegram bot link": url}, status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        """Displays info only for admin users"""
        return super().list(self, request, *args, **kwargs)
