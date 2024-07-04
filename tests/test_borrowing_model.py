from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from telegram_notifications.models import Notification

BORROWINGS_URL = reverse("borrowings:borrowing-list")


def detail_url(borrowing_id):
    return reverse("borrowings:borrowing-detail", args=[borrowing_id])


class BorrowingModelTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            email="test1@email.com", password="password"
        )
        Notification.objects.create(user=user, connect_token="bJHGBKdNsPo")
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
        self.client = APIClient()
        self.client.force_authenticate(user)

    def test_borrowing_str(self):
        borrowing = Borrowing.objects.get(pk=1)
        self.assertEqual(
            str(borrowing),
            f"{borrowing.book_id} - {borrowing.borrow_date}",
        )

    def test_total_borrowing_fee(self):
        borrowing = Borrowing.objects.get(pk=1)
        borrowing.actual_return_date = "2023-08-03"
        borrowing.save()
        actual_period = borrowing.actual_return_date - borrowing.borrow_date
        total_fee = actual_period.days * borrowing.book_id.daily_fee

        self.assertEqual(actual_period.days, 4)
        self.assertEqual(float(total_fee), 5.60 * 4)
