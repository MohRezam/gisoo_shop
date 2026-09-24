from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.notifications.models import InAppNotification
from apps.notifications.serializers.inbox import InAppNotificationSerializer
from apps.notifications.cache import (
    get_cached_unread_count,
    set_cached_unread_count,
    invalidate_unread_count,
)
from utils.paginators import StandardResultPagination


NOTIFICATION_EXAMPLE = {
    "id": 1,
    "title": "سفارش ثبت شد",
    "body": "سفارش GS-260920-00015 با موفقیت ثبت شد.",
    "type": "order",
    "link": "/account/orders/15",
    "order_id": 15,
    "is_read": False,
    "created_at": "2026-09-20T22:10:00+03:30",
}


@extend_schema(
    tags=["Notifications — Inbox"],
    summary="List in-app notifications",
    description="Paginated inbox for the authenticated user. OTP endpoints are unchanged.",
    responses={200: InAppNotificationSerializer(many=True)},
)
class InAppNotificationListAPIView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InAppNotificationSerializer
    pagination_class = StandardResultPagination

    def get_queryset(self):
        qs = InAppNotification.objects.filter(user=self.request.user)
        is_read = self.request.query_params.get("is_read")
        if is_read is not None:
            normalized = str(is_read).strip().lower()
            if normalized in ("1", "true", "yes"):
                qs = qs.filter(is_read=True)
            elif normalized in ("0", "false", "no"):
                qs = qs.filter(is_read=False)
        return qs


@extend_schema(
    tags=["Notifications — Inbox"],
    summary="Unread notification count",
    responses={
        200: OpenApiResponse(
            description="Badge count",
            examples=[OpenApiExample("Count", value={"count": 3})],
        )
    },
)
class UnreadNotificationCountAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cached = get_cached_unread_count(request.user.id)
        if cached is not None:
            return Response({"count": cached})

        count = InAppNotification.objects.filter(
            user=request.user,
            is_read=False,
        ).count()
        set_cached_unread_count(request.user.id, count)
        return Response({"count": count})


@extend_schema(
    tags=["Notifications — Inbox"],
    summary="Mark one notification as read",
    responses={
        200: InAppNotificationSerializer,
        404: OpenApiResponse(description="Not found"),
    },
)
class MarkNotificationReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        notif = InAppNotification.objects.filter(user=request.user, pk=pk).first()
        if notif is None:
            return Response(
                {"detail": "Notification not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not notif.is_read:
            notif.is_read = True
            notif.save(update_fields=["is_read", "updated_at"])
            invalidate_unread_count(request.user.id)
        return Response(InAppNotificationSerializer(notif).data)


@extend_schema(
    tags=["Notifications — Inbox"],
    summary="Mark all notifications as read",
    responses={
        200: OpenApiResponse(
            examples=[OpenApiExample("OK", value={"updated": 5})],
        )
    },
)
class MarkAllNotificationsReadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        updated = InAppNotification.objects.filter(
            user=request.user,
            is_read=False,
        ).update(is_read=True)
        invalidate_unread_count(request.user.id)
        return Response({"updated": updated})
