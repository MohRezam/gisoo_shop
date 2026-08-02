def secure_card_number(card_number: str):
    if not card_number or len(card_number) != 16:
        return None
    new_card_number = "*" * 12 + card_number[-4:]
    return " ".join(
        [
            new_card_number[quarter : quarter + 4]
            for quarter in range(0, len(new_card_number), 4)
        ]
    )
