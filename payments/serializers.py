from payments.models import Payment
from rest_framework import serializers


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "status",
            "payment_type",
        ]


class PaymentListSerializer(PaymentSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "amount",
            "status",
            "payment_type",
        ]


class PaymentDetailSerializer(PaymentSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "session_id",
            "session_url",
            "amount",
            "status",
            "payment_type",
            "borrowing",
        ]
