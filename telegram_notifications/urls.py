from django.urls import path, include
from rest_framework import routers

from telegram_notifications.views import NotificationViewSet

app_name = "telegram-notifications"

router = routers.DefaultRouter()
router.register("", NotificationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
