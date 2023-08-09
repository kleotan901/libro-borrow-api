from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book
from books.serializers import BookSerializer
from borrowings.models import Borrowing
from users.serializers import UserSerializer, UserDetailSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_id",
        ]

    def validate(self, attrs):
        book = Book.objects.get(id=attrs["book_id"].id)
        if book.inventory == 0:
            raise ValidationError("The books are over")
        return attrs


class BorrowingListSerializer(BorrowingSerializer):
    user_id = UserDetailSerializer()
    book_id = serializers.SlugRelatedField(slug_field="title", read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "user_id",
            "book_id",
        ]


class BorrowingDetailSerializer(BorrowingSerializer):
    user_id = UserSerializer(read_only=True)
    book_id = BookSerializer(read_only=True)
    total_fee = serializers.CharField(source="total_borrowing_fee", read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "user_id",
            "book_id",
            "total_fee",
        ]
