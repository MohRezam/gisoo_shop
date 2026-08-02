from datetime import timedelta
from math import floor
import re


def truncate(number, digits=6):
    return floor(number * (10**6)) / (10**6)


UNITS = {"s": "seconds", "m": "minutes", "h": "hours", "d": "days", "w": "weeks"}


def convert_to_seconds(time_str, units: str = "smhdw"):
    """
    Convert readable time to seconds
    """
    timedelta_data = {}
    for match in re.finditer(
        r"(?P<value>\d+(\.\d+)?)(?P<unit>[smhdw]?)", time_str, flags=re.I
    ):
        unit = match.group("unit").lower()
        value = float(match.group("value"))
        if unit is None:
            unit = "s"
        if unit in units and unit in UNITS:
            timedelta_data[UNITS[unit]] = value
    return int(timedelta(**timedelta_data).total_seconds())


def translate_numbers(text: str):
    english_numbers = "0123456789"
    persian_numbers = "۰۱۲۳۴۵۶۷۸۹"
    translation_table = str.maketrans(english_numbers, persian_numbers)
    return text.translate(translation_table)
