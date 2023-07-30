from django.db import models


class Book(models.Model):
    ENUM = [("HARD", "HARD"), ("SOFT", "SOFT")]

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=20, choices=ENUM)
    inventory = models.IntegerField()
    daily_fee = models.DecimalField(decimal_places=2, max_digits=1200)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return f"{self.title}({self.author})"
