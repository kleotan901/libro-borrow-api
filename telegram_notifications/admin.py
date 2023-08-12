from django.contrib import admin

from telegram_notifications.models import Notification

admin.site.register(Notification)
