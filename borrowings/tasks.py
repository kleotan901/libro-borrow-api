import requests
from celery import shared_task
from django.conf import settings

bot_key = settings.BOT_TOKEN


@shared_task
def send_message_new_borrowing(chat_id, message_text):
    send_message_url = f"{settings.TELEGRAM_API_URL}bot{bot_key}/sendMessage?chat_id={chat_id}&text={message_text}"
    requests.post(send_message_url)
    return "Message sent"
