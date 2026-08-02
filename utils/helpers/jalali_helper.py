import jdatetime


def get_persian_jalali_from_datetime(datetime):
    if not datetime:
        return "-"
    return jdatetime.datetime.fromgregorian(datetime=datetime).strftime(
        "%Y/%m/%d | %H:%M"
    )
