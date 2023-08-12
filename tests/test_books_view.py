from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookSerializer

BOOKS_URL = reverse("books:book-list")


def detail_url(book_id):
    return reverse("books:book-detail", args=[book_id])


class UnauthorizedUserBookViewSetTest(TestCase):
    def setUp(self):
        Book.objects.create(
            title="Book 1", author="John Smith", daily_fee=5.60, inventory=30
        )
        Book.objects.create(
            title="Book 2", author="Bob Lee", daily_fee=4.90, inventory=55
        )
        self.client = APIClient()

    def test_get_books_list(self):
        books_list = Book.objects.all()
        result = self.client.get(BOOKS_URL)
        serializer = BookSerializer(books_list, many=True)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        self.assertEqual(books_list.count(), 2)

    def test_retrieve_book(self):
        url = detail_url(book_id=1)
        result = self.client.get(url)
        self.assertEqual(result.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedUserBookViewSetTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            email="test1@email.com", password="password"
        )
        Book.objects.create(
            title="Book 1", author="John Smith", daily_fee=5.60, inventory=30
        )
        Book.objects.create(
            title="Book 2", author="Bob Lee", daily_fee=4.90, inventory=55
        )
        self.client = APIClient()
        self.client = APIClient()
        self.client.force_authenticate(user)

    def test_retrieve_book(self):
        book = Book.objects.get(id=1)
        url = detail_url(book.id)
        result = self.client.get(url)
        serializer = BookSerializer(book)

        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)

    def test_book_creat_forbidden(self):
        payload = {
            "title": "Test1",
            "author": "Name",
            "daily_fee": 3.10,
            "inventory": 70,
        }
        result = self.client.post(BOOKS_URL, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_update_forbidden(self):
        book = Book.objects.get(id=1)
        payload = {
            "title": "Test1",
            "author": "Name",
            "daily_fee": 3.10,
            "inventory": 70,
        }
        url = detail_url(book.id)
        result = self.client.put(url, payload)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)

    def test_book_delete_forbidden(self):
        book = Book.objects.get(id=1)
        url = detail_url(book.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_403_FORBIDDEN)


class AdminUserBookViewSetTest(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_superuser(
            email="admin@email.com", password="password"
        )
        Book.objects.create(
            title="Book 1", author="John Smith", daily_fee=5.60, inventory=30
        )
        Book.objects.create(
            title="Book 2", author="Bob Lee", daily_fee=4.90, inventory=55
        )
        self.client = APIClient()
        self.client = APIClient()
        self.client.force_authenticate(user)

    def test_create_book(self):
        payload = {
            "title": "New test book",
            "author": "Name",
            "cover": "HARD",
            "inventory": 70,
            "daily_fee": 3.10,
        }
        result = self.client.post(BOOKS_URL, data=payload)
        book = Book.objects.get(title="New test book")

        self.assertEqual(result.status_code, status.HTTP_201_CREATED)
        self.assertEqual(result.data["title"], book.title)

    def test_update_book(self):
        book = Book.objects.get(id=1)
        payload = {
            "title": "Test1",
            "author": "Name",
            "cover": "HARD",
            "inventory": 70,
            "daily_fee": 3.10,
        }
        url = detail_url(book.id)
        result = self.client.put(url, data=payload)
        serializer = BookSerializer(book, data=payload)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertTrue(serializer.is_valid())
        self.assertEqual(result.status_code, status.HTTP_200_OK)
        self.assertEqual(result.data, serializer.data)
        self.assertEqual(book.title, "Test1")

    def test_delete_book(self):
        book = Book.objects.get(id=1)
        url = detail_url(book.id)
        result = self.client.delete(url)

        self.assertEqual(result.status_code, status.HTTP_204_NO_CONTENT)
