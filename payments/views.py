import stripe
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from payments.models import Payment
from payments.serializers import (
    PaymentListSerializer,
    PaymentSerializer,
    PaymentDetailSerializer,
)


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    serializer_class = PaymentSerializer
    queryset = Payment.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PaymentDetailSerializer
        if self.action == "list":
            return PaymentListSerializer
        return PaymentSerializer

    def get_queryset(self):
        queryset = self.queryset
        if not self.request.user.is_staff:
            queryset = queryset.filter(borrowing__user_id=self.request.user)
        return queryset

    @action(methods=["get"], detail=True, url_path="success")
    def get_success_payment(self, request, pk):
        # Get success session
        session = stripe.checkout.Session.retrieve(
            request.query_params.get("session_id")
        )
        customer = stripe.Customer.retrieve(session.customer)

        payment = Payment.objects.get(session_id=session.id)

        # if payment was success -> status changed to "PAID"
        payment.status = "PAID"
        payment.save()

        # if borrowing overdue -> payment_type change  to "FINE"
        if payment.borrowing.actual_return_date:
            if (
                payment.borrowing.actual_return_date
                > payment.borrowing.expected_return_date
            ):
                payment.payment_type = "FINE"
                payment.save()

        return Response(
            {"message": f"Thank you for payment, {customer.name}!"},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get"], url_path="cancel")
    def cancel(self, request, pk=None):
        return Response(
            {
                "message": "Payment cancelled. Payment can be paid a bit later (but the session is available for only 24h)"
            },
            status=status.HTTP_204_NO_CONTENT,
        )


# Using Django
@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META["STRIPE_SIGNATURE"]
    event = None
    endpoint_secret = "whsec_HJr55ugRXW5v3cvLXKL47z04glw0eyWF"

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except ValueError as e:
        # Invalid payload
        print("Error parsing payload: {}".format(str(e)))
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        print("Error verifying webhook signature: {}".format(str(e)))
        return HttpResponse(status=400)

    # Handle the event
    if event.type == "payment_intent.succeeded":
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        print("PaymentIntent was successful!")
    elif event.type == "payment_method.attached":
        payment_method = event.data.object  # contains a stripe.PaymentMethod
        print("PaymentMethod was attached to a Customer!")
    # ... handle other event types
    else:
        print("Unhandled event type {}".format(event.type))

    return HttpResponse(status=200)
