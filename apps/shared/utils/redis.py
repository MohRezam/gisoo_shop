import redis
from django.conf import settings
from decouple import config

redis_client = redis.Redis.from_url(
    config("REDIS_URL"),
    decode_responses=True,
)
