from rest_framework import serializers

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
            "user_id",
            "book_id",
        ]


class BorrowingListSerializer(BorrowingSerializer):
    user_id = UserDetailSerializer()
    book_id = serializers.SlugRelatedField(
        slug_field="title", many=True, read_only=True
    )


class BorrowingDetailSerializer(BorrowingSerializer):
    user_id = UserSerializer(read_only=True)
    book_id = BookSerializer(many=True, read_only=True)
