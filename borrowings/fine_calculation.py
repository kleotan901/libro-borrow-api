from datetime import datetime

from borrowings.models import Borrowing


def convert_str_to_datetype(serializer):
    actual_return_date_str = serializer.data.get("actual_return_date")
    actual_return_date = datetime.strptime(actual_return_date_str, "%Y-%m-%d").date()

    return actual_return_date


def fine_multiplier(borrowing: Borrowing) -> float | None:
    multiplier = 2
    total_fine = multiplier * borrowing.book_id.daily_fee
    overdue_days = borrowing.actual_return_date - borrowing.expected_return_date
    total_fine *= overdue_days.days
    total_fine = float(total_fine)

    return total_fine
