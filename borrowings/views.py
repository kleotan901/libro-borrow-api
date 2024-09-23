import datetime

from drf_spectacular.utils import extend_schema, OpenApiParameter

from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from books.models import Book
from borrowings.fine_calculation import fine_multiplier, convert_str_to_datetype
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingReturnSerializer,
    BorrowingCreateSerializer,
)

from borrowings.tasks import send_message_new_borrowing
from payments.models import Payment
from payments.stripe_payment import create_checkout_session, calculate_money_to_pay
from telegram_notifications.models import Notification


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    GenericViewSet,
):
    serializer_class = BorrowingSerializer
    queryset = Borrowing.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "return_book":
            return BorrowingReturnSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer

    def get_queryset(self):
        """Retrieve borrowings filtered by user_id and is_active"""
        queryset = self.queryset

        is_user = self.request.query_params.get("is_user")
        is_active = self.request.query_params.get("is_active")

        if is_user:
            queryset = Borrowing.objects.filter(user_id=is_user)

        if is_active:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        if not self.request.user.is_staff:
            queryset = queryset.filter(user_id=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        borrowed_book = serializer.data.get("book_id")
        book = Book.objects.get(id=borrowed_book)
        if book.inventory == 0:
            return Response(
                {"message": f"Sorry, book {book.title} is out of stock"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.get(id=serializer.data["id"])
        money_to_pay = calculate_money_to_pay(borrowing)

        checkout_session = create_checkout_session(borrowing, money_to_pay)
        Payment.objects.create(
            borrowing=borrowing,
            session_url=checkout_session.url,
            session_id=checkout_session.id,
            amount=money_to_pay,
            payment_type="PAYMENT",
            status="PENDING",
        )

        # Sent a message
        message_text = f"Borrowing created - {book.title}({book.author})"
        chat_id = Notification.objects.get(user=request.user.id).chat_id
        send_message_new_borrowing.delay(chat_id, message_text)

        return Response(
            {"borrowing_data": serializer.data, "payment_url": checkout_session.url},
            status=status.HTTP_201_CREATED,
        )

    @action(methods=["put"], detail=True, url_path="return")
    def return_book(self, request, pk):
        """Endpoint for return book"""
        borrowing = Borrowing.objects.get(id=pk)
        if borrowing.actual_return_date:
            return Response(
                {"message": "This book has already been returned"},
                status=status.HTTP_200_OK,
            )

        if borrowing.user_id.id == request.user.id:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            actual_return_date = convert_str_to_datetype(serializer)
            if not actual_return_date:
                return Response(
                    {"error": "Actual_return_date field can't be blank"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            borrowing.actual_return_date = actual_return_date

            # return book
            book = Book.objects.get(id=borrowing.book_id.id)
            book.inventory += 1
            book.save()

            borrowing.save()

            # if borrowing is overdue
            if borrowing.actual_return_date > borrowing.expected_return_date:
                fine_amount = fine_multiplier(borrowing)
                # create fine payment session
                checkout_session = create_checkout_session(borrowing, fine_amount)
                fine_session = Payment.objects.create(
                    borrowing=borrowing,
                    session_url=checkout_session.url,
                    session_id=checkout_session.id,
                    amount=fine_amount,
                    payment_type="FINE",
                    status="PENDING",
                )
                return Response(
                    {
                        "message": "Book is returned",
                        "fine_payment": fine_session.session_url,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response({"message": "Book is returned"}, status=status.HTTP_200_OK)

        return Response(
            {"message": "User has no rights to return this book"},
            status=status.HTTP_403_FORBIDDEN,
        )

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_user",
                description="Filter borrowings by user id (ex. ?is_user=1)",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_active",
                description="Filter borrowings by is_active (ex. ?is_active=true or ?is_active=false)",
                required=False,
                type=str,
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(self, request, *args, **kwargs)
