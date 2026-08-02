import re


def check_pattern_for_round(str):
    """
    Checks to see if the string contains `round`
    """
    pattern = r"(?i)\bround\b"
    if re.search(pattern, str):
        return True
    else:
        return False
