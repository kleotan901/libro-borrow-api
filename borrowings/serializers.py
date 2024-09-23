from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from books.models import Book
from books.serializers import BookSerializer
from borrowings.fine_calculation import fine_multiplier
from borrowings.models import Borrowing
from payments.models import Payment
from payments.serializers import PaymentSerializer
from payments.stripe_payment import calculate_money_to_pay, create_checkout_session
from users.serializers import UserSerializer, UserDetailSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(read_only=True, many=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book_id",
            "payments",
        ]

    def validate(self, attrs):
        book = Book.objects.get(id=attrs["book_id"].id)
        if book.inventory == 0:
            raise ValidationError("Sorry, this book is out of stock")
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


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ["id", "book_id", "borrow_date", "expected_return_date"]


class BorrowingReturnSerializer(BorrowingSerializer):
    expected_return_date = serializers.SlugRelatedField(
        slug_field="expected_return_date", read_only=True
    )

    class Meta:
        model = Borrowing
        fields = ["id", "book_id", "expected_return_date", "actual_return_date"]


class BorrowingDetailSerializer(serializers.ModelSerializer):
    user_id = UserSerializer(read_only=True)
    book_id = BookSerializer(read_only=True)
    total_fee = serializers.SerializerMethodField()
    payment_session = serializers.SerializerMethodField()
    fine = serializers.SerializerMethodField()
    fine_payment_session = serializers.SerializerMethodField()

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
            "payment_session",
            "fine",
            "fine_payment_session",
        ]

    def get_total_fee(self, obj):
        total_fee = calculate_money_to_pay(obj)
        return total_fee

    def get_fine(self, obj):
        fine_payment = "No fines"
        if obj.actual_return_date:
            if obj.actual_return_date > obj.expected_return_date:
                fine_payment = fine_multiplier(obj)

        return fine_payment

    def get_payment_session(self, obj):
        latest_payment = (
            Payment.objects.filter(
                borrowing_id=obj.id, payment_type="PAYMENT", status="PENDING"
            )
            .order_by("-id")
            .first()
        )
        if latest_payment:
            return {
                "id": latest_payment.id,
                "payment_session": latest_payment.session_url,
            }

    def get_fine_payment_session(self, obj):
        latest_payment = (
            Payment.objects.filter(
                borrowing_id=obj.id, payment_type="FINE", status="PENDING"
            )
            .order_by("-id")
            .first()
        )
        if latest_payment:
            return {
                "id": latest_payment.id,
                "fine_payment_session": latest_payment.session_url,
            }
