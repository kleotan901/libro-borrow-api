import requests
from celery import shared_task
from django.conf import settings
from django.shortcuts import get_object_or_404
from telebot.types import Update

from telegram_notifications.models import Notification


@shared_task
def set_webhook(user_id):
    bot_key = settings.BOT_TOKEN
    updates_url = f"https://api.telegram.org/bot{bot_key}/getUpdates"
    response = requests.get(updates_url).json()
    updates = response.get("result")
    if updates:
        latest_update = updates[-1]
        update = Update.de_json(latest_update)
        chat_id = update.message.chat.id
        user = get_object_or_404(Notification, user_id=user_id)
        user.chat_id = chat_id
        user.save()
        return {"message": "Webhook configured successfully."}
    return {"message": "No updates found."}
