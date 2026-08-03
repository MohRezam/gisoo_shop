from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.models import Payment
from apps.payments.serializers import (
    PaymentSerializer,
)
from apps.payments.services.gateway_callback import gateway_callback
from apps.payments.services.start_payment import (
    start_payment,
)


class PaymentDetailAPIView(
    RetrieveAPIView,
):
    serializer_class = PaymentSerializer

    permission_classes = [
        IsAuthenticated,
    ]

    lookup_url_kwarg = "payment_id"

    def get_queryset(self):
        return (
            Payment.objects
            .select_related(
                "order",
            )
            .filter(
                order__user=self.request.user,
            )
        )


class StartPaymentAPIView(
    APIView,
):
    permission_classes = [
        IsAuthenticated,
    ]

    def post(
            self,
            request,
            payment_id,
    ):
        payment = get_object_or_404(
            Payment.objects.select_related(
                "order",
            ),
            id=payment_id,
            order__user=request.user,
        )

        result = start_payment(
            payment=payment,
        )

        return Response(
            {
                "payment_id": result["payment"].id,
                "status": result["payment"].status,
                "redirect_url": result["redirect_url"],
            },
            status=status.HTTP_200_OK,
        )


class GatewayCallbackAPIView(
    APIView,
):
    permission_classes = [
        AllowAny,
    ]

    def get(
            self,
            request,
    ):
        authority = request.query_params.get(
            "Authority",
        )

        status_param = request.query_params.get(
            "Status",
        )

        if status_param != "OK":
            return Response(
                {
                    "success": False,
                    "message": "Payment canceled.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = gateway_callback(
            authority=authority,
        )

        return Response(
            {
                "success": True,
                "payment_id": payment.id,
                "order_id": payment.order.id,
            }
        )
