from rest_framework import permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.payments.models import PaymentIntentStatus, PaymentIntent
from apps.payments.serializers import (
    PaymentIntentSerializer,
    PaymentReceiptSerializer,
)
from apps.payments.services.create_payment_intent import (
    create_payment_intent,
)
from apps.payments.services.submit_receipt import (
    submit_receipt,
)
from django.utils import timezone


from rest_framework_simplejwt.authentication import JWTAuthentication


class PaymentReceiptSubmitAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, id):
        idempotency_key = request.headers.get("Idempotency-Key")
        receipt_file = request.FILES.get("file")

        result = submit_receipt(
            payment_intent_id=id,
            user=request.user,
            uploaded_file=receipt_file,
            idempotency_key=idempotency_key,
        )

        receipt = result["receipt"]

        response_status = (
            status.HTTP_200_OK
            if result["idempotent_replay"]
            else status.HTTP_201_CREATED
        )

        return Response(
            {
                "receipt": PaymentReceiptSerializer(
                    receipt,
                    context={"request": request},
                ).data,
                "duplicate": result["duplicate"],
                "idempotent_replay": result["idempotent_replay"],
            },
            status=response_status,
        )


class PaymentIntentCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        payment_intent = create_payment_intent(
            order_id=id,
            user=request.user,
        )

        return Response(
            PaymentIntentSerializer(
                payment_intent,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )


class PaymentIntentDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, token):
        payment_intent = (
            PaymentIntent.objects
            .select_related(
                "order",
                "destination_card",
            )
            .filter(
                token=token,
                order__user=request.user,
            )
            .first()
        )

        if payment_intent is None:
            return Response(
                {
                    "detail": "Payment intent not found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
                payment_intent.status
                in {
            PaymentIntentStatus.PENDING_PAYMENT,
            PaymentIntentStatus.REJECTED,
        }
                and payment_intent.expires_at <= timezone.now()
        ):
            payment_intent.status = PaymentIntentStatus.EXPIRED
            payment_intent.save(
                update_fields=["status"]
            )

        return Response(
            PaymentIntentSerializer(
                payment_intent,
                context={"request": request},
            ).data
        )
