import datetime

daily_counter = {}


def generate_numeric_reference_id():
    today = datetime.datetime.now().strftime("%y%m%d")

    counter = daily_counter.get(today, 0) + 1
    daily_counter[today] = counter

    return f"{today}{counter: 05d}"
