import time

import stripe
from django.conf import settings
from stripe.checkout import Session

from borrowings.models import Borrowing

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
HOME_DOMAIN = settings.HOME_DOMAIN


def calculate_money_to_pay(borrowing: Borrowing) -> float:
    borrowing_period = borrowing.expected_return_date - borrowing.borrow_date
    total_amount = borrowing.book_id.daily_fee * borrowing_period.days
    return total_amount


def create_checkout_session(borrowing, money_to_pay: float) -> Session | Exception:
    product = stripe.Product.create(name=borrowing.book_id.title)
    # Convert book.daily_fee to cents
    unit_amount_cents = int(money_to_pay * 100)
    # Create a price for the product
    price = stripe.Price.create(
        product=product.id,
        unit_amount=unit_amount_cents,
        currency="usd",
    )
    # create the Stripe Customer
    customer = stripe.Customer.create(
        email=borrowing.user_id.email,
        name=f"{borrowing.user_id.first_name} {borrowing.user_id.last_name}",
    )

    success_url = f"{settings.HOME_DOMAIN}/api/payments/{borrowing.pk}/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{settings.HOME_DOMAIN}api/payments/cancel/"

    # create the Stripe Session
    checkout_session = stripe.checkout.Session.create(
        line_items=[{"price": price.id, "quantity": 1}],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
        customer=customer,
        expires_at=int(time.time() + (3600 // 2)),  # Configured to expire after 30 min
    )

    return checkout_session


def expire_session(checkout_session):
    # TODO
    if checkout_session.status == "expired":
        return "Expired session!"
    pass
