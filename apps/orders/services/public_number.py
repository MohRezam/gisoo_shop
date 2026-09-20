from django.utils import timezone


def generate_order_public_number(order_id: int) -> str:
    stamp = timezone.now().strftime("%y%m%d")
    return f"GS-{stamp}-{order_id:05d}"
