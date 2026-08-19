import uuid

from django.db import transaction

from apps.products.models import (
    Wishlist,
    WishlistItem,
)

from core_gisoo_backend.settings.components.constants import (
    WISHLIST_COOKIE_NAME,
)


class WishlistService:

    @staticmethod
    def get_or_create_guest_wishlist(
        token=None,
    ):
        if token:
            try:
                return (
                    Wishlist.objects.get(
                        guest_token=token,
                        user__isnull=True,
                    ),
                    False,
                )

            except Wishlist.DoesNotExist:
                pass

        wishlist = Wishlist.objects.create(
            guest_token=uuid.uuid4(),
        )

        return wishlist, True

    @staticmethod
    def get_or_create_user_wishlist(user):
        wishlist, created = (
            Wishlist.objects.get_or_create(
                user=user,
                defaults={
                    "guest_token": None,
                },
            )
        )

        return wishlist, created

    @staticmethod
    def get_wishlist(
        *,
        user=None,
        guest_token=None,
    ):
        if user and user.is_authenticated:
            return (
                WishlistService
                .get_or_create_user_wishlist(user)
            )

        return (
            WishlistService
            .get_or_create_guest_wishlist(
                guest_token
            )
        )

    @staticmethod
    @transaction.atomic
    def toggle_product(
        wishlist,
        product,
    ):
        item = (
            WishlistItem.objects
            .filter(
                wishlist=wishlist,
                product=product,
            )
            .first()
        )

        if item:
            item.delete()

            return {
                "is_favorited": False,
                "action": "removed",
            }

        WishlistItem.objects.create(
            wishlist=wishlist,
            product=product,
        )

        return {
            "is_favorited": True,
            "action": "added",
        }

    @staticmethod
    @transaction.atomic
    def merge_guest_wishlist(
        *,
        guest_wishlist,
        user,
    ):
        user_wishlist, _ = (
            WishlistService
            .get_or_create_user_wishlist(user)
        )

        if guest_wishlist.pk == user_wishlist.pk:
            return user_wishlist

        guest_product_ids = list(
            WishlistItem.objects
            .filter(
                wishlist=guest_wishlist,
            )
            .values_list(
                "product_id",
                flat=True,
            )
        )

        existing_product_ids = set(
            WishlistItem.objects
            .filter(
                wishlist=user_wishlist,
                product_id__in=guest_product_ids,
            )
            .values_list(
                "product_id",
                flat=True,
            )
        )

        new_product_ids = [
            product_id
            for product_id in guest_product_ids
            if product_id not in existing_product_ids
        ]

        WishlistItem.objects.bulk_create(
            [
                WishlistItem(
                    wishlist=user_wishlist,
                    product_id=product_id,
                )
                for product_id in new_product_ids
            ]
        )

        guest_wishlist.delete()

        return user_wishlist

    @staticmethod
    def merge_wishlist_after_login(
        *,
        request,
        user,
    ):
        guest_token = request.COOKIES.get(
            WISHLIST_COOKIE_NAME
        )

        if not guest_token:
            return

        guest_wishlist = (
            Wishlist.objects
            .filter(
                guest_token=guest_token,
                user__isnull=True,
            )
            .first()
        )

        if not guest_wishlist:
            return

        WishlistService.merge_guest_wishlist(
            guest_wishlist=guest_wishlist,
            user=user,
        )