from django.db import models

from borrowings.models import Borrowing


class Payment(models.Model):
    ENUM_STATUS = [("PENDING", "pending"), ("PAID", "paid"), ("EXPIRED", "expired")]
    ENUM_TYPE = [("PAYMENT", "payment"), ("FINE", "fine")]

    status = models.CharField(max_length=20, choices=ENUM_STATUS)
    payment_type = models.CharField(max_length=20, choices=ENUM_TYPE)
    borrowing = models.ForeignKey(
        Borrowing,
        related_name="payments",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=500)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
