"""
Prediction
"""

from decouple import config

KAFKA_HOST = config("KAFKA_HOST", default=None)
KAFKA_FOOTBALL_TOPIC = config("KAFKA_FOOTBALL_TOPIC", default=None)
KAFKA_VOLLEYBALL_TOPIC = config("KAFKA_VOLLEYBALL_TOPIC", default=None)
KAFKA_SEND_TIMEOUT = int(config("KAFKA_SEND_TIMEOUT", default="10"))
