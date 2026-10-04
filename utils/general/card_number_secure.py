def normalize_card_number(card_number: str) -> str:
    """Keep digits only from a pasted/typed card number."""
    return "".join(ch for ch in (card_number or "") if ch.isdigit())


def format_display_pan(card_number: str) -> str | None:
    digits = normalize_card_number(card_number)
    if len(digits) != 16:
        return None
    return " ".join(digits[i : i + 4] for i in range(0, 16, 4))


def ltr_isolate(text: str) -> str:
    """
    Wrap text so RTL pages keep digit groups in left-to-right order.
    Prevents "6063 7313 0907 0499" from rendering as "0499 0907 7313 6063".
    """
    if not text:
        return text
    # U+2066 LEFT-TO-RIGHT ISOLATE … U+2069 POP DIRECTIONAL ISOLATE
    return f"\u2066{text}\u2069"


def secure_card_number(card_number: str):
    digits = normalize_card_number(card_number)
    if len(digits) != 16:
        return None
    new_card_number = "*" * 12 + digits[-4:]
    return " ".join(
        [
            new_card_number[quarter : quarter + 4]
            for quarter in range(0, len(new_card_number), 4)
        ]
    )
