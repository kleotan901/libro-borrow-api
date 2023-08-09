from celery import shared_task
from django.shortcuts import get_object_or_404

from telegram_notifications.models import Notification


@shared_task
def save_chat_id(chat_id, connect_token):
    user = get_object_or_404(Notification, connect_token=connect_token)
    user.chat_id = chat_id
    user.save()
    return "chat_id saved"
