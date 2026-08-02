import random


def generate_otp():
    """Generate a 6-digit OTP."""
    return random.randint(1000, 9999)
