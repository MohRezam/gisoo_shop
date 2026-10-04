from django.db import transaction

from apps.cart.models import Cart, CartItem
from apps.cart.services.cart import _variant_units_in_cart


def _line_title(*, variant=None, bundle=None) -> str:
    if bundle is not None:
        title = getattr(bundle, "title", None) or ""
        if title:
            return title
        product = getattr(getattr(bundle, "variant", None), "product", None)
        return getattr(product, "title", None) or "باندل"
    if variant is not None:
        product = getattr(variant, "product", None)
        return getattr(product, "title", None) or "محصول"
    return "محصول"


def _adjustment(
    *,
    title: str,
    requested_quantity: int,
    final_quantity: int,
    variant_id=None,
    bundle_id=None,
) -> dict | None:
    if requested_quantity == final_quantity:
        return None
    return {
        "variant_id": variant_id,
        "bundle_id": bundle_id,
        "title": title,
        "requested_quantity": requested_quantity,
        "final_quantity": final_quantity,
        "reason": "insufficient_stock",
    }


class CartService:

    @staticmethod
    @transaction.atomic
    def merge_guest_cart(
        *,
        guest_cart,
        user,
    ):
        """
        Merge guest cart into the user's active cart.

        Returns:
            (cart, stock_adjustments)
        """
        adjustments: list[dict] = []

        user_cart = (
            Cart.objects
            .select_for_update()
            .filter(
                user=user,
                is_active=True,
            )
            .first()
        )

        # کاربر هنوز Cart ندارد — Guest Cart تبدیل به User Cart می‌شود.
        if user_cart is None:
            guest_cart.user = user
            guest_cart.save(
                update_fields=[
                    "user",
                ]
            )
            return guest_cart, adjustments

        if guest_cart.pk == user_cart.pk:
            return user_cart, adjustments

        guest_items = list(
            CartItem.objects
            .select_related(
                "variant",
                "variant__product",
                "bundle",
                "bundle__variant",
                "bundle__variant__product",
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
                variant = guest_item.variant
                title = _line_title(variant=variant)
                guest_qty = guest_item.quantity

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
                    requested = user_item.quantity + guest_qty
                    other_units = _variant_units_in_cart(
                        user_cart,
                        variant.id,
                        exclude_item_id=user_item.id,
                    )
                    available = max(
                        0,
                        variant.stock - other_units,
                    )
                    new_quantity = min(requested, available)

                    adj = _adjustment(
                        title=title,
                        requested_quantity=requested,
                        final_quantity=new_quantity,
                        variant_id=variant.id,
                    )
                    if adj:
                        adjustments.append(adj)

                    user_item.quantity = new_quantity
                    if user_item.quantity <= 0:
                        user_item.delete()
                    else:
                        user_item.save(
                            update_fields=[
                                "quantity",
                            ]
                        )
                else:
                    other_units = _variant_units_in_cart(
                        user_cart,
                        variant.id,
                    )
                    available = max(
                        0,
                        variant.stock - other_units,
                    )
                    new_quantity = min(guest_qty, available)

                    adj = _adjustment(
                        title=title,
                        requested_quantity=guest_qty,
                        final_quantity=new_quantity,
                        variant_id=variant.id,
                    )
                    if adj:
                        adjustments.append(adj)

                    if new_quantity <= 0:
                        guest_item.delete()
                        continue

                    guest_item.cart = user_cart
                    guest_item.quantity = new_quantity
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
                title = _line_title(bundle=bundle)
                guest_qty = guest_item.quantity

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
                    requested = user_item.quantity + guest_qty
                    other_units = _variant_units_in_cart(
                        user_cart,
                        variant.id,
                        exclude_item_id=user_item.id,
                    )
                    available_units = max(
                        0,
                        variant.stock - other_units,
                    )
                    max_bundle_quantity = (
                        available_units // bundle.quantity
                        if bundle.quantity
                        else 0
                    )
                    new_quantity = min(requested, max_bundle_quantity)

                    adj = _adjustment(
                        title=title,
                        requested_quantity=requested,
                        final_quantity=new_quantity,
                        bundle_id=bundle.id,
                        variant_id=variant.id,
                    )
                    if adj:
                        adjustments.append(adj)

                    user_item.quantity = new_quantity
                    if user_item.quantity <= 0:
                        user_item.delete()
                    else:
                        user_item.save(
                            update_fields=[
                                "quantity",
                            ]
                        )
                else:
                    other_units = _variant_units_in_cart(
                        user_cart,
                        variant.id,
                    )
                    available_units = max(
                        0,
                        variant.stock - other_units,
                    )
                    max_bundle_quantity = (
                        available_units // bundle.quantity
                        if bundle.quantity
                        else 0
                    )
                    new_quantity = min(guest_qty, max_bundle_quantity)

                    adj = _adjustment(
                        title=title,
                        requested_quantity=guest_qty,
                        final_quantity=new_quantity,
                        bundle_id=bundle.id,
                        variant_id=variant.id,
                    )
                    if adj:
                        adjustments.append(adj)

                    if new_quantity <= 0:
                        guest_item.delete()
                        continue

                    guest_item.cart = user_cart
                    guest_item.quantity = new_quantity
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

        guest_cart.delete()

        return user_cart, adjustments

    @staticmethod
    def merge_cart_after_login(
        *,
        cart_uuid,
        user,
    ):
        """
        Returns:
            (cart_or_None, stock_adjustments)
        """
        if not cart_uuid:
            return None, []

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
            return None, []

        return CartService.merge_guest_cart(
            guest_cart=guest_cart,
            user=user,
        )
