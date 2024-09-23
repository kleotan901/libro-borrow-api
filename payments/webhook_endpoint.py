import stripe
from django.conf import settings
from stripe import WebhookEndpoint

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
HOME_DOMAIN = settings.HOME_DOMAIN


def webhook(*events) -> WebhookEndpoint:
    webhook_endpoint = stripe.WebhookEndpoint.create(
        enabled_events=[*events],
        url=settings.WEBHOOK_URL,
    )

    return webhook_endpoint


if __name__ == "__main__":
    webhook_object = webhook("checkout.session.expired", "checkout.session.completed")
    print("Webhook endpoint created:", webhook_object)
