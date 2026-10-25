def format_sheba_display(value: str) -> str:
    compact = (value or "").replace(" ", "").upper()
    if not compact:
        return ""
    return " ".join(compact[i:i + 4] for i in range(0, len(compact), 4))


def visible_sheba(*, card, order_total_toman: int) -> str:
    """
    Sheba is shown only when a number is saved and the order
    total reaches the admin threshold. Threshold 0 keeps the
    current card-only payment page.
    """

    raw = (getattr(card, "sheba_number", "") or "").replace(" ", "").upper()
    threshold = getattr(card, "sheba_min_amount", 0) or 0
    if not raw or threshold <= 0 or order_total_toman < threshold:
        return ""
    return format_sheba_display(raw)
