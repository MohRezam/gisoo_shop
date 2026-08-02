def convert_farsi_digits_to_english(value: str) -> str:
    farsi_to_english = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    return value.translate(farsi_to_english)
