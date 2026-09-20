from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import serializers, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import Order
from apps.payments.constants import PAYMENT_AMOUNT_UNIT_LABEL
from apps.payments.models import PaymentIntent
from apps.payments.serializers.payment_intent import (
    PaymentIntentSerializer,
    UploadReceiptSerializer,
)
from apps.payments.services.create_payment_intent import create_payment_intent
from apps.payments.services.upload_receipt import upload_payment_receipt
from apps.payments.cache import (
    get_cached_payment_intent_payload,
    set_cached_payment_intent_payload,
    invalidate_payment_intent_token_cache,
)


PAYMENT_INTENT_EXAMPLE = {
    "id": 12,
    "token": "xY9kLmN2pQ...",
    "status": "pending_payment",
    "payable_amount": 850000,
    "amount_unit": {"code": "toman", "label": "تومان"},
    "destination_card": "603799******1234",
    "bank_name": "بانک ملی",
    "holder_name": "گیسو سنتر",
    "expires_at": "2026-09-21T22:00:00+03:30",
    "order_id": 15,
    "can_upload_receipt": True,
    "public_number": "GS-260920-00015",
    "rejection_reason": "",
    "receipt_uploaded_at": None,
    "created_at": "2026-09-20T22:00:00+03:30",
}


@extend_schema(
    tags=["Payments — C2C"],
    summary="Create or resume payment intent",
    description=(
        "Creates a card-to-card (C2C) payment intent for an order.\n\n"
        f"All monetary fields are in **{PAYMENT_AMOUNT_UNIT_LABEL}**.\n\n"
        "**Resume / recreate rules:**\n"
        "- If an active intent exists (`pending_payment`, `receipt_submitted`, "
        "`under_review`, `manual_review`), it is returned (no duplicate).\n"
        "- If the latest intent is `rejected` or `expired`, a **new** intent is created "
        "and the order returns to `waiting_payment`.\n"
        "- If already `paid`, returns 400.\n\n"
        "Gateway redirect (`/payments/.../start`) is not used for the shop; "
        "only C2C + receipt upload."
    ),
    responses={
        201: OpenApiResponse(
            response=PaymentIntentSerializer,
            description="Payment intent created or resumed.",
            examples=[
                OpenApiExample("PaymentIntent", value=PAYMENT_INTENT_EXAMPLE),
            ],
        ),
        400: OpenApiResponse(description="Order not payable / already paid."),
        404: OpenApiResponse(description="Order not found."),
    },
)
class CreatePaymentIntentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        order = Order.objects.filter(id=order_id, user=request.user).first()
        if order is None:
            return Response(
                {"detail": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        intent, created = create_payment_intent(order=order, user=request.user)
        return Response(
            PaymentIntentSerializer(intent, context={"request": request}).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Payments — C2C"],
    summary="Get payment intent by token",
    description=(
        f"Public retrieve by opaque token. Amounts are in {PAYMENT_AMOUNT_UNIT_LABEL}."
    ),
    responses={
        200: PaymentIntentSerializer,
        404: OpenApiResponse(description="Intent not found."),
    },
)
class PaymentIntentByTokenAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, token):
        cached = get_cached_payment_intent_payload(token)
        if cached is not None:
            return Response(cached)

        intent = (
            PaymentIntent.objects.select_related("destination_card", "order")
            .filter(token=token)
            .first()
        )
        if intent is None:
            return Response(
                {"detail": "Payment intent not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        data = PaymentIntentSerializer(intent, context={"request": request}).data
        set_cached_payment_intent_payload(token, data)
        return Response(data)


@extend_schema(
    tags=["Payments — C2C"],
    summary="Upload payment receipt",
    description=(
        "Upload a bank-transfer receipt image (multipart).\n\n"
        "Send header `Idempotency-Key` to safely retry uploads.\n"
        "On success, status becomes `receipt_submitted` then `under_review`."
    ),
    request={
        "multipart/form-data": inline_serializer(
            name="UploadReceiptRequest",
            fields={"receipt": serializers.ImageField()},
        )
    },
    parameters=[
        OpenApiParameter(
            name="Idempotency-Key",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.HEADER,
            required=False,
            description="Optional idempotency key for receipt upload.",
        ),
    ],
    responses={
        200: PaymentIntentSerializer,
        400: OpenApiResponse(description="Invalid status or expired intent."),
        404: OpenApiResponse(description="Intent not found."),
    },
)
class UploadPaymentReceiptAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, intent_id):
        intent = (
            PaymentIntent.objects.select_related("destination_card", "order")
            .filter(id=intent_id, order__user=request.user)
            .first()
        )
        if intent is None:
            return Response(
                {"detail": "Payment intent not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = UploadReceiptSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        idempotency_key = request.headers.get("Idempotency-Key", "") or ""
        intent = upload_payment_receipt(
            intent=intent,
            receipt=serializer.validated_data["receipt"],
            idempotency_key=idempotency_key,
        )
        invalidate_payment_intent_token_cache(intent.token)
        return Response(
            PaymentIntentSerializer(intent, context={"request": request}).data
        )
