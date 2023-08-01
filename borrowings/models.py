from django.conf import settings
from django.db import models
from rest_framework.exceptions import ValidationError

from books.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField()
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="borrowings", on_delete=models.CASCADE
    )
    book_id = models.ForeignKey(
        Book, related_name="borrowings", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.book_id} - {self.borrow_date}"

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        super(Borrowing, self).save(force_insert, force_update, using, update_fields)

    @staticmethod
    def validate_date_fields(borrow_date, expected_return_date, actual_return_date):
        if borrow_date > expected_return_date:
            raise ValidationError(
                "Expected return date cannot be earlier than the borrow date."
            )
        if actual_return_date:
            if borrow_date > actual_return_date:
                raise ValidationError(
                    "Actual return date cannot be earlier than the borrow date."
                )

    def clean(self):
        Borrowing.validate_date_fields(
            self.borrow_date, self.expected_return_date, self.actual_return_date
        )
