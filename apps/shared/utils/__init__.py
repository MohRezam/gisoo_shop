import logging
import time as timelib
from datetime import datetime, time, timedelta

from django.core.cache import caches
from django.core.exceptions import ValidationError

logger = logging.getLogger()


def day_range_for_date(date_str):
    date = convert_string_to_date(date_str)
    return (
        datetime.combine(date, time.min),
        datetime.combine(date, time.max),
    )


def day_range_for_date_with_yesterday_last_hours(date_str):
    date = convert_string_to_date(date_str)
    return (
        datetime.combine(date - timedelta(days=1), time(21, 0)),
        datetime.combine(date, time.max),
    )


def fixture_start_time_range(date):
    today_date = datetime.now().date()
    converted_date = convert_string_to_date(date).date()

    return (
        day_range_for_date_with_yesterday_last_hours(date)
        if datetime.now().hour < 12 and today_date == converted_date
        else day_range_for_date(date)
    )


def convert_string_to_date(date_str):
    try:
        date = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(f'Date "{date_str}" is not formatted as %Y-%m-%d .')
    return date


def time_until_end_of_day(dt):
    tomorrow = dt + timedelta(days=1)
    return (datetime.combine(tomorrow, time.min) - dt).seconds


def separate_by_comma(string: str):
    return string.split(",") if string else []


def get_ttl_hash(seconds=30):
    """Return the same value withing `seconds` time period"""
    return round(timelib.time() / seconds)


def get_cache(alias):
    """
    Retrieves existing configured cache backends
    """
    return caches[alias]
