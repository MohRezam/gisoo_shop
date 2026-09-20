from django.db import transaction

from apps.cart.models import Cart, CartItem


class CartService:

    @staticmethod
    @transaction.atomic
    def merge_guest_cart(
        *,
        guest_cart,
        user,
    ):
        user_cart = (
            Cart.objects
            .select_for_update()
            .filter(
                user=user,
                is_active=True,
            )
            .first()
        )

        # کاربر هنوز Cart ندارد
        # Guest Cart تبدیل به User Cart می‌شود.
        if user_cart is None:

            guest_cart.user = user

            guest_cart.save(
                update_fields=[
                    "user",
                ]
            )

            return guest_cart

        # اگر هر دو یکی باشند
        if guest_cart.pk == user_cart.pk:
            return user_cart

        guest_items = (
            CartItem.objects
            .select_related(
                "variant",
                "bundle",
                "bundle__variant",
            )
            .filter(
                cart=guest_cart,
            )
        )

        for guest_item in guest_items:

            # =================================
            # Variant
            # =================================

            if guest_item.variant_id:

                user_item = (
                    CartItem.objects
                    .filter(
                        cart=user_cart,
                        variant_id=guest_item.variant_id,
                        bundle__isnull=True,
                    )
                    .first()
                )

                if user_item:

                    new_quantity = (
                        user_item.quantity
                        + guest_item.quantity
                    )

                    stock = guest_item.variant.stock

                    user_item.quantity = min(
                        new_quantity,
                        stock,
                    )

                    if user_item.quantity <= 0:

                        user_item.delete()

                    else:

                        user_item.save(
                            update_fields=[
                                "quantity",
                            ]
                        )

                else:

                    stock = guest_item.variant.stock

                    if stock <= 0:

                        guest_item.delete()

                        continue

                    guest_item.cart = user_cart

                    guest_item.quantity = min(
                        guest_item.quantity,
                        stock,
                    )

                    guest_item.save(
                        update_fields=[
                            "cart",
                            "quantity",
                        ]
                    )

            # =================================
            # Bundle
            # =================================

            elif guest_item.bundle_id:

                bundle = guest_item.bundle
                variant = bundle.variant

                max_bundle_quantity = (
                    variant.stock // bundle.quantity
                )

                user_item = (
                    CartItem.objects
                    .filter(
                        cart=user_cart,
                        bundle_id=guest_item.bundle_id,
                        variant__isnull=True,
                    )
                    .first()
                )

                if user_item:

                    new_quantity = (
                        user_item.quantity
                        + guest_item.quantity
                    )

                    user_item.quantity = min(
                        new_quantity,
                        max_bundle_quantity,
                    )

                    if user_item.quantity <= 0:

                        user_item.delete()

                    else:

                        user_item.save(
                            update_fields=[
                                "quantity",
                            ]
                        )

                else:

                    if max_bundle_quantity <= 0:

                        guest_item.delete()

                        continue

                    guest_item.cart = user_cart

                    guest_item.quantity = min(
                        guest_item.quantity,
                        max_bundle_quantity,
                    )

                    guest_item.save(
                        update_fields=[
                            "cart",
                            "quantity",
                        ]
                    )

        # =================================
        # Discount
        # =================================

        if user_cart.discount_id is None:

            user_cart.discount = guest_cart.discount

            user_cart.save(
                update_fields=[
                    "discount",
                ]
            )

        # Guest Cart دیگر لازم نیست.
        guest_cart.delete()

        return user_cart

    @staticmethod
    def merge_cart_after_login(
        *,
        cart_uuid,
        user,
    ):
        if not cart_uuid:
            return None

        guest_cart = (
            Cart.objects
            .filter(
                uuid=cart_uuid,
                user__isnull=True,
                is_active=True,
            )
            .first()
        )

        if not guest_cart:
            return None

        return CartService.merge_guest_cart(
            guest_cart=guest_cart,
            user=user,
        )