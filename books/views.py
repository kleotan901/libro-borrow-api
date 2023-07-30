from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from books.models import Book
from books.permissions import IsAdminOrIfAuthenticatedReadOnly
from books.serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    serializer_class = BookSerializer
    queryset = Book.objects.all()
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_permissions(self):
        if self.action == "list":
            return (AllowAny(),)
        return (IsAdminOrIfAuthenticatedReadOnly(),)
