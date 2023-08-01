from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
)


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
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
        return BorrowingSerializer

    def get_queryset(self):
        """Filtered borrowings by user_id and is_active"""
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
        serializer.save()
        borrowed_book = serializer.data["book_id"]
        book = Book.objects.get(id=borrowed_book)
        book.inventory -= 1
        book.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
