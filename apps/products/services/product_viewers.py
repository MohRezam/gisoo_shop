import random
import time
import uuid

from django.core.cache import caches

VIEWER_TTL = 30
VIEWER_COOKIE_NAME = "product_viewer_id"
DISPLAY_VIEWERS_KEY_PREFIX = "product:display_viewers"

redis_cache = caches["redis"]


def get_viewer_id(request):
    viewer_id = request.COOKIES.get(VIEWER_COOKIE_NAME)

    if not viewer_id:
        viewer_id = str(uuid.uuid4())

    if request.user.is_authenticated:
        return f"user:{request.user.id}"

    return f"guest:{viewer_id}"


def get_viewers_key(product_id):
    return f"product:viewers:{product_id}"


def get_display_viewers_key(product_id):
    return f"{DISPLAY_VIEWERS_KEY_PREFIX}:{product_id}"


def get_display_viewers_count(client, product_id, actual_viewers):
    key = get_display_viewers_key(product_id)

    # If there are more than 5 real viewers,
    # show the real number.
    if actual_viewers > 5:
        client.set(key, actual_viewers)
        return actual_viewers

    previous_count = client.get(key)

    if previous_count is None:
        if actual_viewers == 0:
            display_count = random.randint(1, 10)
        else:
            display_count = random.randint(5, 20)

        client.set(key, display_count)
        return display_count

    previous_count = int(previous_count)

    if actual_viewers == 0:
        min_count = 1
        max_count = 10
    else:
        min_count = 5
        max_count = 20

    possible_counts = range(
        max(min_count, previous_count - 2),
        min(max_count, previous_count + 2) + 1,
    )

    display_count = random.choice(
        list(possible_counts)
    )

    client.set(key, display_count)

    return display_count


def register_viewer(request, product_id):
    viewer_id = get_viewer_id(request)
    key = get_viewers_key(product_id)

    now = time.time()
    expired_before = now - VIEWER_TTL

    client = redis_cache.client.get_client(write=True)

    # Remove inactive viewers.
    client.zremrangebyscore(
        key,
        0,
        expired_before,
    )

    # Update this viewer's last activity.
    client.zadd(
        key,
        {
            viewer_id: now,
        }
    )

    # Keep Redis key alive.
    client.expire(
        key,
        VIEWER_TTL,
    )

    actual_viewers = client.zcard(key)

    display_viewers = get_display_viewers_count(
        client=client,
        product_id=product_id,
        actual_viewers=actual_viewers,
    )

    return display_viewers, viewer_id
