import datetime
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)
from telegram_notifications.models import Notification

BORROWINGS_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id):
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


class UnauthorizedUserBorrowingViewSetTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            email="test@email.com", password="password"
        )
        book = Book.objects.create(
            title="Sample book", author="test name", daily_fee=5.60, inventory=30
        )
        Borrowing.objects.create(
            borrow_date="2023-07-30",
            expected_return_date="2023-08-09",
            user_id=user,
            book_id=book,
        )

        self.client = APIClient()

    def test_get_borrowing_list(self):
        result = self.client.get(BORROWINGS_URL)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_borrowing(self):
        url = detail_url(borrowing_id=1)
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserBorrowingViewSetTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            email="test1@email.com", password="password"
        )
        user_2 = get_user_model().objects.create_user(
            email="test2@email.com", password="password"
        )
        Notification.objects.create(user=user, connect_token="bJHGBKdNsPo")
        Notification.objects.create(user=user_2, connect_token="OuzGBKdNsTr")
        book = Book.objects.create(
            title="Sample book", author="test name", daily_fee=5.60, inventory=30
        )
        Borrowing.objects.create(
            borrow_date="2023-07-30",
            expected_return_date="2023-08-09",
            user_id=user,
            book_id=book,
        )
        Borrowing.objects.create(
            borrow_date="2023-06-11",
            expected_return_date="2023-06-29",
            user_id=user_2,
            book_id=book,
        )
        Borrowing.objects.create(
            borrow_date="2023-06-11",
            expected_return_date="2023-06-29",
            actual_return_date="2023-06-27",
            user_id=user,
            book_id=book,
        )

        self.client = APIClient()
        self.client = APIClient()
        self.client.force_authenticate(user)

    def test_get_borrowing_list(self):
        result = self.client.get(BORROWINGS_URL)
        user = get_user_model().objects.get(id=1)
        requested_user_borrowings = Borrowing.objects.filter(user_id=user.id)
        serializer = BorrowingListSerializer(requested_user_borrowings, many=True)
        all_borrowings_in_bd = Borrowing.objects.all()

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        self.assertEqual(requested_user_borrowings.count(), 2)
        self.assertEqual(all_borrowings_in_bd.count(), 3)

    def test_get_borrowings_filtered_by_is_active(self):
        user = get_user_model().objects.get(id=1)
        users_borrowings = Borrowing.objects.filter(
            user_id=user.id, actual_return_date__isnull=False
        )
        result = self.client.get(BORROWINGS_URL, {"is_active": "false"})
        serializer = BorrowingListSerializer(users_borrowings, many=True)

        self.assertEqual(serializer.data, result.data)
        self.assertEqual(users_borrowings.count(), 1)

    def test_retrieve_borrowing(self):
        borrowing = Borrowing.objects.get(id=1)
        url = detail_url(borrowing.id)
        result = self.client.get(url)
        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    @patch("borrowings.views.send_message_new_borrowing.delay")
    def test_create_borrowing(self, mock_delay):
        book = Book.objects.get(id=1)
        user = get_user_model().objects.get(id=1)
        payload = {
            "borrow_date": "2023-12-02",
            "expected_return_date": "2023-12-11",
            "user_id": user.id,
            "book_id": book.id,
        }
        result = self.client.post(BORROWINGS_URL, data=payload)
        chat_id = Notification.objects.get(user=user.id).chat_id
        message_text = f"Borrowing created - {book.title}({book.author})"
        mock_delay.assert_called_once_with(chat_id, message_text)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)

    def test_borrowing_update_not_allowed(self):
        borrowing = Borrowing.objects.get(id=1)
        book = Book.objects.get(id=1)
        user = get_user_model().objects.get(id=1)
        payload = {
            "borrow_date": "2023-12-02",
            "expected_return_date": "2023-12-11",
            "user_id": user.id,
            "book_id": book.id,
        }
        url = detail_url(borrowing.id)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_borrowing_delete_not_allowed(self):
        borrowing = Borrowing.objects.get(id=1)
        url = detail_url(borrowing.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_return_book(self):
        borrowing = Borrowing.objects.get(id=1)
        actual_date_before_return = borrowing.actual_return_date
        url = f"http://127.0.0.1:8000/api/borrowings/{borrowing.id}/return/"
        result = self.client.post(url)
        book = borrowing.book_id
        actual_date_after_return = Borrowing.objects.get(id=1).actual_return_date

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(book.inventory, 31)
        self.assertIsNone(actual_date_before_return)
        self.assertEqual(actual_date_after_return, datetime.datetime.today().date())

    @patch("borrowings.views.send_message_new_borrowing.delay")
    def test_notification_create_borrowing(self, mock_delay):
        book = Book.objects.get(id=1)
        user = get_user_model().objects.get(id=1)
        payload = {
            "borrow_date": "2023-12-02",
            "expected_return_date": "2023-12-11",
            "user_id": user.id,
            "book_id": book.id,
        }
        result = self.client.post(BORROWINGS_URL, payload)

        chat_id = Notification.objects.get(user=user.id).chat_id
        message_text = f"Borrowing created - {book.title}({book.author})"
        mock_delay.assert_called_once_with(chat_id, message_text)

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
