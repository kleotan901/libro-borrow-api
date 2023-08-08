import datetime

import requests
from celery import shared_task
from django.conf import settings
from django.shortcuts import get_object_or_404

from borrowings.models import Borrowing
from telegram_notifications.models import Notification
from users.models import User

bot_key = settings.BOT_TOKEN


@shared_task
def send_message_new_borrowing(chat_id, message_text):
    if chat_id:
        send_message_url = f"{settings.TELEGRAM_API_URL}bot{bot_key}/sendMessage?chat_id={chat_id}&text={message_text}"
        requests.post(send_message_url)
        return "Message sent"
    return "No chat_id"


@shared_task
def get_borrowings_for_user(chat_id):
    user = get_object_or_404(Notification, chat_id=chat_id).user
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


@shared_task
def daily_message_borrowings_overdue():
    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=datetime.datetime.today()
        + datetime.timedelta(days=1),
        actual_return_date__isnull=True,
    )
    admin = get_object_or_404(User, is_staff=True)
    chat_id = get_object_or_404(Notification, user=admin.id).chat_id
    borrowings_dict = {}
    text = "No borrowings overdue today!"
    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            user = borrowing.user_id.email
            book = f" - {borrowing.book_id.title} ({borrowing.expected_return_date}); "
            if user in borrowings_dict:
                borrowings_dict[user] += book
            else:
                borrowings_dict[user] = book
        text = f"Borrowings overdue:\n{borrowings_dict}"
    send_message_url = f"{settings.TELEGRAM_API_URL}bot{bot_key}/sendMessage?chat_id={chat_id}&text={text}"
    requests.post(send_message_url)
