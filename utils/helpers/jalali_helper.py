import jdatetime

_PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")


def to_persian_digits(value: str) -> str:
    return str(value or "").translate(_PERSIAN_DIGITS)


def get_persian_jalali_from_datetime(datetime, *, persian_digits: bool = True):
    if not datetime:
        return "-"
    text = jdatetime.datetime.fromgregorian(datetime=datetime).strftime(
        "%Y/%m/%d | %H:%M"
    )
    return to_persian_digits(text) if persian_digits else text
