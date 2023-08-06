import datetime

import requests
from celery import shared_task
from django.conf import settings

from borrowings.models import Borrowing
from telegram_notifications.models import Notification

bot_key = settings.BOT_TOKEN


@shared_task
def send_message_new_borrowing(chat_id, message_text):
    send_message_url = f"{settings.TELEGRAM_API_URL}bot{bot_key}/sendMessage?chat_id={chat_id}&text={message_text}"
    requests.post(send_message_url)
    return "Message sent"


@shared_task
def get_borrowings_for_user(chat_id):
    user = Notification.objects.get(chat_id=chat_id).user
    borrowings = Borrowing.objects.filter(
        user_id=user.id, actual_return_date__isnull=True
    )
    if borrowings.exists():
        text = ""
        for borrowing in borrowings:
            text += f"{borrowing.book_id.title} (expected return date: {borrowing.expected_return_date});\n"
        return text
    return "No borrowings!"


@shared_task
def get_overdue_for_user(chat_id):
    user = Notification.objects.get(chat_id=chat_id).user
    overdue_borrowings = Borrowing.objects.filter(
        user_id=user.id,
        expected_return_date__lt=datetime.datetime.today(),
        actual_return_date__isnull=True,
    )
    if overdue_borrowings.exists():
        text = ""
        for borrowing in overdue_borrowings:
            text += f"{borrowing.book_id.title} (expected return date: {borrowing.expected_return_date});\n"
        return text
    return "No overdue borrowings!"
